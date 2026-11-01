#!/usr/bin/env python3
"""fetch_page.py - fetch a source page and cache its text.

The default fetch path for the research-team collectors, used in place of WebFetch.
WebFetch returns a small model's answer to a prompt, so it cannot guarantee the wording of
the original. This script stores the extracted page text as it is; the collection agent then
greps the cache for the passage it needs and copies the quote out of it. The text
goes through the same extraction and normalisation as citation_verifier.py, so check.py's
quote check matches by construction, with no reliance on the agent following an instruction.

PDFs are cached through pypdf when it is installed. Pages whose text cannot be taken
(JavaScript-rendered, paywalled, a PDF without pypdf, an image or other binary type) come
back with a status and no file; fall back to WebFetch for those (research-collector.md).

Output: {RUN_DIR}/pages/{first 16 hex of the URL's SHA1}.txt and {RUN_DIR}/pages/index.json
The body is wrapped at about 200 characters. The wrapping belongs to the cache alone; the
original text keeps its own line breaks.

Examples:
    python fetch_page.py --run-dir research/20260816-topic https://example.com/a https://example.com/b
    python fetch_page.py --run-dir . https://example.com/a --json

Exit codes: 0 = every URL is in the cache (including cached) / 1 = some URL could not be
fetched / 2 = usage or I/O error
"""

import argparse
import concurrent.futures
import datetime
import io
import json
import os
import pathlib
import sys
import tempfile
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
import zlib

from citation_verifier import (DEFAULT_TIMEOUT, HostThrottle, _configure_stdout, cache_name,
                               decode_body, html_to_text, http_fetch, normalize_text)

WRAP_WIDTH = 200        # target line length; one grep hit is one line of reading
MIN_CHARS = 400         # below this, the body was not really fetched (JS-rendered, paywalled)
DEFAULT_WORKERS = 4
BREAK_CHARS = (" ", ".", ",", ";", "。", "、", "）", "」")
NUMBER_CHARS = frozenset("0123456789.,%")
PLAIN_TYPES = {"text/plain", "text/csv", "application/json"}

TEXT_EXTS = {".txt", ".md", ".csv", ".json", ".log"}
MARKUP_EXTS = {".html", ".htm", ".xml"}
DOCX_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _inside_number(s, p):
    """True when a cut before s[p] would fall between two characters of a number."""
    return 0 < p < len(s) and s[p - 1] in NUMBER_CHARS and s[p] in NUMBER_CHARS


def wrap_text(s, width=WRAP_WIDTH):
    """Wrap the body at about `width`, breaking after a break character where there is one.

    A cut never falls inside a number such as 1,200.5 or 26.5%, so a grep for the figure
    finds it on one line.
    """
    lines = []
    i, n = 0, len(s)
    while i < n:
        if n - i <= width:
            lines.append(s[i:])
            break
        cut = next((j + 1 for j in range(width - 1, width // 2 - 1, -1)
                    if s[i + j] in BREAK_CHARS and not _inside_number(s, i + j + 1)), None)
        if cut is None:
            cut = width
            while _inside_number(s, i + cut):
                cut += 1  # move the cut to the end of the number run
        lines.append(s[i:i + cut])
        i += cut
    return "\n".join(lines)


def pdf_text(source):
    """Extract text from a PDF's text layer. `source` is a path or a file-like object.

    Returns (text, missing_detail); missing_detail is set only when pypdf itself cannot be
    imported. A PDF that imports but fails to parse (corrupt, image-only) comes back as an
    empty string, which the caller's min_chars check then reports as "thin".
    # ponytail: pypdf text layer only; PyMuPDF if column/table layout matters
    """
    try:
        import pypdf
    except ImportError:
        return "", "PDF text extraction needs pypdf (pip install pypdf)"
    try:
        reader = pypdf.PdfReader(source)
        text = "".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        text = ""
    return text, None


def docx_text(path):
    """Extract text from a .docx via word/document.xml (stdlib zipfile + ElementTree).

    Every w:t text node is joined within its w:p paragraph, and paragraphs are joined with
    line breaks, so a Grep for a sentence still finds it on one cache line after wrap_text.
    """
    with zipfile.ZipFile(path) as zf:
        xml_bytes = zf.read("word/document.xml")
    root = ET.fromstring(xml_bytes)
    paragraphs = []
    for p in root.iter(DOCX_NS + "p"):
        paragraphs.append("".join(t.text or "" for t in p.iter(DOCX_NS + "t")))
    return "\n".join(paragraphs)


def extract_local_text(path):
    """Extract text from a local file by extension.

    Returns (text, status, detail); status is None on a supported extension (even one
    that extracts to nothing) and "unsupported" otherwise.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in TEXT_EXTS:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read(), None, None
    if ext in MARKUP_EXTS:
        with open(path, "rb") as f:
            raw = f.read()
        return html_to_text(raw, None), None, None
    if ext == ".docx":
        return docx_text(path), None, None
    if ext == ".pdf":
        text, missing = pdf_text(path)
        if missing:
            return "", "unsupported", missing
        return text, None, None
    return "", "unsupported", f"unsupported file type: {ext or '(no extension)'}"


def canonical_file_url(p):
    """The canonical file:// URL for a local path: both the cache key and the recorded
    source.url. Accepts either a filesystem path or a file:// URL."""
    if p.startswith("file://"):
        p = urllib.request.url2pathname(urllib.parse.urlsplit(p).path)
    return pathlib.Path(p).resolve().as_uri()


def _replace_file(tmp, path):
    """os.replace with a short retry: Windows refuses while a reader holds the target open."""
    for attempt in range(5):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.1)


