#!/usr/bin/env python3
"""citation_verifier.py - machine verification of the citations in evidence_log.json.

check.py imports check_quote_match, normalize_text and cache_name, and calls run() once per
merge for URL reachability and DOI/arXiv resolution (empty quote); the command
line below reads a ledger in the {"evidence": [...]} shape. It
checks the HTTP reachability of every source URL, resolves DOIs and arXiv IDs, and matches
each verbatim_quote against the body of its source. Standard library only (it uses the
network).

The checks run in parallel under a per-host throttle (--workers, 8 by default). The interval
between requests to one host stays at REQUEST_INTERVAL, the same as the serial version, so
the load any one server sees is unchanged. The output follows the input order (evidence ID
order) and is deterministic.

Examples:
    python citation_verifier.py evidence_log.json
    python citation_verifier.py evidence_log.json --only E1,E3 --json
    python citation_verifier.py evidence_log.json --workers 1
    python citation_verifier.py evidence_log.json --offline
    python citation_verifier.py --sample > evidence_log.json

Output: citation_check.json, written by default to the directory of the input file. Every
evidence ID carries a severity (PASS/WARN/CRITICAL). A not_found result (the quote does not
match, or the DOI/arXiv ID does not resolve) is a CRITICAL candidate; check.py marks the item
failed. This script never rewrites evidence_log.json itself - writing verdicts
back is the parent's and the verifier's job.

Exit codes: 0 = PASS or WARN only / 1 = at least one CRITICAL / 2 = usage or I/O error
"""

import argparse
import concurrent.futures
import contextlib
import difflib
import hashlib
import html.parser
import json
import os
import random
import re
import sys
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = "research-team-citation-verifier/1.0 (stdlib urllib; research-team skill)"
DEFAULT_TIMEOUT = 15.0
MAX_BODY_BYTES = 2_000_000  # cap the body fetched, still far more than a quote match needs
PDF_MAX_BYTES = 50_000_000  # a PDF is read whole, because pypdf cannot parse a cut file
WHOLE_TYPES = {"application/pdf", "application/zip",
               "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
REQUEST_INTERVAL = (0.5, 1.0)  # minimum interval in seconds, per host, out of respect for robots
HOST_MIN_INTERVAL = {"export.arxiv.org": 3.0}  # the spacing the arXiv API terms of use state
QUOTE_MATCH_RATIO = 0.9
DEFAULT_WORKERS = 8   # default parallelism; HostThrottle keeps the per-host interval
MAX_WORKERS = 16      # beyond this the interval on shared API hosts sets the ceiling anyway

SEVERITY_ORDER = {"PASS": 0, "WARN": 1, "CRITICAL": 2}

SAMPLE = {
    "schema": "research-evidence-1.1",
    "topic": "Detecting fabricated citations produced by LLMs",
    "as_of": "2026-07-11",
    "mode": "STANDARD",
    "key_questions": [
        {"id": "KQ1", "text": "Which methods detect fabricated LLM citations mechanically?"},
    ],
    "evidence": [
        {
            "id": "E1",
            "kq_ids": ["KQ1"],
            "claim": "The Semantic Scholar Academic Graph API is free to use",
            "claim_type": "fact",
            "verbatim_quote": "Semantic Scholar Academic Graph API is free to use",
            "source": {
                "publisher": "Semantic Scholar",
                "title": "Academic Graph API",
                "url": "https://www.semanticscholar.org/product/api",
                "published": "2024",
                "grade": "A",
                "origin_cluster": "src-s2",
            },
            "accessed": "2026-07-11",
            "is_key_figure": False,
            "corroboration": "single_source",
            "corroborating_ids": [],
            "verification": {"status": "unchecked", "note": "illustration for citation_verifier.py --sample"},
        },
        {
            "id": "E2",
            "kq_ids": ["KQ1"],
            "claim": "arXiv:2402.14207 covers a citation verification method (illustration)",
            "claim_type": "fact",
            "verbatim_quote": "we propose a citation verification method",
            "source": {
                "publisher": "arXiv",
                "title": "Citation Verification (illustration)",
                "url": "https://arxiv.org/abs/2402.14207",
                "published": "2024-02",
                "grade": "A",
                "origin_cluster": "src-arxiv",
                "arxiv_id": "2402.14207",
            },
            "accessed": "2026-07-11",
            "is_key_figure": False,
            "corroboration": "single_source",
            "corroborating_ids": [],
            "verification": {"status": "unchecked", "note": "illustration for citation_verifier.py --sample"},
        },
    ],
    "disconfirmation": [
        {
            "hypothesis": "H1: machine citation checks alone rule out fabrication entirely",
            "expected_if_false": "reports of fabrications subtle enough to pass a machine check",
            "queries": ["{disconfirming query}"],
            "found": "nothing found",
            "impact": "no evidence turned up that lowers the likelihood of H1",
        }
    ],
    "search_log": [
        {"query": "{query 1}", "tool": "WebSearch",
         "kind": "normal", "adopted": 1, "kq_id": "KQ1"},
    ],
    "gaps": [],
}


def _configure_stdout():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def bump(current, new):
    """Raise the severity, never lower it."""
    return new if SEVERITY_ORDER[new] > SEVERITY_ORDER[current] else current


def normalize_text(s):
    """Normalise to NFKC and collapse whitespace, ahead of matching a quote."""
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"\s+", " ", s).strip()


