"""Generate manuscript Results figures from fixed raw-result JSON files.

This script is intentionally separate from the general report utilities. It
creates the journal-facing figures with stable M1--M5 labels while preserving
the existing filenames referenced by journal_paper/results.tex.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "journal_paper"


def _figure_datasets() -> list[str]:
    """Datasets the manuscript figures are built from.

    Driven by config.paper_datasets so figures and table fragments always describe the
    same corpora, and a scratch dataset in datasets/ cannot leak into the paper.
    """
    import sys as _sys
    if str(PROJECT_ROOT) not in _sys.path:
        _sys.path.insert(0, str(PROJECT_ROOT))
    import config as _cfg
    pinned = getattr(_cfg, "paper_datasets", None)
    return list(pinned) if pinned else _cfg.discover_available_datasets()


DATASET_REPORT_DIRS = {
    name: PROJECT_ROOT / "datasets" / name / "reports"
    for name in _figure_datasets()
}

METRICS = [
    ("map", "MAP"),
    ("recall", "Recall"),
    ("precision", "Precision"),
    ("ndcg", "NDCG"),
    ("mrr", "MRR"),
    ("hit_rate", "Success"),
]

DATASET_LABELS = {
    "education_eng": "education_eng",
    "education_tr": "education_tr",
    "law_tr": "law_tr",
}

MODEL_COLORS = {
    "M1": "#2868a8",
    "M2": "#7a5195",
    "M3": "#2a9d8f",
    "M4": "#f4a261",
    "M5": "#d1495b",
}


def latest_raw_result_path(dataset_name: str) -> Path:
    report_dir = DATASET_REPORT_DIRS[dataset_name]
    candidates = sorted(report_dir.glob("raw_results_*.json"))
    if not candidates:
        raise FileNotFoundError(f"No raw_results_*.json files found in {report_dir}")
    return candidates[-1]


def load_raw_results() -> tuple[dict[str, dict[str, Any]], dict[str, Path]]:
    datasets = {}
    selected_paths = {}
    for dataset_name in DATASET_REPORT_DIRS:
        path = latest_raw_result_path(dataset_name)
        if not path.exists():
            raise FileNotFoundError(f"Missing raw results file: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("dataset") != dataset_name:
            raise ValueError(f"Unexpected dataset name in {path}: {data.get('dataset')}")
        datasets[dataset_name] = data
        selected_paths[dataset_name] = path
    return datasets, selected_paths


def build_alias_map(reference_dataset: dict[str, Any]) -> dict[str, str]:
    models = reference_dataset["config"]["embedding_models"]
    alias_map = {
        model_info["model_name"]: f"M{index}"
        for index, model_info in enumerate(models, start=1)
    }
    if set(alias_map) != set(reference_dataset["models"]):
        raise ValueError("Model roster in config does not match model results")
    return alias_map


def validate_rosters(datasets: dict[str, dict[str, Any]], alias_map: dict[str, str]) -> None:
    expected_models = list(alias_map.keys())
    for dataset_name, data in datasets.items():
        actual_models = [m["model_name"] for m in data["config"]["embedding_models"]]
        if actual_models != expected_models:
            raise ValueError(f"Model order mismatch in {dataset_name}")
        if set(data["models"]) != set(expected_models):
            raise ValueError(f"Model result mismatch in {dataset_name}")


def ordered_aliases(alias_map: dict[str, str]) -> list[tuple[str, str]]:
    return sorted(alias_map.items(), key=lambda item: int(item[1][1:]))


def metric_value(data: dict[str, Any], model_name: str, metric: str) -> float:
    return float(data["models"][model_name]["metrics"][metric])


def latency_ms(data: dict[str, Any], model_name: str) -> float:
    return float(data["models"][model_name]["timing"]["avg_query_latency_ms"])


def query_count(data: dict[str, Any], model_name: str) -> int:
    return int(data["models"][model_name]["timing"].get("queries_timed", 1))


def weighted_latency_ms(datasets: dict[str, dict[str, Any]], dataset_names: list[str], model_name: str) -> float:
    latencies = np.array([latency_ms(datasets[dataset_name], model_name) for dataset_name in dataset_names])
    weights = np.array([query_count(datasets[dataset_name], model_name) for dataset_name in dataset_names])
    return float(np.average(latencies, weights=weights))


def configure_matplotlib() -> None:
    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "figure.dpi": 120,
            "savefig.dpi": 300,
        }
    )


def save_dataset_metric_profile(
    dataset_name: str,
    data: dict[str, Any],
    alias_map: dict[str, str],
    output_dir: Path,
) -> Path:
    aliases = ordered_aliases(alias_map)
    alias_labels = [alias for _, alias in aliases]
    k_value = data["config"]["k"]

    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    x_positions = np.arange(len(alias_labels))
    width = 0.12
    offsets = (np.arange(len(METRICS)) - (len(METRICS) - 1) / 2) * width
    colors = ["#2868a8", "#e07a5f", "#2a9d8f", "#7a5195", "#f4a261", "#6c757d"]

    for offset, (metric_key, metric_label), color in zip(offsets, METRICS, colors):
        values = [metric_value(data, model_name, metric_key) for model_name, _ in aliases]
        ax.bar(
            x_positions + offset,
            values,
            width=width,
            label=f"{metric_label}@{k_value}",
            color=color,
            edgecolor="white",
            linewidth=0.4,
        )

    ax.set_title(f"{DATASET_LABELS.get(dataset_name, dataset_name)} metric profile")
    ax.set_xlabel("Embedding model")
    ax.set_ylabel("Score")
    ax.set_xticks(x_positions)
    ax.set_xticklabels(alias_labels)
    ax.set_ylim(0, 1.04)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.20), frameon=False)
    fig.tight_layout()

    output_path = output_dir / f"results_{dataset_name}_model_comparison.png"
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return output_path


def save_cross_dataset_heatmap(
    datasets: dict[str, dict[str, Any]],
    alias_map: dict[str, str],
    output_dir: Path,
) -> Path:
    aliases = ordered_aliases(alias_map)
    dataset_names = list(DATASET_REPORT_DIRS)
    values = np.array(
        [
            [metric_value(datasets[dataset_name], model_name, "map") for model_name, _ in aliases]
            for dataset_name in dataset_names
        ]
    )

    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    image = ax.imshow(values, cmap="YlGnBu", vmin=0, vmax=max(0.65, float(values.max())))
    ax.set_title("Cross-dataset MAP@10 comparison")
    ax.set_xlabel("Embedding model")
    ax.set_ylabel("Dataset")
    ax.set_xticks(np.arange(len(aliases)))
    ax.set_xticklabels([alias for _, alias in aliases])
    ax.set_yticks(np.arange(len(dataset_names)))
    ax.set_yticklabels([DATASET_LABELS.get(name, name) for name in dataset_names])

    for row_idx in range(values.shape[0]):
        for col_idx in range(values.shape[1]):
            val = values[row_idx, col_idx]
            ax.text(col_idx, row_idx, f"{val:.4f}", ha="center", va="center", color="#17202a")

    cbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("MAP@10")
    fig.tight_layout()

    output_path = output_dir / "results_cross_dataset_performance.png"
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return output_path


def save_quality_speed_tradeoff(
    datasets: dict[str, dict[str, Any]],
    alias_map: dict[str, str],
    output_dir: Path,
) -> Path:
    aliases = ordered_aliases(alias_map)
    dataset_names = list(DATASET_REPORT_DIRS)

    records = []
    for model_name, alias in aliases:
        map_scores = [metric_value(datasets[dataset_name], model_name, "map") for dataset_name in dataset_names]
        records.append(
            {
                "alias": alias,
                "mean_map": float(np.mean(map_scores)),
                "weighted_latency": weighted_latency_ms(datasets, dataset_names, model_name),
            }
        )

    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    for record in records:
        alias = record["alias"]
        ax.scatter(
            record["weighted_latency"],
            record["mean_map"],
            s=95,
            color=MODEL_COLORS[alias],
            edgecolor="white",
            linewidth=0.8,
            zorder=3,
        )
        ax.annotate(
            alias,
            (record["weighted_latency"], record["mean_map"]),
            textcoords="offset points",
            xytext=(7, 6),
            ha="left",
            va="bottom",
            weight="bold",
        )

    ax.set_title("Quality-speed tradeoff")
    ax.set_xlabel("Weighted query latency (ms/query)")
    ax.set_ylabel("Mean MAP@10")
    ax.grid(alpha=0.25)
    x_values = [record["weighted_latency"] for record in records]
    y_values = [record["mean_map"] for record in records]
    ax.set_xlim(min(x_values) - 4, max(x_values) + 7)
    ax.set_ylim(min(y_values) - 0.04, max(y_values) + 0.05)
    fig.tight_layout()

    output_path = output_dir / "results_quality_speed_tradeoff.png"
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return output_path


def build_metadata(
    datasets: dict[str, dict[str, Any]],
    alias_map: dict[str, str],
    selected_paths: dict[str, Path],
    generated_paths: list[Path] | None = None,
) -> dict[str, Any]:
    aliases = ordered_aliases(alias_map)
    dataset_names = list(DATASET_REPORT_DIRS)
    metadata = {
        "model_aliases": {alias: model_name for model_name, alias in aliases},
        "datasets": dataset_names,
        "raw_result_files": {
            dataset_name: str(selected_paths[dataset_name].relative_to(PROJECT_ROOT))
            for dataset_name in dataset_names
        },
        "figure_labels": {
            "model_labels": [alias for _, alias in aliases],
            "dataset_labels": [DATASET_LABELS.get(name, name) for name in dataset_names],
        },
        "aggregate_quality_speed": {},
        "generated_files": [str(path.relative_to(PROJECT_ROOT)) for path in generated_paths or []],
    }

    for model_name, alias in aliases:
        map_scores = [metric_value(datasets[dataset_name], model_name, "map") for dataset_name in dataset_names]
        metadata["aggregate_quality_speed"][alias] = {
            "mean_map": round(float(np.mean(map_scores)), 4),
            "weighted_latency_ms": round(weighted_latency_ms(datasets, dataset_names, model_name), 2),
            "throughput_range_chunks_per_s": [
                round(
                    min(
                        float(datasets[dataset_name]["models"][model_name]["timing"]["chunks_per_second"])
                        for dataset_name in dataset_names
                    ),
                    1,
                ),
                round(
                    max(
                        float(datasets[dataset_name]["models"][model_name]["timing"]["chunks_per_second"])
                        for dataset_name in dataset_names
                    ),
                    1,
                ),
            ],
        }

    return metadata


def validate_metadata(metadata: dict[str, Any]) -> None:
    labels = metadata["figure_labels"]["model_labels"]
    if labels != ["M1", "M2", "M3", "M4", "M5"]:
        raise ValueError(f"Unexpected model labels: {labels}")

    serialized_labels = json.dumps(metadata["figure_labels"], ensure_ascii=False)
    forbidden = ("sentence-transformers", "MiniLM", "mpnet", "paraphrase")
    found = [token for token in forbidden if token in serialized_labels]
    if found:
        raise ValueError(f"Full model-name fragments found in plotted labels: {found}")


def save_bootstrap_forest(datasets: dict[str, Any], output_dir: Path) -> Path:
    """Forest plot of the pooled aggregate MAP@10 with 95% bootstrap intervals.

    Recomputes the pooled block from the stored per-query rankings via the shared
    pipeline stage, so this figure never depends on a hand-run analysis script.
    Wide, overlapping intervals are exactly the point the figure makes.
    """
    import sys

    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from utils import bootstrap_utils as bs

    pooled, _ = bs.pooled_over_datasets(list(datasets))
    ci = pooled["ci_map"]
    n_queries = pooled["n_queries"]

    order = sorted(ci, key=lambda k: -ci[k]["mean"])
    y = list(range(len(order)))[::-1]  # top row = best
    leader = pooled.get("leader")

    fig, ax = plt.subplots(figsize=(6.2, 3.3))
    for yi, m in zip(y, order):
        mean, lo, hi = ci[m]["mean"], ci[m]["lo"], ci[m]["hi"]
        color = "#b2182b" if m == leader else "#2166ac"
        ax.errorbar(mean, yi, xerr=[[mean - lo], [hi - mean]], fmt="o",
                    color=color, ecolor=color, elinewidth=1.6, capsize=4,
                    markersize=6)
        ax.annotate(f"{mean:.3f}  [{lo:.3f}, {hi:.3f}]", (hi, yi),
                    xytext=(6, 0), textcoords="offset points",
                    va="center", fontsize=8, color="#333333")
    ax.set_yticks(y)
    ax.set_yticklabels(order, fontsize=10)
    ax.set_xlabel(f"Aggregate MAP@10 over {n_queries} scored queries (95% bootstrap CI)",
                  fontsize=9)
    lo_all = min(ci[m]["lo"] for m in order)
    hi_all = max(ci[m]["hi"] for m in order)
    pad = 0.06 * (hi_all - lo_all)
    ax.set_xlim(lo_all - pad, hi_all + 5 * pad)
    ax.grid(axis="x", linestyle=":", alpha=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_title("Query-level bootstrap confidence intervals (model-independent pooled qrels)",
                 fontsize=10)
    fig.tight_layout()
    output_path = output_dir / "results_bootstrap_forest.png"
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path


def generate_figures() -> dict[str, Any]:
    configure_matplotlib()
    datasets, selected_paths = load_raw_results()
    alias_map = build_alias_map(datasets[next(iter(datasets))])
    validate_rosters(datasets, alias_map)

    generated_paths = []
    for dataset_name, data in datasets.items():
        generated_paths.append(save_dataset_metric_profile(dataset_name, data, alias_map, OUTPUT_DIR))
    generated_paths.append(save_cross_dataset_heatmap(datasets, alias_map, OUTPUT_DIR))
    generated_paths.append(save_quality_speed_tradeoff(datasets, alias_map, OUTPUT_DIR))
    try:
        generated_paths.append(save_bootstrap_forest(datasets, OUTPUT_DIR))
    except FileNotFoundError as exc:
        print(f"[Skip] bootstrap forest plot: {exc}")

    metadata = build_metadata(datasets, alias_map, selected_paths, generated_paths)
    validate_metadata(metadata)
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="Print computed metadata without writing figures.",
    )
    args = parser.parse_args()

    datasets, selected_paths = load_raw_results()
    alias_map = build_alias_map(datasets[next(iter(datasets))])
    validate_rosters(datasets, alias_map)

    if args.metadata_only:
        metadata = build_metadata(datasets, alias_map, selected_paths)
        validate_metadata(metadata)
    else:
        metadata = generate_figures()

    print(json.dumps(metadata, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
