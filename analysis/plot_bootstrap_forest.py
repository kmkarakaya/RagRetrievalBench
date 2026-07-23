"""
Forest plot of the query-level bootstrap analysis (A14 uncertainty display).

Reads results_reanalysis/bootstrap_frozen.json (pooled-150 aggregate MAP@10 with
95% percentile bootstrap CIs) and writes a publication-style forest plot to
journal_paper/results_bootstrap_forest.png. Models are ordered by mean MAP@10;
M5 is highlighted. Wide, overlapping CIs are exactly the point the figure makes.
"""
import os
import sys
import json

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SRC = os.path.join(_ROOT, "results_reanalysis", "bootstrap_frozen.json")
OUT = os.path.join(_ROOT, "journal_paper", "results_bootstrap_forest.png")


def main():
    ci = json.load(open(SRC, encoding="utf-8"))["pooled_150"]["ci_map"]
    # order by mean descending
    order = sorted(ci, key=lambda k: -ci[k]["mean"])
    means = [ci[m]["mean"] for m in order]
    los = [ci[m]["lo"] for m in order]
    his = [ci[m]["hi"] for m in order]
    y = list(range(len(order)))[::-1]  # top row = best

    fig, ax = plt.subplots(figsize=(6.2, 3.3))
    for yi, m, mean, lo, hi in zip(y, order, means, los, his):
        color = "#b2182b" if m == "M5" else "#2166ac"
        ax.errorbar(mean, yi, xerr=[[mean - lo], [hi - mean]], fmt="o",
                    color=color, ecolor=color, elinewidth=1.6, capsize=4,
                    markersize=6)
        ax.annotate(f"{mean:.3f}  [{lo:.3f}, {hi:.3f}]", (hi, yi),
                    xytext=(6, 0), textcoords="offset points",
                    va="center", fontsize=8, color="#333333")
    ax.set_yticks(y)
    ax.set_yticklabels(order, fontsize=10)
    ax.set_xlabel("Aggregate MAP@10 over 150 queries (95% bootstrap CI)", fontsize=9)
    ax.set_xlim(0.15, 0.52)
    ax.grid(axis="x", linestyle=":", alpha=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_title("Query-level bootstrap confidence intervals (pooled qrels)", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