def strip_cache_header(text):
    """The page body of a fetch_page.py cache file: the text after its `# url:` header block."""
    return text.split("\n\n", 1)[-1] if text.startswith("# url:") else text


def cache_name(url):
    """The page-cache file name for a URL (also used by fetch_page.py, which imports this)."""
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:16] + ".txt"


BLOCK_TAGS = frozenset((
    "p", "div", "br", "li", "ul", "ol", "tr", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6",
    "section", "article", "header", "footer", "table", "blockquote", "pre",
    "title", "nav", "main", "aside", "dl", "dt", "dd", "figure", "figcaption", "form"))


class _TextExtractor(html.parser.HTMLParser):
    """Extract the visible text of an HTML page, dropping tags, script and style.

    Text inside inline elements joins its neighbours with no separator; a block-level tag
    puts one space, so a word or a Japanese sentence split by <strong> or <a> stays whole.
    """

    def __init__(self):
        super().__init__()
        self._skip_depth = 0
        self._parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip_depth += 1
        elif tag in BLOCK_TAGS and self._skip_depth == 0:
            self._parts.append(" ")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip_depth > 0:
            self._skip_depth -= 1
        elif tag in BLOCK_TAGS and self._skip_depth == 0:
            self._parts.append(" ")

    def handle_data(self, data):
        if self._skip_depth == 0:
            self._parts.append(data)

    def get_text(self):
        return "".join(self._parts)


META_CHARSET = re.compile(rb"""<meta[^>]+charset\s*=\s*["']?\s*([A-Za-z0-9_\-]+)""", re.I)


# Python's shift_jis and euc-jp are strict JIS X 0208/0212 codecs; pages written with the
# Windows and JIS X 0213 extensions need their supersets.
CHARSET_ALIASES = {"shift_jis": "cp932", "shift-jis": "cp932", "sjis": "cp932", "x-sjis": "cp932",
                   "ms_kanji": "cp932", "windows-31j": "cp932", "euc-jp": "euc_jis_2004",
                   "eucjp": "euc_jis_2004", "x-euc-jp": "euc_jis_2004"}


