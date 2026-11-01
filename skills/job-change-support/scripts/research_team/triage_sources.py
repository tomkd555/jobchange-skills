#!/usr/bin/env python3
"""triage_sources.py - sort candidate URLs deterministically before fetching them.

Used by the research-team collectors, between WebSearch and fetch_page.py. It does
three things, all decidable from the URL alone.

1. Group by registrable domain and assign a provisional origin_cluster
   (one publisher is one origin)
2. Derive an expected source grade (grade_hint) from the domain: A for governments,
   international organisations and journals; B for industry bodies, research firms and
   preprint servers; C for everything else
3. Rank by that grade and drop the second and later URL of the same cluster from the fetch
   list (a second page of one publisher adds no independent source)

grade_hint is an expectation only. The grade that goes on an evidence unit is the
collection agent's call after reading the page, following research-collector.md. This script only decides what
to read first. The origin_cluster it assigns is provisional too; merging clusters across
fragments belongs to the orchestrator.

Examples:
    python triage_sources.py --prefix SQ1 https://www.e-stat.go.jp/x https://example.com/blog
    python triage_sources.py --prefix SQ2 --json --input candidates.txt

Exit codes: 0 = there is something to fetch / 1 = nothing to fetch (all duplicates, or no
candidates) / 2 = usage error
"""

import argparse
import json
import re
import sys
import urllib.parse

# Multi-label public suffixes. Anything not listed falls back to the last two labels.
MULTI_SUFFIX = {
    "co.jp", "ne.jp", "or.jp", "go.jp", "ac.jp", "ad.jp", "ed.jp", "gr.jp", "lg.jp",
    "co.uk", "ac.uk", "gov.uk", "org.uk", "com.au", "gov.au", "edu.au",
    "co.kr", "go.kr", "com.cn", "gov.cn", "com.br", "gov.br", "co.in", "gov.in",
    "com.sg", "gov.sg", "com.hk", "gov.hk", "com.tw", "gov.tw",
}

# Grade A: governments, international organisations, peer-reviewed publishers, academic infrastructure
GRADE_A_SUFFIX = (".go.jp", ".lg.jp", ".ac.jp", ".gov", ".mil", ".edu", ".gov.uk", ".int")
GRADE_A_DOMAIN = {
    "oecd.org", "worldbank.org", "imf.org", "who.int", "un.org", "europa.eu", "eurostat.ec.europa.eu",
    "bis.org", "ilo.org", "unesco.org", "iea.org", "doi.org", "ncbi.nlm.nih.gov",
    "pubmed.ncbi.nlm.nih.gov", "nature.com", "science.org", "sciencedirect.com", "springer.com",
    "link.springer.com", "wiley.com", "onlinelibrary.wiley.com", "tandfonline.com", "cell.com",
    "thelancet.com", "bmj.com", "nejm.org", "acm.org", "ieee.org", "jstage.jst.go.jp",
}
# Grade B: industry bodies, corporate IR, research firms, consulting firms, preprint servers
GRADE_B_SUFFIX = (".or.jp", ".gr.jp")
GRADE_B_DOMAIN = {
    "gartner.com", "idc.com", "forrester.com", "statista.com", "mckinsey.com", "bcg.com",
    "bain.com", "deloitte.com", "pwc.com", "kpmg.com", "ey.com", "accenture.com",
    "nri.com", "mri.co.jp", "jri.co.jp", "dir.co.jp", "yano.co.jp", "fuji-keizai.co.jp",
    "idcjapan.co.jp", "impress.co.jp", "itr.co.jp",
    "arxiv.org", "biorxiv.org", "ssrn.com",
}
# Paths on a corporate site that mark the publisher's own announcement or IR material (grade B)
GRADE_B_PATH = re.compile(r"/(ir|investor|investors|press|news|newsroom|release|pdf/ir)(/|$)", re.I)

GRADE_ORDER = {"A": 0, "B": 1, "C": 2}

# Hosts where an account, named by the first path segment, is the publisher
ACCOUNT_PATH_HOSTS = {"github.com", "gitlab.com", "medium.com", "note.com", "qiita.com", "zenn.dev",
                      "dev.to", "huggingface.co"}
# Domains that give each account its own subdomain
ACCOUNT_SUBDOMAIN_DOMAINS = {"github.io", "substack.com", "blogspot.com", "wordpress.com",
                             "hatenablog.com", "hatenablog.jp", "medium.com"}
ARXIV_PATH_RE = re.compile(r"^/(?:abs|pdf)/([^/?#]+?)(?:v\d+)?(?:\.pdf)?/?$", re.I)


def registrable_domain(url):
    """Return the registrable domain of a URL (www. dropped), or "" when undecidable."""
    host = (urllib.parse.urlsplit(url).hostname or "").lower()
    if not host:
        return ""
    host = host[4:] if host.startswith("www.") else host
    labels = host.split(".")
    if len(labels) <= 2:
        return host
    if ".".join(labels[-2:]) in MULTI_SUFFIX:
        return ".".join(labels[-3:])
    return ".".join(labels[-2:])


