"""
Query-level bootstrap confidence intervals (replaces the underpowered n=3
Friedman/paired-t analysis the reviewer criticized).

For each dataset, per-query metric values (50 queries) come from the validated
exact-L2 rankings under a chosen qrels variant. We compute:
  - percentile bootstrap 95% CIs per model per metric (B resamples over queries);
  - paired bootstrap of M5-vs-others MAP@10 differences (difference CI + two-sided
    bootstrap p-value), the query-level inference the reviewer asked for;
  - a pooled-across-datasets CI over all 150 queries for the aggregate MAP@10.

No LLM required. Works for frozen or pooled qrels via --variant.

Outputs: datasets/<name>/analysis/bootstrap_<variant>.json and
results_reanalysis/bootstrap_<variant>.json (combined).
"""
import os
import sys
import json
import argparse

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_ROOT, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np  # noqa: E402
import common as C  # noqa: E402
import config as cfg  # noqa: E402
from query_level_eval import score_dataset  # noqa: E402

B = 10000
ALPHA = 0.05


def qrels_path(dataset, variant):
    if variant == "frozen":
        return os.path.join(C.REPO_ROOT, "datasets", dataset, "qrels.tsv")
    return os.path.join(C.REPO_ROOT, "datasets", dataset, "analysis", f"qrels_{variant}.tsv")


def ci(values, rng):
    v = np.asarray(values, dtype=float)
    n = len(v)
    idx = rng.integers(0, n, size=(B, n))
    means = v[idx].mean(axis=1)
    lo, hi = np.percentile(means, [100 * ALPHA / 2, 100 * (1 - ALPHA / 2)])
    return float(v.mean()), float(lo), float(hi)


def paired(a, b, rng):
    d = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    n = len(d)
    idx = rng.integers(0, n, size=(B, n))
    md = d[idx].mean(axis=1)
    lo, hi = np.percentile(md, [100 * ALPHA / 2, 100 * (1 - ALPHA / 2)])
    p = 2.0 * min((md <= 0).mean(), (md >= 0).mean())
    return float(d.mean()), float(lo), float(hi), float(min(p, 1.0))


def run(variant):
    rng = C.rng()
    combined = {"variant": variant, "B": B, "datasets": {}, "pooled_150": {}}
    pooled_pq = {lab: [] for lab in [f"M{i}" for i in range(1, 6)]}

    for ds in C.DATASETS:
        scored = score_dataset(ds, qrels_path(ds, variant))
        labels = sorted(scored.keys())
        ds_out = {"n_queries": len(scored[labels[0]]["qids"]), "ci": {}, "paired_map_vs_M5": {}}
        for lab in labels:
            ds_out["ci"][lab] = {}
            for metric in C.METRICS:
                mean, lo, hi = ci(scored[lab]["per_query"][metric], rng)
                ds_out["ci"][lab][metric] = {"mean": mean, "lo": lo, "hi": hi}
            pooled_pq[lab].extend(scored[lab]["per_query"]["map"])
        # paired MAP@10: M5 vs each other model
        m5 = scored["M5"]["per_query"]["map"]
        for lab in labels:
            if lab == "M5":
                continue
            dmean, lo, hi, p = paired(m5, scored[lab]["per_query"]["map"], rng)
            ds_out["paired_map_vs_M5"][lab] = {"delta": dmean, "lo": lo, "hi": hi, "p": p}
        combined["datasets"][ds] = ds_out
        adir = C.analysis_dir(ds)
        with open(os.path.join(adir, f"bootstrap_{variant}.json"), "w", encoding="utf-8") as f:
            json.dump(ds_out, f, indent=2)

    # pooled across all 150 queries: aggregate MAP@10 CI + paired
    for lab, vals in pooled_pq.items():
        mean, lo, hi = ci(vals, rng)
        combined["pooled_150"].setdefault("ci_map", {})[lab] = {"mean": mean, "lo": lo, "hi": hi}
    for lab in pooled_pq:
        if lab == "M5":
            continue
        dmean, lo, hi, p = paired(pooled_pq["M5"], pooled_pq[lab], rng)
        combined["pooled_150"].setdefault("paired_map_vs_M5", {})[lab] = {
            "delta": dmean, "lo": lo, "hi": hi, "p": p}

    out_dir = os.path.join(C.REPO_ROOT, "results_reanalysis")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f"bootstrap_{variant}.json"), "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2)

    # console summary
    print(f"\n=== BOOTSTRAP CIs ({variant}, B={B}) ===")
    for ds, d in combined["datasets"].items():
        print(f"\n{ds} (n={d['n_queries']}):  MAP@10 mean [95% CI]")
        for lab in sorted(d["ci"]):
            m = d["ci"][lab]["map"]
            print(f"  {lab}: {m['mean']:.4f} [{m['lo']:.4f}, {m['hi']:.4f}]")
        print(f"  paired MAP@10 (M5 - X): delta [95% CI] p")
        for lab, pr in d["paired_map_vs_M5"].items():
            print(f"    M5-{lab}: {pr['delta']:+.4f} [{pr['lo']:+.4f}, {pr['hi']:+.4f}] p={pr['p']:.3f}")
    print(f"\nPOOLED over 150 queries: aggregate MAP@10 mean [95% CI]")
    for lab in sorted(combined["pooled_150"]["ci_map"]):
        m = combined["pooled_150"]["ci_map"][lab]
        print(f"  {lab}: {m['mean']:.4f} [{m['lo']:.4f}, {m['hi']:.4f}]")
    print("  paired MAP@10 (M5 - X) over 150: delta [95% CI] p")
    for lab, pr in combined["pooled_150"]["paired_map_vs_M5"].items():
        print(f"    M5-{lab}: {pr['delta']:+.4f} [{pr['lo']:+.4f}, {pr['hi']:+.4f}] p={pr['p']:.3f}")
    print(f"\nsaved -> results_reanalysis/bootstrap_{variant}.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="frozen", choices=["frozen", "pooled", "pooled_forced"])
    run(ap.parse_args().variant)


if __name__ == "__main__":
    main()
