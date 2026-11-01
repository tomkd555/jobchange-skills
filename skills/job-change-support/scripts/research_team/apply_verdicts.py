#!/usr/bin/env python3
"""apply_verdicts.py - merge the verifiers' verdicts and build the patch list (research-team 2.0).

Used in research-team Step 5.5, after every verifier has written claims/verdicts_{k}.json.
Standard library only, no network.

Example:
    python apply_verdicts.py --run-dir research/20261024-topic

Reads every claims/batch_*.json and claims/verdicts_*.json and writes verdicts.json:
    {"verdicts": [{"cid", "sentence", "evidence_ids", "verdict", "reason", "found", "source"}],
     "patch": [{"cid", "sentence", "verdict", "action", "reason", "found", "source"}]}
A batch claim with no verdict, a verdict for an unknown cid, a duplicate cid, an unknown
verdict value or an entry that is not a JSON object is an error: the errors are listed and
nothing is written. Prints the counts per verdict and, per patch, the whole sentence, the
reason and the found passage.

Exit codes: 0 = written / 1 = errors in the verdicts / 2 = usage or I/O error
"""

import argparse
import collections
import glob
import json
import os
import sys

VERDICTS = ("supported", "partial", "unsupported", "contradicted")
ACTIONS = {
    "partial": "narrow the sentence to what the quote supports",
    "unsupported": "remove the sentence or replace its support with a passing item",
    "contradicted": "state both sources",
}


def _configure_stdout():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def load_all(pattern):
    """Return ([(file name, object)], [error]) for every file matching pattern."""
    rows, bad = [], []
    for path in sorted(glob.glob(pattern)):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}: {exc}")
        if not isinstance(data, list):
            raise ValueError(f"{path}: expected a JSON list")
        name = os.path.basename(path)
        for n, item in enumerate(data, 1):
            if isinstance(item, dict):
                rows.append((name, item))
            else:
                bad.append(f"{name}: item {n} is not a JSON object")
    return rows, bad


def main():
    _configure_stdout()
    ap = argparse.ArgumentParser(description="Merge verifier verdicts into verdicts.json.")
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()
    claims_dir = os.path.join(args.run_dir, "claims")
    try:
        claim_rows, claim_bad = load_all(os.path.join(claims_dir, "batch_*.json"))
        given_rows, given_bad = load_all(os.path.join(claims_dir, "verdicts_*.json"))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    claims = [c for _, c in claim_rows]
    batch_of = {c["cid"]: name for name, c in claim_rows}
    given = [v for _, v in given_rows]
    by_cid = {c["cid"]: c for c in claims}
    errors, seen = claim_bad + given_bad + [
        f"{cid}: appears in more than one batch" for cid, n in
        collections.Counter(c["cid"] for c in claims).items() if n > 1], {}
    for v in given:
        cid = v.get("cid")
        if cid not in by_cid:
            errors.append(f"verdict for unknown cid {cid!r}")
        elif cid in seen:
            errors.append(f"{cid}: more than one verdict")
        elif v.get("verdict") not in VERDICTS:
            errors.append(f"{cid}: unknown verdict value {v.get('verdict')!r}")
        else:
            seen[cid] = v
    errors += [f"{cid}: no verdict (claim in {batch_of[cid]})" for cid in by_cid if cid not in seen
               and not any(v.get("cid") == cid for v in given)]
    if errors:
        print("\n".join(errors))
        return 1

    verdicts, patch = [], []
    for c in claims:
        v = seen[c["cid"]]
        verdicts.append({"cid": c["cid"], "sentence": c["sentence"],
                         "evidence_ids": [e["id"] for e in c["evidence"]],
                         "verdict": v["verdict"], "reason": v.get("reason", ""),
                         "found": v.get("found", ""), "source": v.get("source", "")})
        if v["verdict"] != "supported":
            patch.append({"cid": c["cid"], "sentence": c["sentence"], "verdict": v["verdict"],
                          "action": ACTIONS[v["verdict"]], "reason": v.get("reason", ""),
                          "found": v.get("found", ""), "source": v.get("source", "")})
    try:
        with open(os.path.join(args.run_dir, "verdicts.json"), "w", encoding="utf-8") as f:
            json.dump({"verdicts": verdicts, "patch": patch}, f, ensure_ascii=False, indent=2)
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(", ".join(f"{n} {sum(1 for v in verdicts if v['verdict'] == n)}" for n in VERDICTS))
    for p in patch:
        print(f"{p['cid']} {p['verdict']}: {p['action']}")
        print(f"  sentence: {p['sentence']}")
        print(f"  reason: {p['reason']}")
        print(f"  found: {p['found']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