def _atomic_write(path, content):
    """Write through a temporary file in the same directory, so a reader never sees a part."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        _replace_file(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def _write_cache(path, url, text):
    """Write the header block plus the wrapped body, shared by a web fetch and a local ingest."""
    accessed = datetime.date.today().isoformat()
    header = (f"# url: {url}\n# accessed: {accessed}\n# chars: {len(text)}\n"
              "# Line breaks belong to this cache alone; the source has its own. Quote from inside one line.\n\n")
    _atomic_write(path, header + wrap_text(text) + "\n")


def cached_chars(path):
    """The `# chars:` header value of a cache file, the unit a fresh fetch reports."""
    with open(path, encoding="utf-8") as f:
        head = [f.readline() for _ in range(3)]
    for line in head:
        if line.startswith("# chars:"):
            return int(line.split(":", 1)[1])
    return None


def decompress(raw, encoding):
    """Undo a gzip or deflate Content-Encoding; other bodies come back as they are."""
    enc = (encoding or "").strip().lower()
    if enc in ("gzip", "x-gzip"):
        return zlib.decompress(raw, 47)
    if enc == "deflate":
        try:
            return zlib.decompress(raw)
        except zlib.error:
            return zlib.decompress(raw, -15)  # some servers send raw deflate with no zlib header
    return raw


def body_text(raw, headers):
    """Extract (text, None) from a fetched body by its content, else (None, unsupported detail)."""
    # get_content_type() reports text/plain when the header is absent; treat that as unknown
    ctype = headers.get_content_type() if headers is not None and headers.get("Content-Type") else ""
    charset = headers.get_content_charset() if headers is not None else None
    if raw[:5] == b"%PDF-":
        text, missing = pdf_text(io.BytesIO(raw))
        return (None, missing) if missing else (text, None)
    if raw[:2] == b"PK":
        try:
            with zipfile.ZipFile(io.BytesIO(raw)) as zf:
                names = zf.namelist()
        except zipfile.BadZipFile:
            names = None  # text that starts with "PK", such as "PKCS #11", falls through
        if names is not None:
            if "word/document.xml" not in names:
                return None, f"unsupported content type: {ctype or 'zip'}"
            try:
                return docx_text(io.BytesIO(raw)), None
            except Exception as exc:  # a corrupt entry or malformed XML, as ingest_one reports
                return None, f"unreadable DOCX: {exc.__class__.__name__}: {exc}"
    if ctype in PLAIN_TYPES:
        return decode_body(raw, charset), None
    if ctype.startswith("text/") or ctype in ("", "application/xhtml+xml", "application/xml"):
        return html_to_text(raw, charset), None
    return None, f"unsupported content type: {ctype}"


def fetch_one(url, run_dir, timeout, min_chars, force, throttle):
    """Fetch one URL into the cache. Returns the result dict."""
    path = os.path.join(run_dir, "pages", cache_name(url))
    if os.path.exists(path) and not force:
        return {"url": url, "status": "cached", "path": path,
                "chars": cached_chars(path), "detail": "already fetched (no duplicate fetch)"}

    status, raw, headers, err, truncated = http_fetch(url, timeout, method="GET", throttle=throttle)
    if status is None or status >= 400 or raw is None:
        return {"url": url, "status": "unreachable", "path": None, "chars": 0,
                "detail": f"GET failed: {err or status}"}
    if truncated and raw[:5] == b"%PDF-":
        return {"url": url, "status": "unsupported", "path": None, "chars": 0,
                "detail": "PDF larger than 50 MB"}
    if truncated and raw[:2] == b"PK":
        return {"url": url, "status": "unsupported", "path": None, "chars": 0,
                "detail": "document larger than 50 MB"}
    try:
        raw = decompress(raw, headers.get("Content-Encoding"))
    except (zlib.error, EOFError, OSError) as exc:
        return {"url": url, "status": "unreachable", "path": None, "chars": 0,
                "detail": f"GET failed: cannot decompress the body ({exc})"}
    text, unsupported = body_text(raw, headers)
    if unsupported:
        return {"url": url, "status": "unsupported", "path": None, "chars": 0, "detail": unsupported}
    is_pdf = raw[:5] == b"%PDF-"
    text = normalize_text(text)
    if len(text) < min_chars:
        where = "in the PDF text layer" if is_pdf else "of body"
        return {"url": url, "status": "thin", "path": None, "chars": len(text),
                "detail": f"only {len(text)} characters {where}"
                          + ("" if is_pdf else " (JavaScript-rendered or paywalled; fall back to WebFetch)")}

    _write_cache(path, url, text)
    return {"url": url, "status": "fetched", "path": path, "chars": len(text),
            "detail": f"HTTP {status}" + (" (PDF)" if is_pdf else "")}


def ingest_one(path, run_dir, min_chars=MIN_CHARS, force=False):
    """Ingest one local file into the cache, reported and keyed like a fetched URL.

    `path` may be a filesystem path or a file:// URL; both resolve to the same canonical
    file:// URL, which becomes the cache key and the source.url the collector records.
    `force` re-extracts a file whose content changed since it was first ingested.
    """
    url = canonical_file_url(path)
    fs_path = urllib.request.url2pathname(urllib.parse.urlsplit(url).path)
    cache_path = os.path.join(run_dir, "pages", cache_name(url))
    if os.path.exists(cache_path) and not force:
        return {"url": url, "status": "cached", "path": cache_path,
                "chars": cached_chars(cache_path), "detail": "already ingested (no duplicate read)"}

    if not os.path.exists(fs_path):
        return {"url": url, "status": "unreachable", "path": None, "chars": 0,
                "detail": f"file not found: {fs_path}"}

    try:
        text, status, detail = extract_local_text(fs_path)
    except Exception as exc:
        return {"url": url, "status": "unreadable", "path": None, "chars": 0,
                "detail": f"extraction raised {exc.__class__.__name__}: {exc}"}
    if status:
        return {"url": url, "status": status, "path": None, "chars": 0, "detail": detail}

    text = normalize_text(text)
    if len(text) < min_chars:
        return {"url": url, "status": "thin", "path": None, "chars": len(text),
                "detail": f"only {len(text)} characters of body"}

    _write_cache(cache_path, url, text)
    return {"url": url, "status": "ingested", "path": cache_path, "chars": len(text),
            "detail": f"local file: {fs_path}"}


def update_index(run_dir, results=None):
    """Rebuild pages/index.json (the URL-to-cache map) from the cache files' header lines.

    The files are the source of truth, so runs that share one pages/ directory cannot
    drop each other's entries. `results` is accepted for the callers that pass it.
    """
    pages = os.path.join(run_dir, "pages")
    index_path = os.path.join(pages, "index.json")
    index = {}
    for name in sorted(os.listdir(pages)) if os.path.isdir(pages) else []:
        if not name.endswith(".txt"):
            continue
        try:
            with open(os.path.join(pages, name), encoding="utf-8") as f:
                head = [f.readline() for _ in range(3)]
            url = head[0].split(":", 1)[1].strip() if head[0].startswith("# url:") else None
            chars = int(head[2].split(":", 1)[1]) if head[2].startswith("# chars:") else None
        except (OSError, ValueError):
            continue
        if url and chars is not None:
            index[url] = {"path": name, "chars": chars}
    _atomic_write(index_path, json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True))
    return index_path


def is_local_target(u):
    """A file:// URL or an existing local path routes to ingest_one; everything else fetches."""
    return u.startswith("file://") or os.path.exists(u)


