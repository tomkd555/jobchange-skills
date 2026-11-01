#!/usr/bin/env python3
"""select_claims.py - pick the cited sentences of report.md for independent verification.

Used in research-team Step 5.3, before the verifiers start. Standard library only, no network.

Example:
    python select_claims.py --run-dir research/20261024-topic --cap 10

Candidates are the sentences (a list item or a table row is one sentence) of report.md that
carry a marker. Evidence ids missing from evidence.jsonl or with check status fail are dropped;
a sentence left with no evidence is skipped and printed. Order: the sentences that match a
"priority" sentence of screen.json (when it exists; markers removed, difflib ratio 0.8 or
more), then sentences under "## Answer", then sentences with a digit, then the rest, each
group in report order. The
list is cut at --cap and written as claims/batch_{k}.json, 5 claims per file, each claim with
its evidence quotes, urls and page paths ("page" is a cached page, or abstracts/{id}.txt for
a paper item whose abstract is in collect/papers_{sq}.json, else null). Removes the batches and
verdicts of an earlier run, verdicts.json included. Prints the batch paths and the number of
candidates the cap dropped.

Exit codes: 0 = batches written / 2 = usage or I/O error
"""

import argparse
import difflib
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import citation_verifier as cv  # noqa: E402
import report_check as rc  # noqa: E402

BATCH_SIZE = 5
SIMILAR = 0.8  # difflib ratio at which a report sentence counts as a screen priority sentence


def paper_abstract(run_dir, e):
    """The abstract of a paper item from its collector db, or None."""
    if not e.get("paper") or not e.get("sq"):
        return None
    try:
        with open(os.path.join(run_dir, "collect", f"papers_{e['sq']}.json"), encoding="utf-8") as f:
            for rec in json.load(f).get("papers", []):
                if rec.get("id") == e["paper"]:
                    return rec.get("abstract") or None
    except (OSError, ValueError, AttributeError):
        pass
    return None


def plain(sentence):
    """The sentence with each marker and the whitespace before it removed, spaces collapsed."""
    return re.sub(r"\s+", " ", re.sub(r"\s*" + rc.MARKER, "", sentence)).strip()


def screen_priority(run_dir):
    """The priority sentences of screen.json in plain form, or [] when there is no screen."""
    try:
        with open(os.path.join(run_dir, "screen.json"), encoding="utf-8") as f:
            return [plain(s) for s in json.load(f).get("priority", [])]
    except OSError:
        return []


def flagged(sentence, priority):
    # a writer may reword a flagged sentence while citing it, so the match is by similarity
    p = plain(sentence)
    return any(difflib.SequenceMatcher(None, p, q).ratio() >= SIMILAR for q in priority)


def main():
    rc._configure_stdout()
    ap = argparse.ArgumentParser(description="Select cited report sentences for verification.")
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--cap", type=int, required=True, help="most claims to verify (10 STANDARD, 25 DEEP)")
    args = ap.parse_args()
    try:
        with open(os.path.join(args.run_dir, "report.md"), encoding="utf-8") as f:
            report = f.read()
        evidence = {e["id"]: e for e in rc.read_jsonl(os.path.join(args.run_dir, "evidence.jsonl"))}

        cited, skipped = [], []
        for sec, s in rc.report_sentences(report):
            ids = list(dict.fromkeys(rc.marker_ids(s)))
            if not ids:
                continue
            # a missing or failed item is a dangling marker that report_check rejects later
            if any(i in evidence and evidence[i].get("check", {}).get("status") != "fail" for i in ids):
                cited.append((sec, s))
            else:
                skipped.append(s)
        priority = screen_priority(args.run_dir)
        first = [s for _, s in cited if flagged(s, priority)]
        cited = [(sec, s) for sec, s in cited if s not in first]
        answer = [s for sec, s in cited if sec == "## Answer"]
        rest = [(sec, s) for sec, s in cited if sec != "## Answer"]
        ordered = first + answer + [s for _, s in rest if rc.has_digit_outside_marker(s)] \
            + [s for _, s in rest if not rc.has_digit_outside_marker(s)]
        chosen = ordered[:max(args.cap, 0)]

        claims = []
        for n, s in enumerate(chosen, 1):
            ev = []
            for i in dict.fromkeys(rc.marker_ids(s)):
                e = evidence.get(i)
                if e is None or e.get("check", {}).get("status") == "fail":
                    continue
                # the cache file name derives from the url; index.json can lose entries
                name = cv.cache_name(e["url"])
                cached = os.path.exists(os.path.join(args.run_dir, "pages", name))
                page = None if e.get("paper") or not cached else "pages/" + name
                abstract = paper_abstract(args.run_dir, e)
                if abstract:
                    page = f"abstracts/{i}.txt"
                    os.makedirs(os.path.join(args.run_dir, "abstracts"), exist_ok=True)
                    with open(os.path.join(args.run_dir, page), "w", encoding="utf-8") as f:
                        f.write(abstract)
                ev.append({"id": i, "quote": e["quote"], "url": e["url"], "page": page})
            claims.append({"cid": f"C{n}", "sentence": s, "evidence": ev})

        os.makedirs(os.path.join(args.run_dir, "claims"), exist_ok=True)
        # a rerun must not leave batches or verdicts of an earlier report behind
        old_files = [os.path.join(args.run_dir, "verdicts.json")]
        for pattern in ("batch_*.json", "verdicts_*.json"):
            old_files += glob.glob(os.path.join(args.run_dir, "claims", pattern))
        for old in old_files:
            if os.path.exists(old):
                os.remove(old)
        paths = []
        for k in range(0, len(claims), BATCH_SIZE):
            path = os.path.join(args.run_dir, "claims", f"batch_{k // BATCH_SIZE + 1}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(claims[k:k + BATCH_SIZE], f, ensure_ascii=False, indent=2)
            paths.append(path)
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print("\n".join(paths))
    for s in skipped:
        print(f"skipped (no usable evidence): {s}")
    print(f"{len(claims)} claims in {len(paths)} batches; {len(ordered) - len(chosen)} candidates "
          "dropped by the cap")
    if priority:
        print(f"{sum(1 for s in chosen if s in first)} screen priority sentences within the cap")
    return 0


if __name__ == "__main__":
    sys.exit(main())