def decode_body(body_bytes, encoding_hint=None):
    """Decode with the header charset, else the page's <meta> charset, else the first strict
    decode among UTF-8 and the Japanese legacy encodings (many go.jp pages send Shift_JIS
    with no header charset)."""
    meta = META_CHARSET.search(body_bytes[:4096])
    declared = [encoding_hint, meta.group(1).decode("ascii") if meta else None]
    for enc in declared:
        if not enc:
            continue
        try:
            return body_bytes.decode(CHARSET_ALIASES.get(enc.lower(), enc), errors="replace")
        except LookupError:
            continue
    for enc in ("utf-8", "cp932", "euc_jis_2004"):
        try:
            return body_bytes.decode(enc)
        except UnicodeDecodeError:
            continue
    return body_bytes.decode("utf-8", errors="replace")


def html_to_text(body_bytes, encoding_hint=None):
    text = decode_body(body_bytes, encoding_hint)
    parser = _TextExtractor()
    try:
        parser.feed(text)
    except Exception:
        pass  # on broken HTML, match against however much text was parsed
    return parser.get_text()


class HostThrottle:
    """Throttle that keeps a minimum interval between requests to the same host.

    Each host holds a reservation for the earliest time the next request to it may start.
    A caller takes the reservation, releases the lock, and only then sleeps until that time,
    so every server sees requests at least REQUEST_INTERVAL apart while requests to
    different hosts never wait on each other.

    The host lock is deliberately not held while sleeping. Holding it would let a task
    bound for a slow shared host (api.crossref.org, export.arxiv.org, archive.org) occupy a
    worker for the whole response time of the task ahead of it, and work on other hosts
    would never start. The reservation scheme allows requests to one host to overlap when
    responses are slower than the interval, and in exchange the waiting never chains onto
    response times.
    """

    def __init__(self, interval=None):
        # Read the default from the module constant at call time, so a test can swap
        # REQUEST_INTERVAL out.
        self._interval = interval or REQUEST_INTERVAL
        self._guard = threading.Lock()
        self._next_free = {}   # host -> time.monotonic() when the next request may start
        self._rand = random.Random(0)  # only draws wait times; no effect on the verdicts

    @contextlib.contextmanager
    def slot(self, url):
        host = (urllib.parse.urlsplit(url).hostname or "").lower()
        with self._guard:
            now = time.monotonic()
            start = max(now, self._next_free.get(host, now))
            # an interval of (0, 0) switches throttling off, so it drops the host floor too
            floor = HOST_MIN_INTERVAL.get(host, 0.0) if self._interval[1] > 0 else 0.0
            gap = max(self._rand.uniform(*self._interval), floor)
            self._next_free[host] = start + gap
        wait = start - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        yield


def _read_capped(resp, timeout, max_bytes, pdf_max_bytes):
    """Read the body in chunks up to the cap (the document cap for a PDF or a zip such as DOCX).

    Returns (body, truncated). A PDF or zip is known by its Content-Type or its first bytes;
    neither parses when cut. The read stops with TimeoutError once the whole request has run
    past twice `timeout` (eight times under the larger document cap), because the socket
    timeout alone restarts on every chunk.
    """
    start = time.monotonic()
    whole = resp.headers.get_content_type() in WHOLE_TYPES
    chunks, size, cap, factor = [], 0, None, 2
    while True:
        chunk = resp.read1(65536)
        if not chunk:
            return b"".join(chunks), False
        chunks.append(chunk)
        size += len(chunk)
        if cap is None and size >= 5:
            head = b"".join(chunks)[:5]
            whole = whole or head == b"%PDF-" or head[:2] == b"PK"
            cap = pdf_max_bytes if whole else max_bytes
            factor = 8 if cap > max_bytes else 2
        if cap is not None and size >= cap:
            body = b"".join(chunks)
            return body[:cap], len(body) > cap or bool(resp.read1(1))
        if time.monotonic() > start + factor * timeout:
            raise TimeoutError(f"timed out: the response took more than {factor} times the timeout")


