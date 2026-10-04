"""jc_config.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_jc_config
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import jc_config as jc  # noqa: E402


class TempTreeTestCase(unittest.TestCase):
    """一時ディレクトリを home・作業ディレクトリとして使う共通の土台。"""

    def setUp(self) -> None:
        # 設定ディレクトリ名をテスト専用の名前へ差し替える。Windows では一時ディレクトリが
        # ホームディレクトリの配下にあるため、上位ディレクトリ探索が実在の
        # ~/.job-change/config.json に当たってしまう。
        patcher = mock.patch.object(jc, "CONFIG_DIRNAME", ".job-change-test")
        patcher.start()
        self.addCleanup(patcher.stop)

        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.data_root = self.root / "data"
        self.data_root.mkdir()
        self.cwd = self.root / "work" / "nested"
        self.cwd.mkdir(parents=True)

    def write_config(self, directory: Path, **overrides: object) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        payload = {"schema_version": "1.0", "data_root": str(self.data_root)}
        payload.update(overrides)
        path = directory / "config.json"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return path


class FindConfigPathTest(TempTreeTestCase):
    def test_search_order(self) -> None:
        places = {
            "env": self.root / "explicit",
            "outer": self.root / "work" / jc.CONFIG_DIRNAME,
            "nearest": self.cwd / jc.CONFIG_DIRNAME,
            "home": self.home / jc.CONFIG_DIRNAME,
        }
        # (ラベル, 存在する場所, 環境変数が指す先, 期待する場所, 期待する由来)
        rows = [
            ("環境変数が最優先", {"env", "nearest", "home"}, "env", "env", "env"),
            ("環境変数の指す先が無ければ無視", {"home"}, "missing", "home", "home"),
            ("上位ディレクトリの設定が home に勝つ", {"outer", "home"}, None, "outer", "project"),
            ("最も近い設定が外側に勝つ", {"outer", "nearest"}, None, "nearest", "project"),
            ("home は最後の手段", {"home"}, None, "home", "home"),
            ("どこにも無い", set(), None, None, ""),
        ]
        for label, present, env_target, expected_place, expected_source in rows:
            with self.subTest(label):
                written = {name: self.write_config(places[name]) for name in present}
                env = {}
                if env_target == "env":
                    env = {jc.ENV_VAR: str(written["env"])}
                elif env_target == "missing":
                    env = {jc.ENV_VAR: str(self.root / "nope.json")}
                found, source = jc.find_config_path(env=env, start_dir=self.cwd, home=self.home)
                self.assertEqual(found, written[expected_place] if expected_place else None)
                self.assertEqual(source, expected_source)
                for directory in places.values():
                    shutil.rmtree(directory, ignore_errors=True)


class LoadConfigTest(TempTreeTestCase):
    def test_defaults_and_overrides(self) -> None:
        config = jc.load_config(self.write_config(self.home / jc.CONFIG_DIRNAME))
        self.assertEqual(
            (config["private_dir"], config["companies_dir"], config["job_search_dir"], config["python"]),
            ("career-private", "companies", "job-search", "python"),
        )
        config = jc.load_config(
            self.write_config(self.home / jc.CONFIG_DIRNAME, python="python3", companies_dir="corp")
        )
        self.assertEqual((config["python"], config["companies_dir"]), ("python3", "corp"))

    def test_invalid_config_is_an_error(self) -> None:
        directory = self.home / jc.CONFIG_DIRNAME
        raw = directory / "raw.json"
        directory.mkdir(parents=True)
        raw.write_text("{ not json", encoding="utf-8")
        no_root = directory / "no_root.json"
        no_root.write_text(json.dumps({"schema_version": "1.0"}), encoding="utf-8")
        rows = [
            ("JSON が壊れている", raw),
            ("data_root が無い", no_root),
            ("data_root が相対パス", self.write_config(directory / "a", data_root="relative-dir")),
            ("ディレクトリ名に区切り文字", self.write_config(directory / "b", private_dir="../outside")),
            ("存在しないファイル", directory / "nothing.json"),
        ]
        for label, path in rows:
            with self.subTest(label), self.assertRaises(jc.ConfigError):
                jc.load_config(path)

    def test_tilde_in_data_root_is_expanded(self) -> None:
        path = self.write_config(self.home / jc.CONFIG_DIRNAME, data_root="~/job-change-data")
        config = jc.load_config(path, home=self.home)
        self.assertEqual(config["data_root"], str(self.home / "job-change-data"))


class ResolveTest(TempTreeTestCase):
    def test_paths_follow_directory_settings(self) -> None:
        config = jc.load_config(
            self.write_config(self.home / jc.CONFIG_DIRNAME, private_dir="secret", companies_dir="corp")
        )
        paths = jc.resolve_paths(config)
        private = self.data_root / "secret"
        self.assertEqual(Path(paths["private"]), private)
        self.assertEqual(Path(paths["companies"]), self.data_root / "corp")
        self.assertEqual(Path(paths["job_search"]), self.data_root / "job-search")
        for key, filename in jc.PRIVATE_FILES.items():
            self.assertEqual(Path(paths[key]), private / filename)
        self.assertFalse(private.exists())


class InitConfigTest(TempTreeTestCase):
    def test_creates_loadable_config_under_home(self) -> None:
        path = jc.init_config(str(self.data_root), home=self.home)
        self.assertEqual(path, self.home / jc.CONFIG_DIRNAME / "config.json")
        self.assertEqual(jc.load_config(path)["data_root"], str(self.data_root))

    def test_existing_config_is_kept(self) -> None:
        existing = self.write_config(self.home / jc.CONFIG_DIRNAME, data_root=str(self.root / "old"))
        before = existing.read_text(encoding="utf-8")
        with self.assertRaises(jc.ConfigError):
            jc.init_config(str(self.data_root), home=self.home)
        self.assertEqual(existing.read_text(encoding="utf-8"), before)

    def test_relative_data_root_is_rejected(self) -> None:
        with self.assertRaises(jc.ConfigError):
            jc.init_config("relative-dir", home=self.home)


class MainTest(TempTreeTestCase):
    def _run(self, argv: list[str], env: dict | None = None) -> tuple[int, str]:
        buffer = StringIO()
        code = jc.main(argv, env=env or {}, start_dir=self.cwd, home=self.home, stream=buffer)
        return code, buffer.getvalue()

    def test_show_exit_codes(self) -> None:
        # (ラベル, 設定の作り方, 期待する終了コード, 期待する status)
        rows = [
            ("未設定", lambda: None, 2, "unconfigured"),
            ("正常", lambda: self.write_config(self.home / jc.CONFIG_DIRNAME), 0, "ok"),
            ("内容が不正", lambda: self.write_config(self.home / jc.CONFIG_DIRNAME, data_root="relative"), 1, "invalid"),
        ]
        for label, setup, code_expected, status in rows:
            with self.subTest(label):
                setup()
                code, output = self._run(["--show"])
                self.assertEqual(code, code_expected)
                self.assertEqual(json.loads(output)["status"], status)
                shutil.rmtree(self.home / jc.CONFIG_DIRNAME, ignore_errors=True)

    def test_show_output_keys_and_env_source(self) -> None:
        env_config = self.write_config(self.root / "explicit")
        code, output = self._run(["--show"], env={jc.ENV_VAR: str(env_config)})
        payload = json.loads(output)
        self.assertEqual(code, 0)
        self.assertEqual(payload["source"], "env")
        self.assertEqual(
            sorted(payload),
            ["config_path", "data_root", "paths", "python", "source", "status"],
        )

    def test_init_exit_codes(self) -> None:
        code, output = self._run(["--init", "--data-root", str(self.data_root)])
        self.assertEqual((code, json.loads(output)["status"]), (0, "created"))
        code, output = self._run(["--init", "--data-root", str(self.data_root)])
        self.assertEqual((code, json.loads(output)["status"]), (1, "exists"))

    def test_path_prints_one_path_or_reports_unconfigured(self) -> None:
        code, _ = self._run(["--path", "profile"])
        self.assertEqual(code, 2)
        self.write_config(self.home / jc.CONFIG_DIRNAME)
        code, output = self._run(["--path", "profile"])
        self.assertEqual(code, 0)
        self.assertEqual(output.strip(), str(self.data_root / "career-private" / "profile.json"))


if __name__ == "__main__":
    unittest.main()
