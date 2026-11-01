#!/usr/bin/env python3
"""check.py - lint collector files and merge them into evidence.jsonl (research-team 2.0).

Copied from research-team with two changes, listed in NOTICE-research-team.md beside this file:
the grade enumeration is A to D (evidence-grading.md) and paper items are rejected, since the
company research has no academic route.

Used in research-team Step 2 (collectors lint their own file) and Step 3.1 (the lead merges
every collector file, assigns evidence ids and checks each item). Standard library only; the
merge uses the network through citation_verifier unless --offline is given.

Examples:
    python check.py --run-dir research/20261024-topic --lint research/20261024-topic/collect/SQ1_web.jsonl
    python check.py --run-dir research/20261024-topic
    python check.py --run-dir research/20261024-topic --only SQ3
    python check.py --run-dir research/20261024-topic --offline
    python check.py --run-dir research/20261024-topic --append research/20261024-topic/claims/opposing.jsonl

Output (merge): evidence.jsonl (each item plus "id" and "check"), digests/SQ{n}.md (the passing
and warn items, each quote with up to 400 characters of context from the cached page) and
gaps.json ({"empty_sq": [...], "failed": [{"id", "reason"}]}). The stdout summary is capped at
40 lines. --only SQ3 re-runs the merge for that sub-question: its old items are replaced, the
new ones take ids after the current maximum, and every other item keeps its id.

--append FILE (Step 6) checks the items of FILE, adds them after the highest id, rewrites the
digests of their sub-questions and prints one line per new id; every earlier id stays. It
exits 1 when an added item fails.
The merge sets each item's cluster: a paper's DOI or arXiv id, the account on a platform host
when the collector left the URL's domain, any other collector value as it is.
A web or local quote passes when it appears verbatim in the page body; it may differ only in
whitespace, typographic quotes, dashes, soft hyphens and zero-width characters.
--lint prints one "N items, M failing" line to stderr; stdout holds the "line k:" failures and,
for a misnamed file, one "file NAME:" line.
A collect/SQ*_*.jsonl file whose name is not SQ{n}_web.jsonl or SQ{n}_academic.jsonl, and an
item whose sq differs from its file name, are failures. --only is case-insensitive.

Exit codes: --lint 0 = clean / 1 = at least one failing item; merge 0 = done (items may have
failed) / 2 = usage or I/O error
"""

import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import citation_verifier as cv  # noqa: E402
import triage_sources as ts  # noqa: E402

REQUIRED = ["sq", "claim", "quote", "url", "title", "publisher", "date", "grade", "cluster",
            "stance", "kind"]
# grades A to D follow references/evidence-grading.md of this skill
ENUMS = {"grade": ("A", "B", "C", "D"), "stance": ("supports", "opposes", "context"),
         "kind": ("fact", "figure", "estimate")}
DATE_RE = re.compile(r"^(\d{4}(-\d{2}(-\d{2})?)?|unknown)$")
FILE_RE = re.compile(r"^SQ(\d+)_(web|academic)\.jsonl$")
CONTEXT = 400
MAX_LINES = 40
# the only differences a verbatim quote may carry: typographic quotes, dashes, soft hyphens,
# zero-width characters and whitespace
FOLD = str.maketrans({**dict.fromkeys("\u201c\u201d\u201e\u201f\u2033", '"'),
                      **dict.fromkeys("\u2018\u2019\u201a\u201b\u2032", "'"),
                      **dict.fromkeys("\u2010\u2011\u2012\u2013\u2014\u2015\u2212", "-"),
                      **dict.fromkeys("\u00ad\u200b\u200c\u200d\ufeff", None)})


def _configure_stdout():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def read_jsonl(path):
    """Return [(line_number, item or None, error or None)] for the non-blank lines."""
    rows = []
    with open(path, encoding="utf-8") as f:
        for k, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                rows.append((k, None, f"invalid JSON ({exc.msg})"))
                continue
            if not isinstance(item, dict):
                rows.append((k, None, "the line holds a value other than a JSON object"))
                continue
            rows.append((k, item, None))
    return rows


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return default


def page_text(run_dir, url):
    """Cached page text for a URL, or None when the page was never fetched.

    The file name derives from the URL, so a lost index.json entry (parallel collectors
    rewrite the index without a lock) does not hide a cached page.
    """
    try:
        with open(os.path.join(run_dir, "pages", cv.cache_name(url)), encoding="utf-8") as f:
            return cv.strip_cache_header(f.read())
    except OSError:
        return None