def http_fetch(url, timeout, method="GET", throttle=None, max_bytes=None, pdf_max_bytes=None):
    """Send a GET or HEAD. Returns (status, body, headers, error, truncated); never raises.

    The size cap is chosen per call: `max_bytes` (MAX_BODY_BYTES by default) for a page,
    `pdf_max_bytes` (PDF_MAX_BYTES by default) when the body is a PDF. `truncated` is True
    when the cap cut the body.
    """
    max_bytes = MAX_BODY_BYTES if max_bytes is None else max_bytes
    pdf_max_bytes = PDF_MAX_BYTES if pdf_max_bytes is None else pdf_max_bytes
    req = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
    ctx = throttle.slot(url) if throttle is not None else contextlib.nullcontext()
    try:
        with ctx, urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.getcode()
            body, truncated = (_read_capped(resp, timeout, max_bytes, pdf_max_bytes)
                               if method == "GET" else (b"", False))
            return status, body, resp.headers, None, truncated
    except urllib.error.HTTPError as e:
        return e.code, None, None, str(e), False
    except Exception as e:
        # Record network failures (timeout, URLError, ConnectionError) and carry on
        return None, None, None, str(e), False


def http_request(url, timeout, method="GET", throttle=None):
    """Send a GET or HEAD. Returns (status, body, encoding, error) and never raises."""
    # a PDF keeps the page cap here: callers match text and never parse the PDF
    status, body, headers, err, _ = http_fetch(url, timeout, method, throttle,
                                               pdf_max_bytes=MAX_BODY_BYTES)
    return status, body, headers.get_content_charset() if headers is not None else None, err


def check_url_reachability(url, timeout, need_body, throttle=None):
    """Check that a URL is reachable. Returns (url_status, body_text_or_None, truncated, detail).

    Where the body is needed - that is, wherever the evidence unit carries a quote, which is
    nearly always, since the quote is a required field - only a GET is sent, no HEAD. The
    GET's status settles reachability just as well. Sending a HEAD first would double the
    number of requests, and on an unreachable URL it would double the timeout wait too.
    """
    if need_body:
        g_status, body, ctype, g_err = http_request(url, timeout, method="GET", throttle=throttle)
        if g_status is not None and g_status < 400:
            text = html_to_text(body, ctype) if body is not None else None
            truncated = body is not None and len(body) >= MAX_BODY_BYTES
            return "reachable", text, truncated, f"GET {g_status}"
        return "unreachable", None, False, f"GET failed: {g_err or g_status}"

    h_status, _, _, h_err = http_request(url, timeout, method="HEAD", throttle=throttle)
    if h_status is not None and h_status < 400:
        return "reachable", None, False, f"HEAD {h_status}"

    # The HEAD errored or is unsupported, so fall back to a GET
    g_status, _, _, g_err = http_request(url, timeout, method="GET", throttle=throttle)
    if g_status is not None and g_status < 400:
        return "reachable", None, False, f"GET {g_status} (HEAD failed: {h_err})"
    return "unreachable", None, False, f"GET failed: {g_err or g_status} (HEAD failed: {h_err})"


