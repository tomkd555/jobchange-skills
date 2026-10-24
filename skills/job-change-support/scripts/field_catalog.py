"""項目の辞書（references/field-catalog.md）を読み込むモジュール。

辞書の原本は Markdown の表 1 か所だけである。wishes.json、posting-check.json、matches、
decisions の各検証スクリプトは、このモジュールを通して field_id・型・単位・向き・列挙値を参照する。
定数のコピーを持たないため、表を直せば全部の検証に反映される。

使い方:
    from field_catalog import load_catalog
    catalog = load_catalog()
    field = catalog.fields["salary_min"]
    error = field.check_value(6000000, catalog)  # None なら型が合う
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import date
from typing import Any

_HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CATALOG_PATH = os.path.join(os.path.dirname(_HERE), "references", "field-catalog.md")

_CODE_RE = re.compile(r"`([^`]*)`")
_DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
_AS_OF_RE = re.compile(r"^[0-9]{4}(-[0-9]{2}(-[0-9]{2})?)?$")

# 「### Job posting fields」のような見出しと、その表の section 名の対応。
_SECTION_HEADINGS = {
    "### Job posting fields": "posting",
    "### Company fields": "company",
    "### User fields": "user",
}

# 辞書の表には列挙名で書くが、値の形の grade と decisions の direction などは enum 表で持つ。
FIELD_TYPES = ("integer", "number", "string", "boolean", "date", "string_list")


@dataclass(frozen=True)
class Field:
    field_id: str
    label: str
    type: str  # FIELD_TYPES のいずれか、または "enum:<name>"
    unit: str | None
    direction: str  # higher / lower / none
    sources: tuple[str, ...]
    section: str  # posting / company / user

    @property
    def enum_name(self) -> str | None:
        return self.type[5:] if self.type.startswith("enum:") else None

    def check_value(self, value: Any, catalog: "Catalog") -> str | None:
        """値が型に合えば None、合わなければ日本語のメッセージを返す。null は常に許す。"""
        if value is None:
            return None
        t = self.type
        if t == "integer":
            if isinstance(value, bool) or not isinstance(value, int):
                return f"{self.field_id} は整数で書く"
        elif t == "number":
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return f"{self.field_id} は数値で書く"
        elif t == "string":
            if not isinstance(value, str) or not value.strip():
                return f"{self.field_id} は空でない文字列で書く"
        elif t == "boolean":
            if not isinstance(value, bool):
                return f"{self.field_id} は真偽値で書く"
        elif t == "date":
            if not is_date(value):
                return f"{self.field_id} は YYYY-MM-DD の実在する日付で書く"
        elif t == "string_list":
            if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value):
                return f"{self.field_id} は空でない文字列の配列で書く"
        elif t.startswith("enum:"):
            allowed = catalog.enums.get(t[5:], {})
            if not isinstance(value, str) or value not in allowed:
                return f"{self.field_id} は {', '.join(allowed)} のいずれかで書く"
        else:
            return f"{self.field_id} の型 {t} は辞書が知らない型である"
        return None


@dataclass
class Catalog:
    fields: dict[str, Field] = field(default_factory=dict)
    enums: dict[str, dict[str, str]] = field(default_factory=dict)
    path: str = DEFAULT_CATALOG_PATH

    def field_ids(self, section: str | None = None) -> tuple[str, ...]:
        return tuple(f.field_id for f in self.fields.values() if section is None or f.section == section)

    def enum_values(self, name: str) -> tuple[str, ...]:
        return tuple(self.enums.get(name, {}))


def is_date(value: Any) -> bool:
    """YYYY-MM-DD の実在する日付か。"""
    if not isinstance(value, str) or not _DATE_RE.match(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def is_as_of(value: Any) -> bool:
    """基準時点 YYYY / YYYY-MM / YYYY-MM-DD か。"""
    if not isinstance(value, str) or not _AS_OF_RE.match(value):
        return False
    if len(value) == 10:
        return is_date(value)
    if len(value) == 7:
        return 1 <= int(value[5:7]) <= 12
    return True


def _split_row(line: str) -> list[str]:
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


def _code(cell: str) -> str | None:
    m = _CODE_RE.search(cell)
    return m.group(1) if m else None


def load_catalog(path: str | None = None) -> Catalog:
    """field-catalog.md を読み、Catalog を返す。表の構造が崩れていれば ValueError を投げる。"""
    path = path or DEFAULT_CATALOG_PATH
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    catalog = Catalog(path=path)
    section: str | None = None
    enum_name: str | None = None
    in_enums = False
    header: list[str] | None = None

    for line in lines:
        if line.startswith("## "):
            in_enums = line.strip() == "## Enumerations"
            section = None
            enum_name = None
            header = None
            continue
        if line.startswith("### "):
            header = None
            if in_enums:
                enum_name = line[4:].strip()
                catalog.enums.setdefault(enum_name, {})
                section = None
            else:
                section = next((s for h, s in _SECTION_HEADINGS.items() if line.startswith(h)), None)
                enum_name = None
            continue
        if not line.startswith("|"):
            header = None
            continue
        cells = _split_row(line)
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue  # 区切り行
        if header is None:
            header = cells
            continue
        if section is not None:
            if len(cells) < 6:
                raise ValueError(f"{path}: 項目の表の列が足りない: {line}")
            field_id = _code(cells[0])
            if not field_id:
                raise ValueError(f"{path}: field_id がバックティック囲みでない: {line}")
            if field_id in catalog.fields:
                raise ValueError(f"{path}: field_id が重複している: {field_id}")
            unit = cells[3] or None
            sources = tuple(s.strip() for s in cells[5].split(",") if s.strip())
            catalog.fields[field_id] = Field(
                field_id=field_id,
                label=cells[1],
                type=cells[2],
                unit=unit,
                direction=cells[4],
                sources=sources,
                section=section,
            )
        elif enum_name is not None:
            if len(cells) < 2:
                raise ValueError(f"{path}: 列挙の表の列が足りない: {line}")
            value = _code(cells[0])
            if value is None:
                raise ValueError(f"{path}: 列挙値がバックティック囲みでない: {line}")
            catalog.enums[enum_name][value] = cells[1]

    if not catalog.fields:
        raise ValueError(f"{path}: 項目の表が見つからない")
    for f_ in catalog.fields.values():
        if f_.type not in FIELD_TYPES and not (f_.type.startswith("enum:") and f_.type[5:] in catalog.enums):
            raise ValueError(f"{path}: {f_.field_id} の型 {f_.type} が定義されていない")
        if f_.direction not in catalog.enums.get("direction", {}):
            raise ValueError(f"{path}: {f_.field_id} の向き {f_.direction} が direction の表にない")
    return catalog


VALUE_KEYS = ("value", "unit", "source_url", "grade", "as_of")


def check_value_object(
    field_: Field, obj: Any, catalog: Catalog, *, allow_user_source: bool = False
) -> list[str]:
    """辞書の値の形 {value, unit, source_url, grade, as_of, quote} を検査し、不備のメッセージを返す。"""
    errors: list[str] = []
    if not isinstance(obj, dict):
        return [f"{field_.field_id} の値はオブジェクトで書く"]
    for key in VALUE_KEYS:
        if key not in obj:
            errors.append(f"{field_.field_id} の値に {key} が無い")
    if errors:
        return errors
    value = obj["value"]
    type_error = field_.check_value(value, catalog)
    if type_error:
        errors.append(type_error)
    if obj["unit"] != field_.unit:
        errors.append(f"{field_.field_id} の unit は {field_.unit!r} で書く（{obj['unit']!r} になっている）")
    if value is not None:
        url = obj["source_url"]
        if not allow_user_source and not (isinstance(url, str) and url.startswith("http")):
            errors.append(f"{field_.field_id} の source_url は http で始まる URL で書く")
        if obj["grade"] not in catalog.enums.get("grade", {}):
            errors.append(f"{field_.field_id} の grade は A〜D で書く")
        if not is_as_of(obj["as_of"]):
            errors.append(f"{field_.field_id} の as_of は YYYY / YYYY-MM / YYYY-MM-DD で書く")
    if "quote" in obj and obj["quote"] is not None and not isinstance(obj["quote"], str):
        errors.append(f"{field_.field_id} の quote は文字列か null で書く")
    return errors