def squeeze(text):
    """The text a verbatim quote is compared on: NFKC, FOLD applied, whitespace removed."""
    return re.sub(r"\s+", "", cv.normalize_text(text).translate(FOLD))


def numbers_present(quote, body):
    """Every digit run of the quote must stand alone somewhere in the body (both normalised)."""
    nq, nb = cv.normalize_text(quote), cv.normalize_text(body)
    return all(re.search(r"(?<!\d)" + re.escape(n) + r"(?!\d)", nb) for n in re.findall(r"\d+", nq))


def file_sq_error(path, item):
    """Reason when the item's sq differs from the SQ in its collector file name, else None."""
    m = FILE_RE.match(os.path.basename(path))
    if m and item.get("sq") != f"SQ{m.group(1)}":
        return f"sq {item.get('sq')!r} differs from the file name's SQ{m.group(1)}"
    return None


def lint_item(run_dir, item, dbs):
    """Return (reason or None, quote_match). The shape, the page and the quote, no network."""
    for key in REQUIRED:
        if item.get(key) in (None, ""):
            return f"missing required field {key}", None
    for key in ("claim", "quote", "url", "title", "publisher"):
        if not isinstance(item[key], str):
            return f"field {key} must be a string", None
    for key, allowed in ENUMS.items():
        if item[key] not in allowed:
            return f"unknown {key} value {item[key]!r}", None
    if not isinstance(item["date"], str) or not DATE_RE.match(item["date"]):
        return f"bad date {item['date']!r}", None
    if item.get("paper"):  # this skill has no academic route; every quote comes from a cached page
        return "paper items are outside this skill; quote from a cached page", None
    text = page_text(run_dir, item["url"])
    if text is None:
        return f"no cached page for {item['url']} in pages/", None
    if squeeze(item["quote"]) not in squeeze(text):
        if not numbers_present(item["quote"], text):
            return "a number in the quote is absent from the page", "not_found"
        match, detail = cv.check_quote_match(item["quote"], text)
        if match != "found":
            return f"quote not found in the cached page ({detail})", match
        return f"quote not verbatim in the cached page ({detail}); copy it again from the page", \
            "not_found"
    return None, "found"


def run_lint(run_dir, path):
    dbs = {}
    failures = count = 0
    name = os.path.basename(path)
    bad_name = not FILE_RE.match(name)
    if bad_name:  # the merge skips such a file, so its items would be lost
        print(f"file {name}: the name is outside SQn_web.jsonl / SQn_academic.jsonl")
    for k, item, err in read_jsonl(path):
        count += 1
        if err is None:
            err, _ = lint_item(run_dir, item, dbs)
        if err is None:
            err = file_sq_error(path, item)
        if err:
            failures += 1
            print(f"line {k}: {err}")
    print(f"{count} items, {failures} failing", file=sys.stderr)
    return 1 if failures or bad_name else 0


def collector_files(run_dir, only):
    """Return (collector files in merge order, names of SQ*_*.jsonl files that fail FILE_RE)."""
    found, bad = [], []
    for path in glob.glob(os.path.join(run_dir, "collect", "SQ*_*.jsonl")):
        m = FILE_RE.match(os.path.basename(path))
        if not m:
            bad.append(os.path.basename(path))
        elif only is None or f"SQ{m.group(1)}" == only:
            found.append((int(m.group(1)), m.group(2) != "web", path))
    return [p for _, _, p in sorted(found)], sorted(bad)


def context_of(text, quote):
    """The quote with up to CONTEXT characters of the cached page around it."""
    body = cv.normalize_text(text)
    nq = cv.normalize_text(quote)
    i = body.find(nq)
    if i < 0:
        return nq
    return body[max(0, i - CONTEXT):i + len(nq) + CONTEXT]