def fetch_or_ingest(u, run_dir, timeout, min_chars, force, throttle):
    if is_local_target(u):
        return ingest_one(u, run_dir, min_chars, force)
    return fetch_one(u, run_dir, timeout, min_chars, force, throttle)


def main():
    _configure_stdout()
    parser = argparse.ArgumentParser(
        description="Fetch source pages, or ingest local materials, and cache their text")
    parser.add_argument("urls", nargs="+",
                        help="URLs to fetch, or local paths / file:// URLs to ingest")
    parser.add_argument("--run-dir", required=True, help="output directory (pages/ is created under it)")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--min-chars", type=int, default=MIN_CHARS,
                        help=f"minimum characters to count as a body (default {MIN_CHARS})")
    parser.add_argument("--force", action="store_true", help="fetch again even when cached")
    parser.add_argument("--json", action="store_true", help="print JSON")
    args = parser.parse_args()

    throttle = HostThrottle()
    urls = list(dict.fromkeys(args.urls))  # drop repeated URLs in the arguments
    workers = max(1, min(args.workers, len(urls)))
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(fetch_or_ingest, u, args.run_dir, args.timeout,
                               args.min_chars, args.force, throttle) for u in urls]
        results = [f.result() for f in futures]  # keep the input order

    try:
        index_path = update_index(args.run_dir, results)
    except OSError as e:
        print(f"error: cannot write index.json: {e}", file=sys.stderr)
        return 2

    failed = [r for r in results if r["status"] not in ("fetched", "cached", "ingested")]
    if args.json:
        print(json.dumps({"results": results, "index": index_path,
                          "failed": len(failed)}, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"[{r['status']}] {r['url']}"
                  + (f" -> {r['path']} ({r['chars']} chars)" if r["path"] else f" - {r['detail']}"))
        if failed:
            print(f"{len(failed)} URL(s) fall back to WebFetch (research-collector.md)")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