def check_wayback(url, timeout, throttle=None):
    """Query the Wayback Availability API. Returns (archive_dict_or_None, detail)."""
    api = "https://archive.org/wayback/available?url=" + urllib.parse.quote(url, safe="")
    status, body, _, err = http_request(api, timeout, method="GET", throttle=throttle)
    if status != 200 or body is None:
        return None, f"the Wayback query failed: {err or status}"
    try:
        data = json.loads(body.decode("utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None, "the Wayback response is not valid JSON"
    closest = (data.get("archived_snapshots") or {}).get("closest")
    if not closest or not closest.get("available"):
        return None, "the Wayback Machine holds no snapshot"
    return {"wayback_url": closest.get("url", ""), "timestamp": closest.get("timestamp", "")}, \
        "the Wayback Machine holds a snapshot"


def check_doi(doi, timeout, throttle=None):
    """Resolve a DOI. Returns (status, detail); status is resolved, not_found or error.

    Crossref is asked first, and on a 404 the query falls back to doi.org's registration
    agency (RA) API. Without that fallback a real DOI registered outside Crossref - a
    DataCite one, say, such as an arXiv DOI under 10.48550/... - would be called a
    fabrication on the strength of a Crossref 404 alone. Only a DOI the RA API does not
    know either comes back as not_found.
    """
    api = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    status, _body, _, err = http_request(api, timeout, method="GET", throttle=throttle)
    if status == 200:
        return "resolved", "resolved through Crossref"
    if status != 404:
        return "error", f"the Crossref query errored: {err or status}"

    ra_api = "https://doi.org/ra/" + urllib.parse.quote(doi, safe="/")
    ra_status, ra_body, _, ra_err = http_request(ra_api, timeout, method="GET", throttle=throttle)
    if ra_status != 200 or ra_body is None:
        return "error", f"Crossref returned 404 and the doi.org RA query errored: {ra_err or ra_status}"
    try:
        entries = json.loads(ra_body.decode("utf-8", errors="replace"))
        entry = entries[0] if isinstance(entries, list) and entries else {}
    except json.JSONDecodeError:
        return "error", "the doi.org RA response is not valid JSON"
    if entry.get("RA"):
        return "resolved", (f"Crossref returned 404, but doi.org resolved it through the "
                            f"registration agency {entry['RA']}")
    return "not_found", ("Crossref returned 404 and doi.org holds no registration either "
                         "(possible fabrication)")


def check_arxiv(arxiv_id, timeout, throttle=None):
    """Resolve an arXiv ID through export.arxiv.org, falling back to the abstract page.

    Returns (status, detail); status is resolved, not_found or error. HostThrottle keeps 3
    seconds between requests to export.arxiv.org, the spacing the arXiv API terms state; an
    API failure (HTTP 429 under load) falls back to a HEAD, then a GET, on
    https://arxiv.org/abs/{id}: 200 counts as resolved, 404 as not_found. The API stays
    the first attempt.
    """
    api = "http://export.arxiv.org/api/query?id_list=" + urllib.parse.quote(arxiv_id, safe="")
    api_status, body, _, api_err = http_request(api, timeout, method="GET", throttle=throttle)
    if api_status == 200 and body is not None:
        text = body.decode("utf-8", errors="replace")
        m = re.search(r"<opensearch:totalResults[^>]*>(\d+)</opensearch:totalResults>", text)
        if m and int(m.group(1)) == 0:
            return "not_found", "arXiv holds no such ID (possible fabrication)"
        if "<entry>" in text:
            return "resolved", "resolved through the arXiv API"

    api_detail = f"the arXiv API query failed: {api_err or api_status}"
    abs_url = "https://arxiv.org/abs/" + urllib.parse.quote(arxiv_id, safe="")
    h_status, _, _, h_err = http_request(abs_url, timeout, method="HEAD", throttle=throttle)
    if h_status == 200:
        return "resolved", f"{api_detail}; resolved through the abstract page (HEAD {h_status})"
    if h_status == 404:
        return "not_found", f"{api_detail}; the abstract page is 404 (possible fabrication)"

    g_status, _, _, g_err = http_request(abs_url, timeout, method="GET", throttle=throttle)
    if g_status == 200:
        return "resolved", (f"{api_detail}; resolved through the abstract page "
                            f"(GET {g_status}, HEAD failed: {h_err})")
    if g_status == 404:
        return "not_found", f"{api_detail}; the abstract page is 404 (possible fabrication)"
    return "error", f"{api_detail}; the abstract page also failed: {g_err or g_status}"


def containment(norm_quote, norm_body):
    """How much of the quote appears, in order, somewhere in the body (0.0-1.0).

    The body is scanned with windows twice the quote's length, stepped by one quote
    length, so the quote always falls inside one window whatever its offset in the page.
    The score is the count of quote characters matched inside the window. A symmetric
    similarity ratio over an equal-length window would charge the quote for the surrounding
    page text, which made the verdict depend on where the quote happened to sit; the count
    depends only on whether the quote is there.
    """
    qlen = len(norm_quote)
    best = 0.0
    for i in range(0, max(1, len(norm_body)), qlen):
        window = norm_body[i:i + 2 * qlen]
        matcher = difflib.SequenceMatcher(None, norm_quote, window, autojunk=False)
        matched = sum(b.size for b in matcher.get_matching_blocks())
        best = max(best, matched / qlen)
        if best >= QUOTE_MATCH_RATIO:
            break
    return best


def check_quote_match(quote, body_text, truncated=False):
    """Match a verbatim_quote against the source body.

    Returns (quote_match, detail); quote_match is found, not_found or unfetchable.
    """
    if body_text is None:
        return "unfetchable", "the body could not be fetched (possibly a 403 or a JS-only page)"
    norm_quote = normalize_text(quote)
    norm_body = normalize_text(body_text)
    if not norm_quote:
        return "not_found", "the verbatim_quote is empty"
    if norm_quote in norm_body:
        return "found", "the quote appears in the body"
    if not norm_body:
        return "not_found", "the body is empty"
    best = containment(norm_quote, norm_body)
    if best >= QUOTE_MATCH_RATIO:
        return "found", (f"found a window matching {best:.2f} of the quote "
                         f"(difflib, threshold {QUOTE_MATCH_RATIO})")
    if truncated:
        # The body was cut at the fetch limit. A quote beyond the cut may well be genuine.
        return "unfetchable", (f"the best match is {best:.2f}, but the body was cut at "
                               f"{MAX_BODY_BYTES} bytes (the quote may lie past the cut)")
    return "not_found", (f"the best match is {best:.2f}, below the threshold "
                         f"{QUOTE_MATCH_RATIO}")


def verify_one(e, timeout, offline, throttle=None, pages_dir=None):
    eid = e.get("id", "?")
    src = e.get("source") or {}
    quote = e.get("verbatim_quote", "")
    url = src.get("url", "")
    doi = src.get("doi")
    arxiv_id = src.get("arxiv_id")
    result = {"id": eid, "url": url, "doi": doi, "arxiv_id": arxiv_id}

    # A local source (fetch_page.py's ingest_one, url starting with file://, or a source
    # that carries local_path) needs no network for its own check, so it runs even under
    # --offline; only its doi/arxiv fields, if any, still honour that flag below.
    is_local = url.startswith("file://") or bool(src.get("local_path"))

    if offline and not is_local:
        result.update({
            "url_status": "skipped", "archive": None,
            "doi_status": "skipped" if doi else "n/a",
            "arxiv_status": "skipped" if arxiv_id else "n/a",
            "quote_match": "skipped",
            "severity": "WARN" if (url or doi or arxiv_id) else "PASS",
            "detail": "not verified: offline mode",
        })
        return result

    notes = []
    severity = "PASS"

    if is_local:
        cache_path = os.path.join(pages_dir or "", cache_name(url))
        if os.path.exists(cache_path):
            with open(cache_path, encoding="utf-8") as f:
                body_text = strip_cache_header(f.read())
            url_status, truncated, detail = "local", False, f"read from the page cache: {cache_path}"
        else:
            url_status, body_text, truncated, detail = "unreachable", None, False, \
                f"no cached file for this local source: {cache_path}"
    elif url:
        need_body = bool(quote)
        url_status, body_text, truncated, detail = check_url_reachability(
            url, timeout, need_body, throttle)
    else:
        url_status, body_text, truncated, detail = "skipped", None, False, "no url"
    notes.append(f"url: {detail}")
    if url_status == "unreachable":
        severity = bump(severity, "WARN")

    archive = None
    if url_status == "unreachable" and not is_local:
        archive, wb_detail = check_wayback(url, timeout, throttle)
        notes.append(f"wayback: {wb_detail}")

    # Reaching this line with offline True means is_local was True (the early return above
    # covers every other case), so this guard also keeps a local source's own doi/arxiv
    # fields from reaching the network under --offline.
    if doi and offline:
        doi_status, doi_detail = "skipped", "not verified: offline mode"
    elif doi:
        doi_status, doi_detail = check_doi(doi, timeout, throttle)
    else:
        doi_status, doi_detail = "n/a", "no source.doi"
    notes.append(f"doi: {doi_detail}")
    if doi_status == "not_found":
        severity = "CRITICAL"
    elif doi_status == "error":
        severity = bump(severity, "WARN")

    if arxiv_id and offline:
        arxiv_status, arxiv_detail = "skipped", "not verified: offline mode"
    elif arxiv_id:
        arxiv_status, arxiv_detail = check_arxiv(arxiv_id, timeout, throttle)
    else:
        arxiv_status, arxiv_detail = "n/a", "no source.arxiv_id"
    notes.append(f"arxiv: {arxiv_detail}")
    if arxiv_status == "not_found":
        severity = "CRITICAL"
    elif arxiv_status == "error":
        severity = bump(severity, "WARN")

    if not quote:
        quote_match, quote_detail = "n/a", "no verbatim_quote"
    elif not url:
        quote_match, quote_detail = "unfetchable", "no url, so the body cannot be fetched"
    else:
        quote_match, quote_detail = check_quote_match(quote, body_text, truncated)
        if quote_match == "not_found" and not is_local and pages_dir:
            cache_path = os.path.join(pages_dir, cache_name(url))
            if os.path.exists(cache_path):
                with open(cache_path, encoding="utf-8") as f:
                    cached_text = strip_cache_header(f.read())
                cached_match, cached_detail = check_quote_match(quote, cached_text)
                if cached_match == "found":
                    quote_match = "found_cached"
                    quote_detail = ("the live page text differs from fetch_page.py's "
                                    "cached extraction; matched there instead: " + cached_detail)
    notes.append(f"quote: {quote_detail}")
    if quote_match == "not_found":
        severity = "CRITICAL"
    elif quote_match == "unfetchable":
        severity = bump(severity, "WARN")

    result.update({
        "url_status": url_status, "archive": archive,
        "doi_status": doi_status, "arxiv_status": arxiv_status,
        "quote_match": quote_match, "severity": severity,
        "detail": " / ".join(notes),
    })
    return result


def needs_retry(r):
    """Is this result a WARN whose cause might be transient (worth one re-request)?"""
    return (r["severity"] == "WARN"
            and (r.get("url_status") in ("unreachable", "error")
                 or r.get("doi_status") == "error"
                 or r.get("arxiv_status") == "error"
                 or r.get("quote_match") == "unfetchable"))


def retry_warn_results(log, results, timeout, throttle, pages_dir=None):
    """Re-request once every WARN result that might have been transient network trouble,
    and replace the record only when the retry does better (never worse).

    A local (file://) source is skipped: no network request changes a missing cache file.
    """
    evidence_by_id = {e.get("id"): e for e in log.get("evidence", [])}
    out = []
    for r in results:
        e = evidence_by_id.get(r["id"])
        if not needs_retry(r) or e is None or (r.get("url") or "").startswith("file://"):
            out.append(r)
            continue
        retry = verify_one(e, timeout, False, throttle, pages_dir=pages_dir)
        out.append(retry if SEVERITY_ORDER[retry["severity"]] < SEVERITY_ORDER[r["severity"]] else r)
    return out


def run(log, only_ids, timeout, offline, workers=DEFAULT_WORKERS, pages_dir=None, retry_warn=False):
    evidence = log.get("evidence", [])
    if only_ids:
        wanted = set(only_ids)
        evidence = [e for e in evidence if e.get("id") in wanted]

    throttle = None
    if offline or workers <= 1 or len(evidence) <= 1:
        results = [verify_one(e, timeout, offline, pages_dir=pages_dir) for e in evidence]
    else:
        throttle = HostThrottle()
        n = min(workers, MAX_WORKERS, len(evidence))
        with concurrent.futures.ThreadPoolExecutor(max_workers=n) as ex:
            # map returns results in input order, so results stays in evidence ID order
            results = list(ex.map(
                lambda e: verify_one(e, timeout, offline, throttle, pages_dir=pages_dir), evidence))

    if retry_warn and not offline:
        results = retry_warn_results(log, results, timeout, throttle or HostThrottle(), pages_dir)

    critical = [r for r in results if r["severity"] == "CRITICAL"]
    warn = [r for r in results if r["severity"] == "WARN"]
    verdict = "CRITICAL" if critical else ("WARN" if warn else "PASS")

    return {
        "verdict": verdict,
        "checked_count": len(results),
        "critical_count": len(critical),
        "warn_count": len(warn),
        "offline": offline,
        "results": results,
    }


def main():
    _configure_stdout()
    parser = argparse.ArgumentParser(
        description="Machine verification of the citations in evidence_log.json "
                    "(URL reachability, DOI/arXiv resolution, quote matching)")
    parser.add_argument("log", nargs="?", help="path to evidence_log.json")
    parser.add_argument("--only",
                        help="comma-separated evidence IDs to verify (e.g. E1,E3)")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                        help=f"HTTP timeout in seconds (default {DEFAULT_TIMEOUT:.0f})")
    parser.add_argument("--offline", action="store_true",
                        help="use no network and record every check as skipped")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS,
                        help=f"how many checks run in parallel (default {DEFAULT_WORKERS}; "
                             f"1 runs them serially). The "
                             f"{REQUEST_INTERVAL[0]}-{REQUEST_INTERVAL[1]}s interval between "
                             f"requests to one host holds in parallel too")
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--output", default=None,
                        help="where to write citation_check.json "
                             "(default: the directory of the input file)")
    parser.add_argument("--pages-dir", default=None,
                        help="fetch_page.py's page cache, matched when the live page "
                             "differs and read for file:// sources "
                             "(default: pages/ beside the input file)")
    parser.add_argument("--retry-warn", action="store_true",
                        help="after the main pass, re-request once every WARN result "
                             "that might have been transient network trouble")
    parser.add_argument("--sample", action="store_true",
                        help="print a sample evidence ledger and exit")
    args = parser.parse_args()

    if args.sample:
        print(json.dumps(SAMPLE, ensure_ascii=False, indent=2))
        return 0

    if not args.log:
        parser.error("give the path to evidence_log.json, or --sample")

    try:
        with open(args.log, encoding="utf-8") as f:
            log = json.load(f)
    except OSError as e:
        print(f"error: cannot read the file: {e}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"error: the file is not valid JSON: {e}", file=sys.stderr)
        return 2

    only_ids = [x.strip() for x in args.only.split(",") if x.strip()] if args.only else None
    log_dir = os.path.dirname(os.path.abspath(args.log)) or "."
    pages_dir = args.pages_dir or os.path.join(log_dir, "pages")

    summary = run(log, only_ids, args.timeout, args.offline, args.workers,
                  pages_dir=pages_dir, retry_warn=args.retry_warn)

    output_path = args.output or os.path.join(log_dir, "citation_check.json")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"error: cannot write the output file: {e}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"verdict: {summary['verdict']} ({summary['checked_count']} checked / "
              f"CRITICAL {summary['critical_count']} / WARN {summary['warn_count']})")
        print(f"output: {output_path}")
        for r in summary["results"]:
            print(f"  [{r['severity']}] {r['id']}: url={r['url_status']} doi={r['doi_status']} "
                  f"arxiv={r['arxiv_status']} quote={r['quote_match']}")
            if r["archive"]:
                print(f"      archive: {r['archive']['wayback_url']} ({r['archive']['timestamp']})")

    return 1 if summary["critical_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