def write_digest(run_dir, sq, items):
    lines = []
    for it in items:
        if it["check"]["status"] == "fail":
            continue
        text = None if it.get("paper") else page_text(run_dir, it["url"])
        lines += [f"### {it['id']} ({it['grade']}, {it['stance']}, {it['kind']}) "
                  f"{it['check']['status']}, cluster {it['cluster']}", "",
                  it["claim"], "", f"{it['publisher']}, {it['date']}, {it['url']}", "",
                  "> " + (context_of(text, it["quote"]) if text else it["quote"]), ""]
    os.makedirs(os.path.join(run_dir, "digests"), exist_ok=True)
    with open(os.path.join(run_dir, "digests", f"{sq}.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def item_cluster(item):
    """The item's independence cluster: a paper by its arXiv id or DOI; a cluster the collector
    left at the URL's domain refined to the account on platform hosts; any other value kept."""
    arxiv = str(item.get("arxiv_id") or "").strip().lower()
    doi = str(item.get("doi") or "").strip().lower()
    if not arxiv and doi.startswith("10.48550/arxiv."):  # the DOI DataCite gives an arXiv preprint
        arxiv = doi[len("10.48550/arxiv."):]
    if arxiv:
        return "arxiv:" + re.sub(r"v\d+$", "", arxiv)
    if doi:
        return "doi:" + doi
    if isinstance(item.get("cluster"), str) and item["cluster"] == ts.registrable_domain(item["url"]):
        return ts.origin(item["url"])
    return item.get("cluster")


def check_items(run_dir, items, offline, dbs):
    """Attach item['check'] to every item: lint first, then one citation_verifier pass.

    The verifier sees each distinct URL once (reachability, empty quote) and each distinct
    DOI/arXiv pair once; the quote match comes from the lint's cached-page match.
    """
    records, pending = {}, []
    for it in items:
        reason, qm = lint_item(run_dir, it, dbs)
        if reason:
            it["check"] = {"status": "fail", "quote_match": qm or "n/a", "detail": reason}
            continue
        keys = []
        if not it.get("paper"):  # a paper item has no page to reach
            keys.append("U:" + it["url"])
            records.setdefault(keys[-1], {"url": it["url"]})
        if it.get("doi") or it.get("arxiv_id"):
            keys.append(f"D:{it.get('doi')}|{it.get('arxiv_id')}")
            records.setdefault(keys[-1], {"url": "", "doi": it.get("doi"), "arxiv_id": it.get("arxiv_id")})
        pending.append((it, qm, keys))
    results = {}
    if records:
        recs = [{"id": k, "verbatim_quote": "", "source": src} for k, src in records.items()]
        out = cv.run({"evidence": recs}, None, cv.DEFAULT_TIMEOUT, offline,
                     pages_dir=os.path.join(run_dir, "pages"))
        results = {r["id"]: r for r in out["results"]}
    for it, qm, keys in pending:
        sev = "PASS"
        for k in keys:
            sev = cv.bump(sev, results[k]["severity"])
        # the pass sends an empty quote; the lint already matched the real one
        detail = " / ".join(re.sub(r"( / )?quote: no verbatim_quote", "", results[k]["detail"])
                            for k in keys) or "paper abstract matched"
        it["check"] = {"status": {"PASS": "pass", "WARN": "warn", "CRITICAL": "fail"}[sev],
                       "quote_match": qm, "detail": detail}


def append(run_dir, path, offline):
    """Add the items of FILE to evidence.jsonl after the current maximum id; others keep theirs.

    An item already in evidence.jsonl (same url and quote) is skipped, so a rerun adds nothing.
    """
    ev_path = os.path.join(run_dir, "evidence.jsonl")
    old = [it for _, it, _ in read_jsonl(ev_path) if it]
    seen = {(it.get("url"), it.get("quote")) for it in old}
    next_id = max([int(it["id"][1:]) for it in old] + [0]) + 1
    new, lines = [], []
    for k, item, err in read_jsonl(path):
        if err:
            lines.append(f"line {k}: {err}")
        elif (item.get("url"), item.get("quote")) not in seen:
            seen.add((item.get("url"), item.get("quote")))
            item["id"] = f"E{next_id}"
            next_id += 1
            new.append(item)
    check_items(run_dir, new, offline, {})
    for it in new:
        if isinstance(it.get("url"), str):
            it["cluster"] = item_cluster(it)
    with open(ev_path, "a", encoding="utf-8") as f:
        for it in new:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    everything = old + new
    for sq in dict.fromkeys(it.get("sq") for it in new):
        write_digest(run_dir, sq, [it for it in everything if it.get("sq") == sq])
    lines += [f"{it['id']} {it['check']['status']}: {it['check']['detail'][:160]}" for it in new]
    print("\n".join(lines) or "nothing new to add")
    return 1 if any(it["check"]["status"] == "fail" for it in new) or any(
        l.startswith("line ") for l in lines) else 0


def merge(run_dir, only, offline):
    files, bad_files = collector_files(run_dir, only)
    if not files:
        print("error: no collect/SQ*_*.jsonl files to merge", file=sys.stderr)
        return 2
    dbs = {}
    ev_path = os.path.join(run_dir, "evidence.jsonl")
    old = [it for _, it, _ in read_jsonl(ev_path) if it] if only and os.path.exists(ev_path) else []
    next_id = max([int(it["id"][1:]) for it in old] + [0]) + 1

    items, shape_fail = [], []
    for path in files:
        for k, item, err in read_jsonl(path):
            if err:
                shape_fail.append((os.path.basename(path), k, err))
                continue
            err = file_sq_error(path, item)
            if err:
                shape_fail.append((os.path.basename(path), k, err))
                continue
            item["id"] = f"E{next_id}"
            next_id += 1
            items.append(item)
    check_items(run_dir, items, offline, dbs)
    for it in items:
        if isinstance(it.get("url"), str):
            it["cluster"] = item_cluster(it)

    ordered = [it for it in old if it.get("sq") != only] + items
    with open(ev_path, "w", encoding="utf-8") as f:
        for it in ordered:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

    nums = {m.group(1) for m in (FILE_RE.match(os.path.basename(p)) for p in
                                 glob.glob(os.path.join(run_dir, "collect", "SQ*_*.jsonl"))) if m}
    try:
        with open(os.path.join(run_dir, "brief.md"), encoding="utf-8") as f:
            nums |= set(re.findall(r"^\s*-\s*SQ(\d+):", f.read(), re.M))
    except OSError:
        pass
    sqs = [f"SQ{n}" for n in sorted(nums, key=int)]
    for sq in sqs if only is None else [only]:
        write_digest(run_dir, sq, [it for it in ordered if it.get("sq") == sq])
    failed = [{"id": it["id"], "reason": it["check"]["detail"]} for it in ordered
              if it["check"]["status"] == "fail"]
    failed += [{"id": f"{name}:line {k}", "reason": err} for name, k, err in shape_fail]
    failed += [{"id": name, "reason": "file name does not match SQ{n}_web.jsonl or SQ{n}_academic.jsonl"}
               for name in bad_files]
    if only:  # shape failures of the other sub-questions stay from the earlier run
        prev = load_json(os.path.join(run_dir, "gaps.json"), {}).get("failed", [])
        listed = {f_["id"] for f_ in failed}
        failed += [f_ for f_ in prev if not f_["id"].startswith("E")
                   and not f_["id"].startswith(only + "_") and f_["id"] not in listed]
    empty = [sq for sq in sqs if not any(it.get("sq") == sq and it["check"]["status"] != "fail"
                                         for it in ordered)]
    with open(os.path.join(run_dir, "gaps.json"), "w", encoding="utf-8") as f:
        json.dump({"empty_sq": empty, "failed": failed}, f, ensure_ascii=False, indent=2)

    summary = []
    for sq in sqs:
        its = [it for it in ordered if it.get("sq") == sq]
        n = {s: sum(1 for it in its if it["check"]["status"] == s) for s in ("pass", "warn", "fail")}
        clusters = {it["cluster"] for it in its if it["check"]["status"] != "fail"}
        summary.append(f"{sq}: pass {n['pass']}, warn {n['warn']}, fail {n['fail']}, "
                       f"independent clusters {len(clusters)}")
    room = max(MAX_LINES - len(summary) - 1, 0)
    summary += [f"fail {f_['id']}: {f_['reason'][:160]}" for f_ in failed[:room]]
    if len(failed) > room:
        summary.append(f"... and {len(failed) - room} more failures (see gaps.json)")
    print("\n".join(summary[:MAX_LINES]))
    return 0


def main():
    _configure_stdout()
    ap = argparse.ArgumentParser(description="Lint collector files and merge them into evidence.jsonl.")
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--lint", metavar="FILE", help="shape-check one collector file; no network")
    ap.add_argument("--only", metavar="SQn", help="re-run the merge for one sub-question")
    ap.add_argument("--append", metavar="FILE",
                    help="check the items of FILE and add them after the highest evidence id")
    ap.add_argument("--offline", action="store_true", help="no network (tests)")
    args = ap.parse_args()
    args.only = args.only.upper() if args.only else None
    if not os.path.isdir(args.run_dir):
        print(f"error: no such run directory: {args.run_dir}", file=sys.stderr)
        return 2
    try:
        if args.lint:
            return run_lint(args.run_dir, args.lint)
        if args.append:
            return append(args.run_dir, args.append, args.offline)
        return merge(args.run_dir, args.only, args.offline)
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
