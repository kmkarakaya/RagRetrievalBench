"""
Frozen-snapshot bootstrap CLI for the alternative qrels variants.

The uncertainty computation itself is a pipeline stage and lives in
utils/bootstrap_utils.py; `python rag_benchmark.py --bootstrap --dataset <name>`
is the normal way to run it, and the dataset report renders its output.

This script exists only for the snapshot-specific question the reviewer revision
needed: how the same rankings score under a *different qrels construction*
(`qrels_pooled.tsv` / `qrels_pooled_forced.tsv`, built by pooled_qrels.py). It runs
the shared stage once per dataset per variant and additionally reports the pooled
across-dataset aggregate.

Because the resampling is seeded per (dataset, model, metric) rather than by call
order, every variant draws the same resample indices, so differences between
variants are attributable to the qrels and not to Monte Carlo noise.

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

import common as C  # noqa: E402
from utils import bootstrap_utils as bs  # noqa: E402


def qrels_path(dataset, variant):
    if variant == "frozen":
        return os.path.join(C.REPO_ROOT, "datasets", dataset, "qrels.tsv")
    return os.path.join(C.REPO_ROOT, "datasets", dataset, "analysis", f"qrels_{variant}.tsv")


def zero_marker(pr):
    return "  [excludes 0]" if bs.excludes_zero(pr) else "  [includes 0]"


def run(variant):
    B, alpha, seed = bs._settings()
    combined = {"variant": variant, "B": B, "seed": seed, "datasets": {}, "pooled": {}}
    per_dataset_vectors = {}

    for ds in C.DATASETS:
        scored = bs.score_dataset(ds, qrels_path(ds, variant))
        block = bs.compute_dataset_bootstrap(ds, scored=scored, B=B, alpha=alpha, seed=seed)
        block["B"] = B
        block["confidence"] = round(1.0 - alpha, 4)
        block["seed"] = seed
        combined["datasets"][ds] = block
        per_dataset_vectors[ds] = {
            lab: scored[lab]["per_query"][bs.PRIMARY_METRIC] for lab in scored
        }
        with open(bs.bootstrap_output_path(ds, variant), "w", encoding="utf-8") as f:
            json.dump(block, f, indent=2)

    combined["pooled"] = bs.compute_pooled_bootstrap(
        per_dataset_vectors, B=B, alpha=alpha, seed=seed)

    out_dir = os.path.join(C.REPO_ROOT, "results_reanalysis")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f"bootstrap_{variant}.json"), "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2)

    print(f"\n=== BOOTSTRAP CIs ({variant}, B={B}, seed={seed}) ===")
    for ds, d in combined["datasets"].items():
        leader = d["leader"]
        print(f"\n{ds} (n={d['n_queries']}, leader {leader}):  MAP@10 mean [95% CI]")
        for lab in sorted(d["ci"]):
            m = d["ci"][lab][bs.PRIMARY_METRIC]
            print(f"  {lab}: {m['mean']:.4f} [{m['lo']:.4f}, {m['hi']:.4f}]")
        print(f"  paired MAP@10 (leader {leader} - X): delta [95% CI] p")
        for lab, pr in d["paired_map_vs_leader"].items():
            print(f"    {leader}-{lab}: {pr['delta']:+.4f} [{pr['lo']:+.4f}, {pr['hi']:+.4f}] "
                  f"p={pr['p']:.3f}{zero_marker(pr)}")

    pooled = combined["pooled"]
    print(f"\nPOOLED over {pooled['n_queries']} queries (unstratified): "
          f"aggregate MAP@10 mean [95% CI]")
    for lab in sorted(pooled["ci_map"]):
        m = pooled["ci_map"][lab]
        print(f"  {lab}: {m['mean']:.4f} [{m['lo']:.4f}, {m['hi']:.4f}]")
    pldr = pooled["leader"]
    print(f"  paired MAP@10 (leader {pldr} - X): delta [95% CI] p")
    for lab, pr in pooled["paired_map_vs_leader"].items():
        print(f"    {pldr}-{lab}: {pr['delta']:+.4f} [{pr['lo']:+.4f}, {pr['hi']:+.4f}] "
              f"p={pr['p']:.3f}{zero_marker(pr)}")
    print(f"\nsaved -> results_reanalysis/bootstrap_{variant}.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="frozen", choices=["frozen", "pooled", "pooled_forced"])
    run(ap.parse_args().variant)


if __name__ == "__main__":
    main()