def origin(url):
    """Return the independence cluster of a URL: a paper by its arXiv id or DOI, a platform
    account by its account, any other page by its registrable domain."""
    parts = urllib.parse.urlsplit(url)
    host = (parts.hostname or "").lower()
    host = host[4:] if host.startswith("www.") else host
    domain = registrable_domain(url)
    m = ARXIV_PATH_RE.match(parts.path or "") if domain == "arxiv.org" else None
    if m:
        return "arxiv:" + m.group(1).lower()
    if domain == "doi.org" and parts.path.strip("/"):
        return "doi:" + urllib.parse.unquote(parts.path.strip("/")).lower()
    if domain in ACCOUNT_SUBDOMAIN_DOMAINS and host != domain:
        return host
    segment = (parts.path or "").strip("/").split("/")[0]
    if host in ACCOUNT_PATH_HOSTS and segment:
        return f"{host}/{segment.lower()}"
    return domain


def grade_hint(url):
    """Return (grade, reason): the source grade expected from the URL alone."""
    parts = urllib.parse.urlsplit(url)
    host = (parts.hostname or "").lower()
    domain = registrable_domain(url)
    if host.endswith(GRADE_A_SUFFIX) or domain in GRADE_A_DOMAIN or host in GRADE_A_DOMAIN:
        return "A", "government, international organisation or academic-infrastructure domain"
    if host.endswith(GRADE_B_SUFFIX) or domain in GRADE_B_DOMAIN:
        return "B", "industry body, research firm or consulting firm domain"
    if GRADE_B_PATH.search(parts.path or ""):
        return "B", "the publisher's own announcement or IR path"
    return "C", "none of the above (trade media, blog or secondary source)"


def triage(urls, prefix):
    """Sort the candidate URLs. Returns the result dict."""
    clusters, order = {}, []
    rows = []
    for url in dict.fromkeys(urls):  # drop repeated URLs first
        domain = registrable_domain(url)
        if not domain:
            rows.append({"url": url, "domain": "", "cluster": None, "grade_hint": "C",
                         "reason": "no host in the URL", "duplicate": True})
            continue
        key = origin(url)
        if key not in clusters:
            order.append(key)
            clusters[key] = f"{prefix}-{len(order)}"
        grade, reason = grade_hint(url)
        rows.append({"url": url, "domain": domain, "cluster": clusters[key],
                     "grade_hint": grade, "reason": reason, "duplicate": False})

    seen_clusters = set()
    # by expected grade, then by input order (read what you found first, first)
    ranked = [r for _, r in sorted(enumerate(rows),
                                   key=lambda p: (GRADE_ORDER[p[1]["grade_hint"]], p[0]))]
    for r in ranked:
        if r["duplicate"]:
            continue
        if r["cluster"] in seen_clusters:
            r["duplicate"] = True
            r["reason"] += "; an earlier URL shares this cluster (it adds no second independent source)"
        else:
            seen_clusters.add(r["cluster"])

    fetch_order = [r["url"] for r in ranked if not r["duplicate"]]
    notes = []
    if fetch_order and all(r["grade_hint"] == "C" for r in ranked if not r["duplicate"]):
        notes.append("every candidate to fetch is expected to be grade C, which cannot carry a "
                     "key figure; run a primary-source search first (allowed_domains)")
    if len(seen_clusters) < 3:
        notes.append(f"only {len(seen_clusters)} independent cluster(s), short of the floor for "
                     "independent sources; add a search along a different line")
    return {"prefix": prefix, "candidates": len(rows), "clusters": len(seen_clusters),
            "fetch_order": fetch_order, "ranked": ranked, "notes": notes}


def main():
    parser = argparse.ArgumentParser(
        description="Rank candidate URLs before fetching and assign provisional origin_cluster")
    parser.add_argument("urls", nargs="*", help="candidate URLs")
    parser.add_argument("--prefix", required=True,
                        help="prefix for the provisional origin_cluster (the assigned SQ, e.g. SQ1)")
    parser.add_argument("--input", help="file of candidate URLs, one per line (# lines ignored)")
    parser.add_argument("--json", action="store_true", help="print JSON")
    args = parser.parse_args()

    urls = list(args.urls)
    if args.input:
        try:
            with open(args.input, encoding="utf-8") as f:
                urls += [l.strip() for l in f if l.strip() and not l.startswith("#")]
        except OSError as e:
            print(f"error: cannot read the candidate file: {e}", file=sys.stderr)
            return 2
    if not urls:
        print("error: no candidate URLs", file=sys.stderr)
        return 2

    result = triage(urls, args.prefix)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for r in result["ranked"]:
            mark = "skip " if r["duplicate"] else "fetch"
            print(f"[{mark}] {r['grade_hint']} {r['cluster'] or '-'} {r['url']}\n"
                  f"        {r['reason']}")
        print(f"{len(result['fetch_order'])} to fetch / {result['clusters']} independent clusters")
        for n in result["notes"]:
            print(f"  note: {n}")

    return 0 if result["fetch_order"] else 1


if __name__ == "__main__":
    sys.exit(main())
