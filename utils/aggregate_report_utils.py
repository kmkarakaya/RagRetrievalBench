"""
Aggregate reporting utilities for cross-dataset performance comparison.
Implements statistical analysis and visualization generation for multi-dataset benchmarks.
"""
import json
import os
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import config as cfg

# Check for required dependencies
try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("Warning: scipy not available. Install with: conda install scipy")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas not available. Install with: conda install pandas")

try:
    import matplotlib.pyplot as plt
    import matplotlib
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available for visualizations")


# Shared colormap for aggregate heatmaps (aligned with significance heatmap)
AGG_HEATMAP_CMAP = "Reds_r"
HEATMAP_TITLE_SIZE = 16
HEATMAP_TICK_SIZE = 10
HEATMAP_ANNOT_SIZE = 10

METRIC_DISPLAY_NAMES = {
    "map": "MAP",
    "recall": "Recall",
    "precision": "Precision",
    "ndcg": "NDCG",
    "mrr": "MRR",
    "hit_rate": "Success/Hit Rate",
}

METRIC_HEADER_NAMES = {
    "map": "MAP",
    "recall": "Recall",
    "precision": "Precision",
    "ndcg": "NDCG",
    "mrr": "MRR",
    "hit_rate": "Success",
}


def metric_display_name(metric: str) -> str:
    """Human-readable metric name for narrative text and titles."""
    return METRIC_DISPLAY_NAMES.get(metric, metric.upper())


def metric_header_name(metric: str) -> str:
    """Short metric name for table headers."""
    return METRIC_HEADER_NAMES.get(metric, metric.upper())


def check_aggregate_dependencies():
    """
    Check if required dependencies for aggregate reporting are installed.
    Raises ImportError with installation instructions if missing.
    """
    missing = []
    
    if not SCIPY_AVAILABLE:
        missing.append("scipy (install: conda install scipy)")
    
    if not PANDAS_AVAILABLE:
        missing.append("pandas (install: conda install pandas)")
    
    if missing:
        raise ImportError(
            f"Aggregate reporting requires additional packages:\n" +
            "\n".join(f"  - {pkg}" for pkg in missing) +
            "\n\nInstall all: conda install scipy pandas"
        )
    
    # Check optional dependencies
    if not MATPLOTLIB_AVAILABLE:
        print("Warning: matplotlib not found. Visualizations will be disabled.")
        print("Install: conda install matplotlib")


# ============================================================================
# Data Loading Functions
# ============================================================================

def load_dataset_results(dataset_name: str) -> Optional[Dict]:
    """
    Load most recent raw_results JSON for a dataset.
    Returns None if not found or invalid.
    """
    raw_results_path = cfg.get_latest_raw_results(dataset_name)
    
    if raw_results_path is None:
        print(f"Warning: No raw results found for dataset '{dataset_name}'")
        return None
    
    try:
        with open(raw_results_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate required fields
        required_fields = ["dataset", "timestamp", "config", "models", "corpus_stats"]
        for field in required_fields:
            if field not in data:
                print(f"Warning: Missing field '{field}' in {raw_results_path}")
                return None

        # Warn on missing detailed fields (backward compatibility)
        optional_fields = [
            "corpus_characteristics",
            "query_characteristics",
            "relevance_characteristics",
            "representative_queries"
        ]
        missing_optional = [field for field in optional_fields if field not in data]
        if missing_optional:
            print(
                f"Warning: Missing detailed fields in {raw_results_path}: "
                f"{', '.join(missing_optional)}. Aggregate report will show N/A."
            )
        
        return data
    
    except json.JSONDecodeError as e:
        print(f"Error: Corrupted JSON in {raw_results_path}: {e}")
        return None
    except Exception as e:
        print(f"Error loading {raw_results_path}: {e}")
        return None


def load_multiple_datasets(dataset_names: List[str] = None) -> Dict[str, Dict]:
    """
    Load results for multiple datasets.
    Uses config.discover_available_datasets() if dataset_names is None.
    Validates minimum dataset count (config.aggregate_min_datasets).
    
    Returns: {"dataset_name": {...raw_results...}, ...}
    """
    if dataset_names is None:
        dataset_names = cfg.discover_available_datasets()
        print(f"Auto-discovered datasets: {', '.join(dataset_names)}")
    
    if len(dataset_names) < cfg.aggregate_min_datasets:
        raise ValueError(
            f"Need at least {cfg.aggregate_min_datasets} datasets for aggregation. "
            f"Found: {len(dataset_names)} datasets"
        )
    
    datasets = {}
    for name in dataset_names:
        if name in cfg.aggregate_exclude_datasets:
            print(f"Skipping excluded dataset: {name}")
            continue
        
        data = load_dataset_results(name)
        if data is not None:
            datasets[name] = data
        else:
            print(f"Warning: Could not load dataset '{name}', skipping...")
    
    if len(datasets) < cfg.aggregate_min_datasets:
        raise ValueError(
            f"Successfully loaded only {len(datasets)} datasets, "
            f"need at least {cfg.aggregate_min_datasets}"
        )
    
    return datasets


def validate_metric_compatibility(datasets: Dict[str, Dict]) -> Dict[str, Any]:
    """
    Check metric flag consistency across datasets.
    Returns validation report with warnings/errors.
    If config.aggregate_require_identical_metrics=True, raises error on mismatch.
    """
    if not datasets:
        return {"status": "error", "message": "No datasets provided"}
    
    # Collect metric flags from all datasets
    dataset_metrics = {}
    for ds_name, ds_data in datasets.items():
        metric_flags = ds_data.get("config", {}).get("metric_flags", {})
        dataset_metrics[ds_name] = metric_flags
    
    # Find common metrics (intersection)
    all_metrics = ["compute_map", "compute_recall", "compute_precision", "compute_ndcg", "compute_mrr", "compute_hit_rate"]
    common_metrics = set(all_metrics)
    
    for ds_name, flags in dataset_metrics.items():
        enabled = {m for m in all_metrics if flags.get(m, False)}
        common_metrics &= enabled
    
    # Check if identical metrics required
    if cfg.aggregate_require_identical_metrics:
        first_flags = list(dataset_metrics.values())[0]
        for ds_name, flags in dataset_metrics.items():
            if flags != first_flags:
                raise ValueError(
                    f"Dataset '{ds_name}' has different metric configuration. "
                    f"Set config.aggregate_require_identical_metrics=False to allow intersection."
                )
    
    # Build report
    report = {
        "status": "ok" if common_metrics else "error",
        "common_metrics": sorted(list(common_metrics)),
        "dataset_metrics": dataset_metrics,
        "warnings": []
    }
    
    if not common_metrics:
        report["status"] = "error"
        report["message"] = "No common metrics found across all datasets"
    
    # Add warnings for excluded metrics
    all_enabled = set()
    for flags in dataset_metrics.values():
        all_enabled.update([m for m in all_metrics if flags.get(m, False)])
    
    excluded = all_enabled - common_metrics
    if excluded:
        metric_names = [metric_display_name(m.replace("compute_", "")) for m in excluded]
        report["warnings"].append(
            f"Metrics {', '.join(metric_names)} excluded (not enabled in all datasets)"
        )
    
    return report


def validate_config_consistency(datasets: Dict[str, Dict]) -> None:
    """
    Enforce identical dataset configs required for aggregation.
    Raises ValueError on mismatch.
    """
    if not datasets:
        raise ValueError("No datasets provided")

    first_ds = list(datasets.values())[0]
    first_config = first_ds.get("config", {})
    required_keys = ["k", "chunk_size", "chunk_overlap", "metric_flags"]

    for key in required_keys:
        if key not in first_config:
            raise ValueError(f"Missing config '{key}' in dataset '{first_ds.get('dataset', 'unknown')}'")

    for ds_name, ds_data in datasets.items():
        config = ds_data.get("config", {})
        for key in required_keys:
            if config.get(key) != first_config.get(key):
                raise ValueError(
                    f"Dataset '{ds_name}' has different config for '{key}'. "
                    "Aggregation requires identical k, chunking, and metric flags across datasets."
                )


# ============================================================================
# Metric Normalization Functions
# ============================================================================

def get_common_metrics(datasets: Dict[str, Dict]) -> List[str]:
    """
    Identify metrics enabled in ALL datasets.
    Returns: ["map", "recall", "ndcg"] (intersection of enabled metrics)
    """
    validation = validate_metric_compatibility(datasets)
    
    if validation["status"] == "error":
        return []
    
    # Convert compute_* to metric names using stable preferred order.
    ordered_flags = ["compute_map", "compute_recall", "compute_precision", "compute_ndcg", "compute_mrr", "compute_hit_rate"]
    common_set = set(validation["common_metrics"])
    return [m.replace("compute_", "") for m in ordered_flags if m in common_set]


def normalize_model_names(datasets: Dict[str, Dict]) -> Dict[str, str]:
    """
    Handle model name variations across datasets.
    Example: "sentence-transformers/all-MiniLM-L6-v2" vs "all-MiniLM-L6-v2"
    
    Returns mapping: {normalized_name: canonical_name}
    """
    all_models = set()
    for ds_data in datasets.values():
        all_models.update(ds_data.get("models", {}).keys())
    
    # For now, use full name as canonical (most detailed)
    # Future enhancement: implement fuzzy matching for variations
    mapping = {name: name for name in all_models}
    
    return mapping


def extract_model_scores_across_datasets(
    datasets: Dict[str, Dict],
    model_name: str,
    metric: str
) -> Dict[str, float]:
    """
    Extract scores for one model/metric across all datasets.
    Returns: {"education": 0.7999, "finance": 0.6543, ...}
    """
    scores = {}
    
    for ds_name, ds_data in datasets.items():
        models = ds_data.get("models", {})
        if model_name in models:
            model_data = models[model_name]
            metrics = model_data.get("metrics", {})
            if metric in metrics:
                scores[ds_name] = float(metrics[metric])
    
    return scores


# ============================================================================
# Aggregation Functions
# ============================================================================

def aggregate_model_performance(datasets: Dict[str, Dict]) -> Dict[str, Dict]:
    """
    Compute aggregate statistics per model across datasets.
    
    Returns structure:
    {
        "sentence-transformers/all-MiniLM-L6-v2": {
            "map": {
                "mean": 0.75,
                "median": 0.77,
                "std": 0.12,
                "min": 0.65,
                "max": 0.85,
                "scores_by_dataset": {"education": 0.80, "finance": 0.70}
            },
            "recall": {...},
            ...
        },
        ...
    }
    """
    # Get all unique models across datasets
    all_models = set()
    for ds_data in datasets.values():
        all_models.update(ds_data.get("models", {}).keys())
    
    # Get common metrics
    common_metrics = get_common_metrics(datasets)
    
    aggregated = {}
    
    for model_name in all_models:
        aggregated[model_name] = {}
        
        for metric in common_metrics:
            scores_dict = extract_model_scores_across_datasets(datasets, model_name, metric)
            
            if not scores_dict:
                continue
            
            scores = list(scores_dict.values())
            
            aggregated[model_name][metric] = {
                "mean": float(np.mean(scores)),
                "median": float(np.median(scores)),
                "std": float(np.std(scores, ddof=1)) if len(scores) > 1 else 0.0,
                "min": float(np.min(scores)),
                "max": float(np.max(scores)),
                "scores_by_dataset": scores_dict,
                "count": len(scores)
            }
    
    return aggregated


def calculate_model_rankings(
    datasets: Dict[str, Dict],
    metric: str
) -> Dict[str, List[Tuple[str, int]]]:
    """
    Rank models for each dataset on specified metric.
    
    Returns:
    {
        "education": [
            ("all-MiniLM-L6-v2", 1),
            ("all-mpnet-base-v2", 2),
            ...
        ],
        "finance": [...]
    }
    """
    rankings = {}
    
    for ds_name, ds_data in datasets.items():
        models = ds_data.get("models", {})
        
        # Extract scores for this metric
        model_scores = []
        for model_name, model_data in models.items():
            score = model_data.get("metrics", {}).get(metric)
            if score is not None:
                model_scores.append((model_name, float(score)))
        
        # Sort by score (descending) and assign ranks
        model_scores.sort(key=lambda x: x[1], reverse=True)
        rankings[ds_name] = [(model, rank + 1) for rank, (model, _) in enumerate(model_scores)]
    
    return rankings


def calculate_average_ranks(
    rankings: Dict[str, List[Tuple[str, int]]]
) -> List[Tuple[str, float]]:
    """
    Compute mean rank across datasets for each model.
    Used for overall best model determination.
    
    Returns: [("all-MiniLM-L6-v2", 1.33), ("all-mpnet-base-v2", 2.67), ...]
    Sorted by average rank (lower is better).
    """
    model_ranks = {}
    
    for ds_rankings in rankings.values():
        for model_name, rank in ds_rankings:
            if model_name not in model_ranks:
                model_ranks[model_name] = []
            model_ranks[model_name].append(rank)
    
    # Calculate average ranks
    avg_ranks = [
        (model, np.mean(ranks))
        for model, ranks in model_ranks.items()
    ]
    
    # Sort by average rank (lower is better)
    avg_ranks.sort(key=lambda x: x[1])
    
    return avg_ranks


def calculate_consistency_scores(model_results: Dict[str, Dict]) -> Dict[str, Dict]:
    """
    Measure performance variability across datasets.
    
    Returns per model:
    {
        "all-MiniLM-L6-v2": {
            "coefficient_of_variation": 0.15,  # std/mean across datasets
            "rank_stability": 0.85,  # 1 - (rank_std / max_possible_rank_std)
            "worst_case_drop": 0.20  # (max_score - min_score) / max_score
        },
        ...
    }
    """
    consistency = {}
    
    for model_name, metrics_data in model_results.items():
        model_consistency = {}
        
        # Get all metric scores across datasets
        all_scores = []
        for metric, stats in metrics_data.items():
            if isinstance(stats, dict) and "scores_by_dataset" in stats:
                scores = list(stats["scores_by_dataset"].values())
                if scores:
                    all_scores.extend(scores)
        
        if not all_scores:
            continue
        
        mean_score = np.mean(all_scores)
        std_score = np.std(all_scores, ddof=1) if len(all_scores) > 1 else 0.0
        
        # Coefficient of variation
        cv = (std_score / mean_score) if mean_score > 0 else 0.0
        
        # Worst case drop
        max_score = np.max(all_scores)
        min_score = np.min(all_scores)
        worst_drop = ((max_score - min_score) / max_score) if max_score > 0 else 0.0
        
        model_consistency = {
            "coefficient_of_variation": float(cv),
            "worst_case_drop": float(worst_drop),
            "score_range": float(max_score - min_score)
        }
        
        consistency[model_name] = model_consistency
    
    return consistency


# ============================================================================
# Statistical Analysis Functions
# ============================================================================

def perform_pairwise_significance_tests(
    datasets: Dict[str, Dict],
    metric: str,
    alpha: float = None
) -> 'pd.DataFrame':
    """
    Paired t-test for all model pairs across datasets.
    Each dataset provides one paired observation.
    
    Returns DataFrame with p-values (NaN on diagonal, symmetric matrix).
    """
    if not SCIPY_AVAILABLE or not PANDAS_AVAILABLE:
        check_aggregate_dependencies()
    
    if alpha is None:
        alpha = cfg.aggregate_significance_level
    
    # Get all models
    all_models = set()
    for ds_data in datasets.values():
        all_models.update(ds_data.get("models", {}).keys())
    
    all_models = sorted(list(all_models))
    
    # Build scores matrix: rows=models, cols=datasets
    scores_matrix = {}
    for model in all_models:
        scores = extract_model_scores_across_datasets(datasets, model, metric)
        # Need to have same datasets for pairing
        scores_matrix[model] = scores
    
    # Create p-value matrix
    n_models = len(all_models)
    p_values = np.full((n_models, n_models), np.nan)
    
    for i, model_a in enumerate(all_models):
        for j, model_b in enumerate(all_models):
            if i >= j:  # Skip diagonal and lower triangle
                continue
            
            scores_a = scores_matrix[model_a]
            scores_b = scores_matrix[model_b]
            
            # Get paired scores (only datasets with both models)
            common_datasets = set(scores_a.keys()) & set(scores_b.keys())
            
            if len(common_datasets) < 2:  # Need at least 2 pairs for t-test
                continue
            
            paired_a = [scores_a[ds] for ds in sorted(common_datasets)]
            paired_b = [scores_b[ds] for ds in sorted(common_datasets)]
            
            try:
                t_stat, p_val = stats.ttest_rel(paired_a, paired_b)
                p_values[i, j] = p_val
                p_values[j, i] = p_val  # Symmetric
            except Exception as e:
                print(f"Warning: Could not compute t-test for {model_a} vs {model_b}: {e}")
    
    # Create DataFrame
    df = pd.DataFrame(p_values, index=all_models, columns=all_models)
    
    return df


def calculate_effect_sizes(
    datasets: Dict[str, Dict],
    model_a: str,
    model_b: str,
    metric: str
) -> Dict[str, float]:
    """
    Cohen's d effect size for model comparison.
    
    Returns:
    {
        "cohens_d": 0.85,
        "interpretation": "large",  # small (<0.5), medium (0.5-0.8), large (>0.8)
        "mean_difference": 0.15
    }
    """
    scores_a = extract_model_scores_across_datasets(datasets, model_a, metric)
    scores_b = extract_model_scores_across_datasets(datasets, model_b, metric)
    
    # Get paired scores
    common_datasets = set(scores_a.keys()) & set(scores_b.keys())
    
    if len(common_datasets) < 2:
        return {"cohens_d": 0.0, "interpretation": "insufficient_data", "mean_difference": 0.0}
    
    paired_a = [scores_a[ds] for ds in sorted(common_datasets)]
    paired_b = [scores_b[ds] for ds in sorted(common_datasets)]
    
    mean_a, mean_b = np.mean(paired_a), np.mean(paired_b)
    var_a, var_b = np.var(paired_a, ddof=1), np.var(paired_b, ddof=1)
    n_a, n_b = len(paired_a), len(paired_b)
    
    # Pooled standard deviation
    pooled_std = np.sqrt(((n_a - 1) * var_a + (n_b - 1) * var_b) / (n_a + n_b - 2))
    
    # Cohen's d
    cohens_d = (mean_a - mean_b) / pooled_std if pooled_std > 0 else 0.0
    
    # Interpretation
    abs_d = abs(cohens_d)
    if abs_d < 0.5:
        interpretation = "small"
    elif abs_d < 0.8:
        interpretation = "medium"
    else:
        interpretation = "large"
    
    return {
        "cohens_d": float(cohens_d),
        "interpretation": interpretation,
        "mean_difference": float(mean_a - mean_b)
    }


def generate_win_tie_loss_matrix(
    datasets: Dict[str, Dict],
    metric: str,
    tie_threshold: float = 0.01
) -> 'pd.DataFrame':
    """
    Win-Tie-Loss analysis across datasets.
    
    Returns DataFrame showing wins for row model vs column model:
                        all-MiniLM-L6-v2  all-mpnet-base-v2
    all-MiniLM-L6-v2                 -              "2-0-1"
    all-mpnet-base-v2            "1-0-2"                  -
    
    Format: "Wins-Ties-Losses" across datasets.
    """
    if not PANDAS_AVAILABLE:
        check_aggregate_dependencies()
    
    # Get all models
    all_models = set()
    for ds_data in datasets.values():
        all_models.update(ds_data.get("models", {}).keys())
    
    all_models = sorted(list(all_models))
    
    # Build WTL matrix
    wtl_matrix = {}
    
    for model_a in all_models:
        wtl_matrix[model_a] = {}
        
        for model_b in all_models:
            if model_a == model_b:
                wtl_matrix[model_a][model_b] = "-"
                continue
            
            wins, ties, losses = 0, 0, 0
            
            # Compare across datasets
            for ds_data in datasets.values():
                models = ds_data.get("models", {})
                
                if model_a not in models or model_b not in models:
                    continue
                
                score_a = models[model_a].get("metrics", {}).get(metric)
                score_b = models[model_b].get("metrics", {}).get(metric)
                
                if score_a is None or score_b is None:
                    continue
                
                diff = score_a - score_b
                
                if abs(diff) <= tie_threshold:
                    ties += 1
                elif diff > 0:
                    wins += 1
                else:
                    losses += 1
            
            wtl_matrix[model_a][model_b] = f"{wins}-{ties}-{losses}"
    
    return pd.DataFrame(wtl_matrix).T


def perform_friedman_test(
    datasets: Dict[str, Dict],
    metric: str
) -> Tuple[float, float]:
    """
    Friedman test for overall differences across multiple models and datasets.
    Non-parametric alternative to repeated measures ANOVA.
    
    Returns: (chi_square_statistic, p_value)
    """
    if not SCIPY_AVAILABLE:
        check_aggregate_dependencies()
    
    # Get all models
    all_models = set()
    for ds_data in datasets.values():
        all_models.update(ds_data.get("models", {}).keys())
    
    all_models = sorted(list(all_models))
    
    # Build scores matrix: each row is a dataset, each column is a model
    scores_by_dataset = []
    
    for ds_name in sorted(datasets.keys()):
        ds_data = datasets[ds_name]
        models = ds_data.get("models", {})
        
        dataset_scores = []
        for model in all_models:
            score = models.get(model, {}).get("metrics", {}).get(metric)
            if score is not None:
                dataset_scores.append(score)
            else:
                dataset_scores.append(np.nan)
        
        scores_by_dataset.append(dataset_scores)
    
    # Remove columns (models) with any NaN
    scores_array = np.array(scores_by_dataset)
    valid_cols = ~np.isnan(scores_array).any(axis=0)
    
    if valid_cols.sum() < 3:
        return (np.nan, np.nan)  # Need at least 3 models
    
    scores_array = scores_array[:, valid_cols]
    
    try:
        statistic, p_value = stats.friedmanchisquare(*scores_array.T)
        return (float(statistic), float(p_value))
    except Exception as e:
        print(f"Warning: Friedman test failed: {e}")
        return (np.nan, np.nan)


# ============================================================================
# Helper Functions
# ============================================================================

def get_common_models(datasets: Dict[str, Dict]) -> List[str]:
    """Get models that appear in all datasets."""
    if not datasets:
        return []
    
    model_sets = [set(ds_data.get("models", {}).keys()) for ds_data in datasets.values()]
    common = set.intersection(*model_sets) if model_sets else set()
    
    return sorted(list(common))


def get_all_models(datasets: Dict[str, Dict]) -> List[str]:
    """Get all unique models across datasets."""
    all_models = set()
    for ds_data in datasets.values():
        all_models.update(ds_data.get("models", {}).keys())
    
    return sorted(list(all_models))


def extract_query_latency_matrix(datasets: Dict[str, Dict]) -> Dict[str, Dict[str, Optional[float]]]:
    """
    Extract avg query latency (ms/query) per model per dataset from raw results timing.

    Returns:
    {
        "model_a": {"dataset_1": 12.3, "dataset_2": None, ...},
        ...
    }
    """
    matrix: Dict[str, Dict[str, Optional[float]]] = {}
    dataset_names = sorted(datasets.keys())

    for model_name in get_all_models(datasets):
        matrix[model_name] = {}
        for ds_name in dataset_names:
            timing = datasets.get(ds_name, {}).get("models", {}).get(model_name, {}).get("timing", {})
            latency_ms = timing.get("avg_query_latency_ms")
            matrix[model_name][ds_name] = float(latency_ms) if isinstance(latency_ms, (int, float)) else None

    return matrix


def compute_weighted_query_latency_summary(datasets: Dict[str, Dict]) -> Dict[str, Dict[str, Optional[float]]]:
    """
    Compute weighted mean query latency across datasets for each model.
    Weight = queries_timed from each dataset's raw results timing.
    """
    summary: Dict[str, Dict[str, Optional[float]]] = {}

    for model_name in get_all_models(datasets):
        weighted_sum = 0.0
        total_weight = 0
        latency_values: List[float] = []

        for ds_name in sorted(datasets.keys()):
            timing = datasets.get(ds_name, {}).get("models", {}).get(model_name, {}).get("timing", {})
            latency_ms = timing.get("avg_query_latency_ms")
            queries_timed = timing.get("queries_timed")

            if (
                isinstance(latency_ms, (int, float))
                and isinstance(queries_timed, (int, float))
                and queries_timed > 0
            ):
                latency = float(latency_ms)
                weight = int(queries_timed)
                weighted_sum += latency * weight
                total_weight += weight
                latency_values.append(latency)

        summary[model_name] = {
            "weighted_mean_latency_ms": (weighted_sum / total_weight) if total_weight > 0 else None,
            "best_latency_ms": min(latency_values) if latency_values else None,
            "worst_latency_ms": max(latency_values) if latency_values else None,
            "datasets_with_latency_data": len(latency_values),
            "total_queries_timed": total_weight,
        }

    return summary


# ============================================================================
# Visualization Generation Functions
# ============================================================================

def generate_cross_dataset_radar_chart(
    model_results: Dict[str, Dict],
    metrics: List[str],
    output_dir: str,
    timestamp: str,
    top_n_models: int = 5
) -> str:
    """
    Multi-axis radar chart comparing top models across metrics.
    Each metric axis shows mean score across datasets with error bars (std).
    
    Returns: Path to saved PNG file.
    """
    if not MATPLOTLIB_AVAILABLE:
        print("Warning: matplotlib not available, skipping radar chart")
        return ""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Select top N models by mean performance
    model_means = []
    for model_name, metrics_data in model_results.items():
        mean_scores = [metrics_data[m]["mean"] for m in metrics if m in metrics_data]
        if mean_scores:
            model_means.append((model_name, np.mean(mean_scores)))
    
    model_means.sort(key=lambda x: x[1], reverse=True)
    top_models = [m[0] for m in model_means[:top_n_models]]
    
    # Prepare data for radar chart
    num_metrics = len(metrics)
    angles = np.linspace(0, 2 * np.pi, num_metrics, endpoint=False).tolist()
    angles += angles[:1]  # Close the circle
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(top_models)))
    
    for idx, model_name in enumerate(top_models):
        values = []
        for metric in metrics:
            if metric in model_results[model_name]:
                values.append(model_results[model_name][metric]["mean"])
            else:
                values.append(0)
        
        values += values[:1]  # Close the circle
        
        short_name = model_name.split("/")[-1]
        ax.plot(angles, values, 'o-', linewidth=2, label=short_name, color=colors[idx])
        ax.fill(angles, values, alpha=0.15, color=colors[idx])
    
    # Set labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([metric_header_name(m) for m in metrics], fontsize=12)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"])
    ax.grid(True)
    
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    plt.title("Cross-Dataset Model Performance Comparison", size=16, pad=20)
    
    output_path = os.path.join(output_dir, f"cross_dataset_radar_chart_{timestamp}.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path


def generate_model_ranking_heatmap(
    rankings: Dict[str, List[Tuple[str, int]]],
    output_dir: str,
    timestamp: str
) -> str:
    """
    Heatmap showing model ranks per dataset.
    Rows: Models, Columns: Datasets, Values: Rank (1=best)
    Color scale: Green (rank 1) to Red (worst rank)
    
    Returns: Path to saved PNG file.
    """
    if not MATPLOTLIB_AVAILABLE or not PANDAS_AVAILABLE:
        print("Warning: matplotlib/pandas not available, skipping heatmap")
        return ""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Build matrix
    all_models = set()
    for ds_rankings in rankings.values():
        all_models.update([m for m, _ in ds_rankings])
    
    all_models = sorted(list(all_models))
    datasets = sorted(rankings.keys())
    
    rank_matrix = []
    for model in all_models:
        row = []
        for dataset in datasets:
            rank = None
            for m, r in rankings[dataset]:
                if m == model:
                    rank = r
                    break
            row.append(rank if rank is not None else np.nan)
        rank_matrix.append(row)
    
    df = pd.DataFrame(rank_matrix, index=[m.split("/")[-1] for m in all_models], columns=datasets)
    
    fig, ax = plt.subplots(figsize=(max(8, len(datasets) * 1.5), max(6, len(all_models) * 0.5)))
    
    # Create heatmap (invert colormap so green=1, red=high)
    im = ax.imshow(df.values, cmap=AGG_HEATMAP_CMAP, aspect='auto', vmin=1, vmax=len(all_models))
    
    # Set ticks
    ax.set_xticks(np.arange(len(datasets)))
    ax.set_yticks(np.arange(len(all_models)))
    ax.set_xticklabels(datasets)
    ax.set_yticklabels(df.index)
    ax.tick_params(axis='both', labelsize=HEATMAP_TICK_SIZE)
    
    # Rotate x labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Add rank numbers
    for i in range(len(all_models)):
        for j in range(len(datasets)):
            if not np.isnan(df.values[i, j]):
                text = ax.text(
                    j, i, int(df.values[i, j]),
                    ha="center", va="center", color="black", fontweight='bold', fontsize=HEATMAP_ANNOT_SIZE
                )
    
    ax.set_title("Model Rankings Across Datasets", fontsize=HEATMAP_TITLE_SIZE, pad=20)
    fig.colorbar(im, ax=ax, label='Rank (1=Best)')
    
    output_path = os.path.join(output_dir, f"model_ranking_heatmap_{timestamp}.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path


def generate_performance_distribution_plots(
    model_results: Dict[str, Dict],
    metric: str,
    output_dir: str,
    timestamp: str
) -> str:
    """
    Box plot for score distributions across datasets.
    One subplot per model showing score distribution.
    
    Returns: Path to saved PNG file.
    """
    if not MATPLOTLIB_AVAILABLE:
        print("Warning: matplotlib not available, skipping distribution plots")
        return ""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Collect data
    models_with_data = []
    for model_name, metrics_data in model_results.items():
        if metric in metrics_data:
            scores = list(metrics_data[metric]["scores_by_dataset"].values())
            if scores:
                models_with_data.append((model_name, scores))
    
    if not models_with_data:
        return ""
    
    n_models = len(models_with_data)
    fig, axes = plt.subplots(1, n_models, figsize=(n_models * 4, 6), squeeze=False)
    
    for idx, (model_name, scores) in enumerate(models_with_data):
        ax = axes[0, idx]
        
        # Box plot
        bp = ax.boxplot([scores], widths=0.6, patch_artist=True,
                        boxprops=dict(facecolor='lightblue', alpha=0.7),
                        medianprops=dict(color='red', linewidth=2))
        
        # Overlay individual points
        ax.scatter([1] * len(scores), scores, alpha=0.6, c='blue', s=50)
        
        short_name = model_name.split("/")[-1]
        ax.set_title(short_name, fontsize=12)
        ax.set_ylabel(metric_display_name(metric) + " Score" if idx == 0 else "")
        ax.set_xticks([])
        ax.set_ylim(0, 1)
        ax.grid(axis='y', alpha=0.3)
    
    fig.suptitle(f"{metric_display_name(metric)} Distribution Across Datasets", fontsize=16)
    
    output_path = os.path.join(output_dir, f"performance_distribution_{metric}_{timestamp}.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path


def generate_dataset_difficulty_chart(
    datasets: Dict[str, Dict],
    metric: str,
    output_dir: str,
    timestamp: str
) -> str:
    """
    Bar chart showing mean model performance per dataset.
    Datasets sorted by mean score to identify "easy" vs "hard" datasets.
    Error bars show std across models.
    
    Returns: Path to saved PNG file.
    """
    if not MATPLOTLIB_AVAILABLE:
        print("Warning: matplotlib not available, skipping difficulty chart")
        return ""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Calculate mean and std per dataset
    dataset_stats = []
    
    for ds_name, ds_data in datasets.items():
        models = ds_data.get("models", {})
        scores = []
        
        for model_data in models.values():
            score = model_data.get("metrics", {}).get(metric)
            if score is not None:
                scores.append(score)
        
        if scores:
            dataset_stats.append({
                "name": ds_name,
                "mean": np.mean(scores),
                "std": np.std(scores, ddof=1) if len(scores) > 1 else 0
            })
    
    # Sort by mean (hardest to easiest)
    dataset_stats.sort(key=lambda x: x["mean"])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    names = [ds["name"] for ds in dataset_stats]
    means = [ds["mean"] for ds in dataset_stats]
    stds = [ds["std"] for ds in dataset_stats]
    
    colors = plt.cm.RdYlGn(np.array(means))
    
    bars = ax.barh(names, means, xerr=stds, capsize=5, color=colors, alpha=0.7)
    
    ax.set_xlabel(f"Mean {metric_display_name(metric)} Score Across Models", fontsize=12)
    ax.set_ylabel("Dataset", fontsize=12)
    ax.set_title(f"Dataset Difficulty Ranking (by {metric_display_name(metric)})", fontsize=14)
    ax.set_xlim(0, 1)
    ax.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (mean, std) in enumerate(zip(means, stds)):
        ax.text(mean + std + 0.02, i, f"{mean:.3f}", va='center')
    
    output_path = os.path.join(output_dir, f"dataset_difficulty_{metric}_{timestamp}.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path


def generate_dataset_characteristics_chart(
    datasets: Dict[str, Dict],
    output_dir: str,
    timestamp: str
) -> str:
    """
    Overview chart for dataset sizes (Documents (PDFs), chunks, queries, qrels).

    Returns: Path to saved PNG file.
    """
    if not MATPLOTLIB_AVAILABLE:
        print("Warning: matplotlib not available, skipping dataset characteristics chart")
        return ""

    os.makedirs(output_dir, exist_ok=True)

    dataset_stats = []
    for ds_name, ds_data in datasets.items():
        stats = ds_data.get("corpus_stats", {})
        dataset_stats.append({
            "name": ds_name,
            "pdfs": int(stats.get("total_pdfs", 0)),
            "chunks": int(stats.get("total_chunks", 0)),
            "queries": int(stats.get("total_queries", 0)),
            "qrels": int(stats.get("total_qrels", 0))
        })

    if not dataset_stats:
        return ""

    names = [ds["name"] for ds in dataset_stats]
    pdfs = [ds["pdfs"] for ds in dataset_stats]
    chunks = [ds["chunks"] for ds in dataset_stats]
    queries = [ds["queries"] for ds in dataset_stats]
    qrels = [ds["qrels"] for ds in dataset_stats]

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    axes[0, 0].barh(names, pdfs, color="#4c78a8", alpha=0.8)
    axes[0, 0].set_title("Documents (PDFs)")

    axes[0, 1].barh(names, chunks, color="#f58518", alpha=0.8)
    axes[0, 1].set_title("Chunks")

    axes[1, 0].barh(names, queries, color="#54a24b", alpha=0.8)
    axes[1, 0].set_title("Queries")

    axes[1, 1].barh(names, qrels, color="#e45756", alpha=0.8)
    axes[1, 1].set_title("Qrels")

    for ax in axes.flat:
        ax.grid(axis='x', alpha=0.3)

    fig.suptitle("Dataset Characteristics Overview", fontsize=14)
    plt.tight_layout()

    output_path = os.path.join(output_dir, f"dataset_characteristics_{timestamp}.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    return output_path


def generate_model_performance_heatmap(
    datasets: Dict[str, Dict],
    metric: str,
    output_dir: str,
    timestamp: str
) -> str:
    """
    Heatmap of model performance by dataset for a single metric.

    Returns: Path to saved PNG file.
    """
    if not MATPLOTLIB_AVAILABLE or not PANDAS_AVAILABLE:
        print("Warning: matplotlib/pandas not available, skipping performance heatmap")
        return ""

    os.makedirs(output_dir, exist_ok=True)

    all_models = get_all_models(datasets)
    dataset_names = sorted(datasets.keys())

    matrix = []
    for model_name in all_models:
        row = []
        for ds_name in dataset_names:
            ds_data = datasets.get(ds_name, {})
            score = ds_data.get("models", {}).get(model_name, {}).get("metrics", {}).get(metric)
            row.append(score if score is not None else np.nan)
        matrix.append(row)

    df = pd.DataFrame(matrix, index=[m.split("/")[-1] for m in all_models], columns=dataset_names)

    fig, ax = plt.subplots(figsize=(max(10, len(dataset_names) * 1.2), max(6, len(all_models) * 0.4)))
    im = ax.imshow(df.values, cmap=AGG_HEATMAP_CMAP, aspect='auto', vmin=0, vmax=1)

    ax.set_xticks(np.arange(len(dataset_names)))
    ax.set_yticks(np.arange(len(all_models)))
    ax.set_xticklabels(dataset_names)
    ax.set_yticklabels(df.index)
    ax.tick_params(axis='both', labelsize=HEATMAP_TICK_SIZE)
    ax.tick_params(axis='both', labelsize=HEATMAP_TICK_SIZE)

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    for i in range(len(all_models)):
        for j in range(len(dataset_names)):
            if not np.isnan(df.values[i, j]):
                ax.text(
                    j, i, f"{df.values[i, j]:.3f}",
                    ha="center", va="center", color="black", fontsize=HEATMAP_ANNOT_SIZE
                )

    ax.set_title(
        f"Model Performance Heatmap ({metric_display_name(metric)})",
        fontsize=HEATMAP_TITLE_SIZE,
        pad=16
    )
    fig.colorbar(im, ax=ax, label=f"{metric_display_name(metric)} Score")

    output_path = os.path.join(output_dir, f"model_performance_heatmap_{metric}_{timestamp}.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    return output_path


def generate_embedding_speed_heatmap(
    datasets: Dict[str, Dict],
    output_dir: str,
    timestamp: str
) -> str:
    """
    Heatmap of embedding throughput (chunks/sec) by model and dataset.

    Returns: Path to saved PNG file.
    """
    if not MATPLOTLIB_AVAILABLE or not PANDAS_AVAILABLE:
        print("Warning: matplotlib/pandas not available, skipping speed heatmap")
        return ""

    os.makedirs(output_dir, exist_ok=True)

    all_models = get_all_models(datasets)
    dataset_names = sorted(datasets.keys())

    matrix = []
    for model_name in all_models:
        row = []
        for ds_name in dataset_names:
            timing = datasets.get(ds_name, {}).get("models", {}).get(model_name, {}).get("timing", {})
            chunks_per_second = timing.get("chunks_per_second")
            row.append(chunks_per_second if isinstance(chunks_per_second, (int, float)) else np.nan)
        matrix.append(row)

    df = pd.DataFrame(matrix, index=[m.split("/")[-1] for m in all_models], columns=dataset_names)

    if df.isna().all().all():
        return ""

    fig, ax = plt.subplots(figsize=(max(10, len(dataset_names) * 1.2), max(6, len(all_models) * 0.4)))
    im = ax.imshow(df.values, cmap=AGG_HEATMAP_CMAP, aspect='auto')

    ax.set_xticks(np.arange(len(dataset_names)))
    ax.set_yticks(np.arange(len(all_models)))
    ax.set_xticklabels(dataset_names)
    ax.set_yticklabels(df.index)

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    for i in range(len(all_models)):
        for j in range(len(dataset_names)):
            if not np.isnan(df.values[i, j]):
                ax.text(
                    j, i, f"{df.values[i, j]:.1f}",
                    ha="center", va="center", color="black", fontsize=HEATMAP_ANNOT_SIZE
                )

    ax.set_title("Embedding Throughput (Chunks/sec)", fontsize=HEATMAP_TITLE_SIZE, pad=16)
    fig.colorbar(im, ax=ax, label="Chunks per Second")

    output_path = os.path.join(output_dir, f"embedding_speed_heatmap_{timestamp}.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    return output_path


def generate_query_latency_heatmap(
    datasets: Dict[str, Dict],
    output_dir: str,
    timestamp: str
) -> str:
    """
    Heatmap of query retrieval latency (ms/query) by model and dataset.
    Lower values are better.

    Returns: Path to saved PNG file.
    """
    if not MATPLOTLIB_AVAILABLE or not PANDAS_AVAILABLE:
        print("Warning: matplotlib/pandas not available, skipping latency heatmap")
        return ""

    os.makedirs(output_dir, exist_ok=True)

    all_models = get_all_models(datasets)
    dataset_names = sorted(datasets.keys())

    matrix = []
    for model_name in all_models:
        row = []
        for ds_name in dataset_names:
            timing = datasets.get(ds_name, {}).get("models", {}).get(model_name, {}).get("timing", {})
            avg_query_latency_ms = timing.get("avg_query_latency_ms")
            row.append(avg_query_latency_ms if isinstance(avg_query_latency_ms, (int, float)) else np.nan)
        matrix.append(row)

    df = pd.DataFrame(matrix, index=[m.split("/")[-1] for m in all_models], columns=dataset_names)

    if df.isna().all().all():
        return ""

    fig, ax = plt.subplots(figsize=(max(10, len(dataset_names) * 1.2), max(6, len(all_models) * 0.4)))
    im = ax.imshow(df.values, cmap=AGG_HEATMAP_CMAP, aspect='auto')

    ax.set_xticks(np.arange(len(dataset_names)))
    ax.set_yticks(np.arange(len(all_models)))
    ax.set_xticklabels(dataset_names)
    ax.set_yticklabels(df.index)

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    for i in range(len(all_models)):
        for j in range(len(dataset_names)):
            if not np.isnan(df.values[i, j]):
                ax.text(
                    j, i, f"{df.values[i, j]:.2f}",
                    ha="center", va="center", color="black", fontsize=HEATMAP_ANNOT_SIZE
                )

    ax.set_title("Query Retrieval Latency (ms/query, lower is better)", fontsize=HEATMAP_TITLE_SIZE, pad=16)
    fig.colorbar(im, ax=ax, label="Avg Query Latency (ms/query)")

    output_path = os.path.join(output_dir, f"query_latency_heatmap_{timestamp}.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    return output_path


def generate_pairwise_significance_heatmap(
    significance_matrix: 'pd.DataFrame',
    output_dir: str,
    timestamp: str,
    alpha: float = 0.05
) -> str:
    """
    Heatmap of p-values with significance indicators.
    Color: White (p>0.05) to Dark Red (p<0.001)
    Annotations: "***" (p<0.001), "**" (p<0.01), "*" (p<0.05), "ns" (not significant)
    
    Returns: Path to saved PNG file.
    """
    if not MATPLOTLIB_AVAILABLE or not PANDAS_AVAILABLE:
        print("Warning: matplotlib/pandas not available, skipping significance heatmap")
        return ""
    
    os.makedirs(output_dir, exist_ok=True)
    
    models = significance_matrix.index.tolist()
    n_models = len(models)
    
    # Set diagonal to vmax for white color
    for i in range(n_models):
        significance_matrix.values[i, i] = alpha * 2
    
    fig, ax = plt.subplots(figsize=(max(10, n_models * 0.8), max(8, n_models * 0.8)))
    
    # Create heatmap
    im = ax.imshow(significance_matrix.values, cmap=AGG_HEATMAP_CMAP, aspect='auto', vmin=0, vmax=alpha*2)
    
    # Set ticks
    ax.set_xticks(np.arange(n_models))
    ax.set_yticks(np.arange(n_models))
    short_names = [m.split("/")[-1] for m in models]
    ax.set_xticklabels(short_names)
    ax.set_yticklabels(short_names)
    ax.tick_params(axis='both', labelsize=HEATMAP_TICK_SIZE)
    
    # Rotate labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Add significance annotations
    for i in range(n_models):
        for j in range(n_models):
            if i == j:
                text_str = ""
            else:
                p_val = significance_matrix.values[i, j]
                
                if np.isnan(p_val):
                    text_str = ""
                else:
                    text_str = f"{p_val:.3f}"
            
            text = ax.text(
                j, i, text_str, ha="center", va="center",
                color="black", fontweight='bold', fontsize=HEATMAP_ANNOT_SIZE
            )
    
    ax.set_title(
        f"Pairwise Statistical Significance (alpha={alpha})",
        fontsize=HEATMAP_TITLE_SIZE,
        pad=20
    )
    fig.colorbar(im, ax=ax, label='p-value')
    
    output_path = os.path.join(output_dir, f"pairwise_significance_heatmap_{timestamp}.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path


def generate_consistency_comparison_chart(
    consistency_scores: Dict[str, Dict],
    output_dir: str,
    timestamp: str
) -> str:
    """
    Grouped bar chart comparing consistency metrics across models.
    Groups: coefficient_of_variation, worst_case_drop
    
    Returns: Path to saved PNG file.
    """
    if not MATPLOTLIB_AVAILABLE:
        print("Warning: matplotlib not available, skipping consistency chart")
        return ""
    
    os.makedirs(output_dir, exist_ok=True)
    
    models = list(consistency_scores.keys())
    short_names = [m.split("/")[-1] for m in models]
    
    cv_values = [consistency_scores[m].get("coefficient_of_variation", 0) for m in models]
    drop_values = [consistency_scores[m].get("worst_case_drop", 0) for m in models]
    
    x = np.arange(len(models))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(max(10, len(models) * 0.8), 6))
    
    bars1 = ax.bar(x - width/2, cv_values, width, label='Coefficient of Variation', alpha=0.8)
    bars2 = ax.bar(x + width/2, drop_values, width, label='Worst Case Drop', alpha=0.8)
    
    ax.set_xlabel('Model', fontsize=12)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Model Consistency Across Datasets', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(short_names, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    output_path = os.path.join(output_dir, f"consistency_comparison_{timestamp}.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path


# ============================================================================
# Main Report Generation Function
# ============================================================================

def generate_aggregate_report(
    dataset_names: List[str] = None,
    output_dir: str = None,
    metrics: List[str] = None,
    generate_pdf: bool = False
) -> str:
    """
    Generate comprehensive cross-dataset comparison report.
    
    Args:
        dataset_names: Datasets to include (None = auto-discover all)
        output_dir: Custom output directory (None = use config.aggregate_results_dir)
        metrics: Metrics to analyze (None = use common metrics across datasets)
        generate_pdf: Convert Markdown to PDF using pandoc
    
    Returns: Path to generated Markdown report
    """
    print("="*80)
    print("GENERATING AGGREGATE CROSS-DATASET REPORT")
    print("="*80)
    
    # Check dependencies
    check_aggregate_dependencies()
    
    # Set output directory
    if output_dir is None:
        # Generate timestamp for this report run
        timestamp = __import__('datetime').datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = os.path.join(cfg.aggregate_results_dir, timestamp)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Load datasets
    print("\n📂 Loading datasets...")
    datasets = load_multiple_datasets(dataset_names)
    
    if not datasets:
        raise ValueError("No datasets loaded. Cannot generate aggregate report.")
    
    print(f"✓ Loaded {len(datasets)} datasets: {', '.join(datasets.keys())}")
    
    # Validate compatibility
    print("\n🔍 Validating metric compatibility...")
    validation = validate_metric_compatibility(datasets)
    
    if validation["status"] == "error":
        raise ValueError(validation.get("message", "Metric validation failed"))
    
    for warning in validation.get("warnings", []):
        print(f"⚠️  {warning}")

    print("\n🔒 Validating config consistency...")
    validate_config_consistency(datasets)
    
    # Determine metrics to analyze
    if metrics is None:
        metrics = get_common_metrics(datasets)
    
    if not metrics:
        raise ValueError("No common metrics found across datasets")
    
    print(f"✓ Analyzing metrics: {', '.join([metric_display_name(m) for m in metrics])}")
    
    # Aggregate model performance
    print("\n📊 Aggregating model performance...")
    model_results = aggregate_model_performance(datasets)
    
    common_models = get_common_models(datasets)
    all_models = get_all_models(datasets)
    
    print(f"✓ Found {len(all_models)} total models, {len(common_models)} common across all datasets")
    
    # Calculate rankings
    primary_metric = metrics[0]  # Use first metric as primary
    heatmap_metric = "map" if "map" in metrics else primary_metric
    rankings = calculate_model_rankings(datasets, primary_metric)
    avg_ranks = calculate_average_ranks(rankings)
    
    # Calculate consistency
    print("\n🔬 Computing consistency scores...")
    consistency = calculate_consistency_scores(model_results)
    
    # Statistical tests
    print("\n📈 Performing statistical analysis...")
    significance_matrix = None
    if cfg.aggregate_statistical_tests and len(datasets) >= 2:
        significance_matrix = perform_pairwise_significance_tests(datasets, primary_metric)
        print(f"✓ Computed pairwise significance tests for {metric_display_name(primary_metric)}")
    
    friedman_stat, friedman_p = perform_friedman_test(datasets, primary_metric)
    
    # Generate timestamp for files
    timestamp = __import__('datetime').datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Generate visualizations
    print("\n🎨 Generating visualizations...")
    viz_paths = {}
    
    if cfg.aggregate_generate_visualizations and MATPLOTLIB_AVAILABLE:
        try:
            viz_paths["radar"] = generate_cross_dataset_radar_chart(model_results, metrics, output_dir, timestamp)
            print("  ✓ Radar chart")
        except Exception as e:
            print(f"  ⚠️  Radar chart failed: {e}")
        
        try:
            viz_paths["heatmap"] = generate_model_ranking_heatmap(rankings, output_dir, timestamp)
            print("  ✓ Ranking heatmap")
        except Exception as e:
            print(f"  ⚠️  Ranking heatmap failed: {e}")

        try:
            viz_paths["dataset_characteristics"] = generate_dataset_characteristics_chart(datasets, output_dir, timestamp)
            print("  ✓ Dataset characteristics chart")
        except Exception as e:
            print(f"  ⚠️  Dataset characteristics chart failed: {e}")

        try:
            viz_paths[f"performance_heatmap_{heatmap_metric}"] = generate_model_performance_heatmap(
                datasets, heatmap_metric, output_dir, timestamp
            )
            print(f"  ✓ Performance heatmap ({metric_display_name(heatmap_metric)})")
        except Exception as e:
            print(f"  ⚠️  Performance heatmap ({metric_display_name(heatmap_metric)}) failed: {e}")

        try:
            viz_paths["speed_heatmap"] = generate_embedding_speed_heatmap(datasets, output_dir, timestamp)
            if viz_paths["speed_heatmap"]:
                print("  ✓ Embedding speed heatmap")
        except Exception as e:
            print(f"  ⚠️  Embedding speed heatmap failed: {e}")

        try:
            viz_paths["latency_heatmap"] = generate_query_latency_heatmap(datasets, output_dir, timestamp)
            if viz_paths["latency_heatmap"]:
                print("  ✓ Query latency heatmap")
        except Exception as e:
            print(f"  ⚠️  Query latency heatmap failed: {e}")
        
        for metric in metrics:
            try:
                viz_paths[f"dist_{metric}"] = generate_performance_distribution_plots(model_results, metric, output_dir, timestamp)
                print(f"  ✓ Distribution plot ({metric_display_name(metric)})")
            except Exception as e:
                print(f"  ⚠️  Distribution plot ({metric_display_name(metric)}) failed: {e}")
            
            try:
                viz_paths[f"difficulty_{metric}"] = generate_dataset_difficulty_chart(datasets, metric, output_dir, timestamp)
                print(f"  ✓ Difficulty chart ({metric_display_name(metric)})")
            except Exception as e:
                print(f"  ⚠️  Difficulty chart ({metric_display_name(metric)}) failed: {e}")
        
        if significance_matrix is not None:
            try:
                viz_paths["significance"] = generate_pairwise_significance_heatmap(significance_matrix, output_dir, timestamp)
                print("  ✓ Significance heatmap")
            except Exception as e:
                print(f"  ⚠️  Significance heatmap failed: {e}")
        
        try:
            viz_paths["consistency"] = generate_consistency_comparison_chart(consistency, output_dir, timestamp)
            print("  ✓ Consistency chart")
        except Exception as e:
            print(f"  ⚠️  Consistency chart failed: {e}")
    
    # Generate Markdown report
    print("\n📝 Writing report...")
    report_path = os.path.join(output_dir, "aggregate_report.md")
    
    _write_markdown_report(
        report_path=report_path,
        datasets=datasets,
        model_results=model_results,
        rankings=rankings,
        avg_ranks=avg_ranks,
        consistency=consistency,
        significance_matrix=significance_matrix,
        friedman_result=(friedman_stat, friedman_p),
        metrics=metrics,
        viz_paths=viz_paths
    )
    
    print(f"\n✅ Report generated: {report_path}")
    
    # Generate PDF if requested
    if generate_pdf:
        try:
            from utils.report_utils import convert_md_to_pdf
            pdf_path = convert_md_to_pdf(report_path, output_dir)
            if pdf_path:
                print(f"✅ PDF generated: {pdf_path}")
            else:
                print("⚠️  PDF generation failed")
        except ImportError:
            print("⚠️  PDF conversion utility not available")
        except Exception as e:
            print(f"⚠️  PDF generation failed: {e}")
    
    print("="*80)
    
    return report_path


def _write_markdown_report(
    report_path: str,
    datasets: Dict[str, Dict],
    model_results: Dict[str, Dict],
    rankings: Dict[str, List[Tuple[str, int]]],
    avg_ranks: List[Tuple[str, float]],
    consistency: Dict[str, Dict],
    significance_matrix,
    friedman_result: Tuple[float, float],
    metrics: List[str],
    viz_paths: Dict[str, str]
):
    """Write the actual Markdown report content."""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        # Header
        timestamp = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        def _fmt(value, digits=2):
            if isinstance(value, (int, float)) and not np.isnan(value):
                return f"{value:.{digits}f}"
            return "N/A"

        f.write(f"# Cross-Dataset Embedding Model Comparison Report\n\n")
        f.write(f"*Generated: {timestamp}*\n\n")
        f.write(f"---\n\n")
        
        # Executive Summary
        f.write("## Executive Summary\n\n")
        
        # Dataset statistics
        f.write("### Datasets Analyzed\n\n")
        total_pdfs = sum(ds.get("corpus_stats", {}).get("total_pdfs", 0) for ds in datasets.values())
        total_chunks = sum(ds.get("corpus_stats", {}).get("total_chunks", 0) for ds in datasets.values())
        total_queries = sum(ds.get("corpus_stats", {}).get("total_queries", 0) for ds in datasets.values())
        
        for ds_name, ds_data in datasets.items():
            stats = ds_data.get("corpus_stats", {})
            num_pdfs = stats.get('total_pdfs', 0)
            f.write(f"- **{ds_name}**: {num_pdfs} document{'s' if num_pdfs != 1 else ''} (PDFs) → {stats.get('total_chunks', 'N/A')} chunks, ")
            f.write(f"{stats.get('total_queries', 'N/A')} queries, ")
            f.write(f"{stats.get('total_qrels', 'N/A')} qrels\n")
        
        f.write(f"- **Total**: {len(datasets)} datasets, {total_pdfs} document{'s' if total_pdfs != 1 else ''} (PDFs) → {total_chunks} chunks, {total_queries} queries\n\n")
        
        # Best performers
        f.write("### Overall Best Performers (by Average Rank)\n\n")
        for i, (model_name, avg_rank) in enumerate(avg_ranks[:5], 1):
            short_name = model_name.split("/")[-1]
            f.write(f"{i}. **{short_name}** (Avg Rank: {avg_rank:.2f})\n")
            
            # Find best performances
            best_datasets = []
            primary_metric = metrics[0]
            if primary_metric in model_results.get(model_name, {}):
                scores = model_results[model_name][primary_metric]["scores_by_dataset"]
                for ds_name, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]:
                    best_datasets.append(f"{ds_name} ({metric_display_name(primary_metric)}={score:.2f})")
            
            if best_datasets:
                f.write(f"   - Best on: {', '.join(best_datasets)}\n")
            
            # Consistency
            if model_name in consistency:
                cv = consistency[model_name].get("coefficient_of_variation", 0)
                f.write(f"   - Consistency: CV={cv:.3f}\n")
            
            f.write("\n")
        
        # Key findings
        f.write("### Key Findings\n\n")
        
        # Statistical significance highlight
        if significance_matrix is not None and len(avg_ranks) >= 2:
            best_model = avg_ranks[0][0]
            second_model = avg_ranks[1][0]
            
            try:
                p_val = significance_matrix.loc[best_model, second_model]
                if not np.isnan(p_val):
                    effect = calculate_effect_sizes(datasets, best_model, second_model, metrics[0])
                    
                    f.write(f"- **Statistical Significance**: {best_model.split('/')[-1]} ")
                    if p_val < 0.05:
                        f.write(f"significantly outperforms {second_model.split('/')[-1]} ")
                        f.write(f"on {metric_display_name(metrics[0])} across datasets ")
                        f.write(f"(p={p_val:.3f}, Cohen's d={effect['cohens_d']:.2f})\n")
                    else:
                        f.write(f"does not significantly differ from {second_model.split('/')[-1]} ")
                        f.write(f"on {metric_display_name(metrics[0])} (p={p_val:.3f})\n")
            except Exception as e:
                pass
        
        # Dataset difficulty
        primary_metric = metrics[0]
        dataset_means = {}
        for ds_name, ds_data in datasets.items():
            models_data = ds_data.get("models", {})
            scores = [m.get("metrics", {}).get(primary_metric) for m in models_data.values()]
            scores = [s for s in scores if s is not None]
            if scores:
                dataset_means[ds_name] = np.mean(scores)
        
        if len(dataset_means) >= 2:
            easiest = max(dataset_means, key=dataset_means.get)
            hardest = min(dataset_means, key=dataset_means.get)
            f.write(f"- **Dataset Difficulty**: {hardest} dataset is harder ")
            f.write(f"(mean {metric_display_name(primary_metric)}={dataset_means[hardest]:.2f} vs ")
            f.write(f"{easiest}={dataset_means[easiest]:.2f})\n")
        
        # Performance variability
        if consistency and avg_ranks:
            most_consistent_model = min(consistency.items(), key=lambda x: x[1].get("coefficient_of_variation", 1))
            f.write(f"- **Performance Variability**: {most_consistent_model[0].split('/')[-1]} ")
            f.write(f"shows most consistent performance ")
            f.write(f"(CV={most_consistent_model[1].get('coefficient_of_variation', 0):.2f})\n")
        
        f.write("\n---\n\n")
        
        # Methodology
        f.write("## Methodology\n\n")
        f.write("### Evaluation Setup\n\n")
        f.write("- **Retrieval Method**: ChromaDB vector search with cosine similarity\n")
        
        # Get k value from first dataset
        first_ds = list(datasets.values())[0]
        k_val = first_ds.get("config", {}).get("k", "N/A")
        f.write(f"- **k Value**: {k_val} (for all metrics)\n")
        
        chunk_size = first_ds.get("config", {}).get("chunk_size", "N/A")
        chunk_overlap = first_ds.get("config", {}).get("chunk_overlap", "N/A")
        f.write(f"- **Chunking**: {chunk_size} tokens with {chunk_overlap}-token overlap\n")
        f.write(f"- **Metrics Computed**: {', '.join([metric_display_name(m) for m in metrics])}\n\n")
        
        f.write("### Statistical Analysis Methods\n\n")
        f.write(f"- **Paired t-tests**: Comparing models across datasets (alpha={cfg.aggregate_significance_level})\n")
        f.write("- **Effect Size**: Cohen's d for practical significance\n")
        f.write("- **Consistency Metrics**: Coefficient of variation, worst-case drop\n")
        
        if friedman_result[0] and not np.isnan(friedman_result[0]):
            f.write(f"- **Friedman Test**: chi-squared={friedman_result[0]:.2f}, p={friedman_result[1]:.3f}\n")
        
        f.write("\n---\n\n")

        # Dataset characteristics
        heatmap_metric = "map" if "map" in metrics else metrics[0]
        f.write("## Dataset Characteristics\n\n")
        
        from tabulate import tabulate
        
        dataset_rows = []
        total_pdfs = 0
        total_chunks = 0
        total_queries = 0
        total_qrels = 0

        for ds_name, ds_data in datasets.items():
            stats = ds_data.get("corpus_stats", {})
            pdfs = int(stats.get("total_pdfs", 0))
            chunks = int(stats.get("total_chunks", 0))
            queries = int(stats.get("total_queries", 0))
            qrels = int(stats.get("total_qrels", 0))

            total_pdfs += pdfs
            total_chunks += chunks
            total_queries += queries
            total_qrels += qrels

            dataset_rows.append([ds_name, pdfs, chunks, queries, qrels])

        dataset_rows.append(["Total", total_pdfs, total_chunks, total_queries, total_qrels])

        f.write(tabulate(
            dataset_rows,
            headers=["Dataset", "Documents (PDFs)", "Chunks", "Queries", "Qrels"],
            tablefmt="pipe"
        ))
        f.write("\n\n")
        f.write("**Table: Dataset Statistics Summary**\n\n")
        f.write("**Column Explanations:**\n")
        f.write("- **Dataset**: Dataset identifier used in the benchmark\n")
        f.write("- **Documents (PDFs)**: Number of source documents (PDF files)\n")
        f.write("- **Chunks**: Total text chunks created from documents (PDFs)\n")
        f.write("- **Queries**: Number of evaluation queries generated\n")
        f.write("- **Qrels**: Number of relevance judgments (query-document labels)\n\n")
        f.write("**How to interpret:**\n")
        f.write("- **More chunks** generally indicate larger corpora and higher retrieval complexity\n")
        f.write("- **More queries and qrels** increase evaluation coverage and statistical power\n\n")

        detail_rows = []
        avg_chunk_vals = []
        avg_query_vals = []
        avg_rel_vals = []
        coverage_vals = []

        for ds_name, ds_data in datasets.items():
            corpus_chars = ds_data.get("corpus_characteristics", {})
            query_chars = ds_data.get("query_characteristics", {})
            relevance_chars = ds_data.get("relevance_characteristics", {})

            avg_chunk = corpus_chars.get("avg_chunk_length")
            avg_query = query_chars.get("avg_query_length")
            avg_rel = relevance_chars.get("avg_relevant_docs_per_query")
            coverage = relevance_chars.get("coverage_ratio")

            if isinstance(avg_chunk, (int, float)):
                avg_chunk_vals.append(avg_chunk)
            if isinstance(avg_query, (int, float)):
                avg_query_vals.append(avg_query)
            if isinstance(avg_rel, (int, float)):
                avg_rel_vals.append(avg_rel)
            if isinstance(coverage, (int, float)):
                coverage_vals.append(coverage)

            detail_rows.append([
                ds_name,
                _fmt(avg_chunk, 1),
                _fmt(avg_query, 1),
                _fmt(avg_rel, 1),
                f"{_fmt(coverage, 2)}%"
            ])

        if viz_paths.get("dataset_characteristics"):
            f.write(f"![Dataset Characteristics Overview]({os.path.basename(viz_paths['dataset_characteristics'])})\n\n")
            f.write("**Figure: Dataset Characteristics Overview**\n\n")
            f.write("This figure compares dataset size indicators (documents (PDFs), chunks, queries, qrels) across all datasets.\n\n")

        if detail_rows:
            detail_rows.append([
                "Average",
                _fmt(np.mean(avg_chunk_vals) if avg_chunk_vals else None, 1),
                _fmt(np.mean(avg_query_vals) if avg_query_vals else None, 1),
                _fmt(np.mean(avg_rel_vals) if avg_rel_vals else None, 1),
                f"{_fmt(np.mean(coverage_vals) if coverage_vals else None, 2)}%"
            ])

            f.write(tabulate(
                detail_rows,
                headers=["Dataset", "Avg Chunk Length (words)", "Avg Query Length (words)", "Avg Relevant Documents", "Coverage Ratio"],
                tablefmt="pipe"
            ))
            f.write("\n\n")
            f.write("**Table: Aggregated Dataset Characteristics**\n\n")

        f.write("---\n\n")
        
        # Cross-Dataset Model Comparison
        f.write("## Cross-Dataset Model Comparison\n\n")
        f.write(f"### Overall Performance Rankings (by {metric_display_name(metrics[0])})\n\n")
        
        # Create ranking table
        
        table_data = []
        for model_name, avg_rank in avg_ranks:
            short_name = model_name.split("/")[-1]
            
            primary_stats = model_results.get(model_name, {}).get(metrics[0], {})
            mean_score = primary_stats.get("mean", 0)
            std_score = primary_stats.get("std", 0)
            cv = consistency.get(model_name, {}).get("coefficient_of_variation", 0)
            
            # Count datasets where this model is #1
            wins = sum(1 for ds_rankings in rankings.values() 
                      if ds_rankings and ds_rankings[0][0] == model_name)
            
            table_data.append([
                short_name,
                f"{avg_rank:.2f}",
                f"{mean_score:.4f}",
                f"{std_score:.4f}",
                f"{cv:.3f}",
                wins
            ])
        
        f.write(tabulate(table_data, 
                        headers=["Model", "Avg Rank", f"Mean {metric_display_name(metrics[0])}", "Std", "CV", "Datasets Won"],
                        tablefmt="github"))
        f.write("\n\n")
        
        f.write("**Table: Cross-Dataset Model Performance Summary**\n\n")
        f.write("**Column Explanations:**\n")
        f.write("- **Avg Rank**: Average ranking position across datasets (1.0 = best overall)\n")
        f.write(f"- **Mean {metric_display_name(metrics[0])}**: Average {metric_display_name(metrics[0])} score across all datasets\n")
        f.write("- **Std**: Standard deviation of performance across datasets\n")
        f.write("- **CV**: Coefficient of variation (Std/Mean) - measures relative consistency\n")
        f.write("- **Datasets Won**: Number of datasets where this model ranked #1\n\n")
        
        f.write("**How to use this table:**\n")
        f.write("- **Sort by Avg Rank**: Identifies the most reliable models overall\n")
        f.write("- **Check CV values**: Lower CV indicates more consistent performance\n")
        f.write("- **Compare Mean vs Std**: High mean with low std = reliable excellence\n")
        f.write("- **Datasets Won**: Shows how often a model is the best choice\n\n")

        f.write(f"### Model Performance by Dataset ({metric_display_name(heatmap_metric)})\n\n")

        if viz_paths.get(f"performance_heatmap_{heatmap_metric}"):
            f.write(
                f"![Model Performance Heatmap]({os.path.basename(viz_paths[f'performance_heatmap_{heatmap_metric}'])})\n\n"
            )
            f.write("**Figure: Model Performance by Dataset**\n\n")
            f.write(
                f"This heatmap shows {metric_display_name(heatmap_metric)} scores for each model across all datasets. "
                "Darker colors indicate lower scores (weaker performance).\n\n"
            )

        dataset_names = sorted(datasets.keys())
        all_models = get_all_models(datasets)
        perf_rows = []
        for model_name in all_models:
            row = [model_name.split("/")[-1]]
            for ds_name in dataset_names:
                score = datasets.get(ds_name, {}).get("models", {}).get(model_name, {}).get("metrics", {}).get(heatmap_metric)
                row.append(_fmt(score, 4) if isinstance(score, (int, float)) else "N/A")
            perf_rows.append(row)

        if dataset_names and perf_rows:
            f.write(tabulate(
                perf_rows,
                headers=["Model"] + dataset_names,
                tablefmt="github"
            ))
            f.write("\n\n")

        f.write("### Embedding Speed Comparison (Chunks/sec)\n\n")

        if viz_paths.get("speed_heatmap"):
            f.write(f"![Embedding Speed Heatmap]({os.path.basename(viz_paths['speed_heatmap'])})\n\n")
            f.write("**Figure: Embedding Throughput by Dataset**\n\n")
            f.write("This heatmap compares embedding throughput in chunks per second across datasets.\n\n")

        speed_rows = []
        for model_name in all_models:
            row = [model_name.split("/")[-1]]
            for ds_name in dataset_names:
                timing = datasets.get(ds_name, {}).get("models", {}).get(model_name, {}).get("timing", {})
                chunks_per_second = timing.get("chunks_per_second")
                row.append(_fmt(chunks_per_second, 1) if isinstance(chunks_per_second, (int, float)) else "N/A")
            speed_rows.append(row)

        if dataset_names and speed_rows:
            f.write(tabulate(
                speed_rows,
                headers=["Model"] + dataset_names,
                tablefmt="github"
            ))
            f.write("\n\n")

        f.write("### Query Retrieval Latency Comparison (ms/query)\n\n")
        f.write("Lower values are better. Latency is measured during `collection.query(...)` only.\n\n")

        if viz_paths.get("latency_heatmap"):
            f.write(f"![Query Latency Heatmap]({os.path.basename(viz_paths['latency_heatmap'])})\n\n")
            f.write("**Figure: Query Retrieval Latency by Dataset**\n\n")
            f.write("This heatmap compares average retrieval latency in ms/query across datasets (lower is better).\n\n")

        latency_matrix = extract_query_latency_matrix(datasets)
        latency_rows = []
        for model_name in all_models:
            row = [model_name.split("/")[-1]]
            model_latency = latency_matrix.get(model_name, {})
            for ds_name in dataset_names:
                latency = model_latency.get(ds_name)
                row.append(_fmt(latency, 2) if isinstance(latency, (int, float)) else "N/A")
            latency_rows.append(row)

        if dataset_names and latency_rows:
            f.write(tabulate(
                latency_rows,
                headers=["Model"] + dataset_names,
                tablefmt="github"
            ))
            f.write("\n\n")

        latency_summary = compute_weighted_query_latency_summary(datasets)
        summary_rows = []
        for model_name in all_models:
            stats = latency_summary.get(model_name, {})
            weighted = stats.get("weighted_mean_latency_ms")
            summary_rows.append([
                model_name.split("/")[-1],
                _fmt(weighted, 2) if isinstance(weighted, (int, float)) else "N/A",
                _fmt(stats.get("best_latency_ms"), 2) if isinstance(stats.get("best_latency_ms"), (int, float)) else "N/A",
                _fmt(stats.get("worst_latency_ms"), 2) if isinstance(stats.get("worst_latency_ms"), (int, float)) else "N/A",
                f"{int(stats.get('datasets_with_latency_data', 0))}",
                f"{int(stats.get('total_queries_timed', 0))}",
            ])

        summary_rows.sort(
            key=lambda row: float(row[1]) if row[1] != "N/A" else float("inf")
        )

        if summary_rows:
            f.write(tabulate(
                summary_rows,
                headers=[
                    "Model",
                    "Weighted Mean Latency (ms/query)",
                    "Best (Min)",
                    "Worst (Max)",
                    "Datasets with Latency Data",
                    "Total Queries Timed",
                ],
                tablefmt="github"
            ))
            f.write("\n\n")
        
        # Add visualization references
        if viz_paths.get("radar"):
            f.write(f"![Cross-Dataset Radar Chart]({os.path.basename(viz_paths['radar'])})\n\n")
            f.write("**Figure: Cross-Dataset Performance Comparison**\n\n")
            f.write("This radar chart shows how each embedding model performs across all evaluated metrics (MAP, NDCG, etc.) ")
            f.write("and datasets simultaneously. Each axis represents a different metric, with values normalized to a common scale.\n\n")
            f.write("**How to interpret:**\n")
            f.write("- **Larger area**: Better overall performance across metrics\n")
            f.write("- **Balanced shape**: Consistent performance across different evaluation aspects\n")
            f.write("- **Spiky shape**: Strong in some metrics but weak in others\n")
            f.write("- **Position relative to center**: Distance from center indicates performance level\n\n")
            f.write("**Why it matters:** Identifies models with well-rounded capabilities vs. specialized models, ")
            f.write("helping you choose based on your specific requirements.\n\n")
        
        if viz_paths.get("heatmap"):
            f.write(f"![Model Ranking Heatmap]({os.path.basename(viz_paths['heatmap'])})\n\n")
            f.write("**Figure: Model Rankings Across Individual Datasets**\n\n")
            f.write("This heatmap displays the ranking position (1=best, higher numbers=worse) of each model ")
            f.write("within each dataset. Darker colors indicate better performance (lower ranks).\n\n")
            f.write("**How to interpret:**\n")
            f.write("- **Dark horizontal stripes**: Model performs consistently well across datasets\n")
            f.write("- **Varied colors per model**: Performance varies significantly by dataset\n")
            f.write("- **Light colors**: Model struggles on those specific datasets\n")
            f.write("- **Column patterns**: Reveals which datasets are easier/harder for all models\n\n")
            f.write("**Why it matters:** Shows model reliability across different domains and identifies ")
            f.write("specialized vs. general-purpose models.\n\n")
        
        # Statistical Significance Section
        if significance_matrix is not None:
            f.write("### Statistical Significance Analysis\n\n")
            f.write("This section determines whether observed performance differences between models are ")
            f.write("statistically significant (real differences) rather than random chance.\n\n")
            
            if viz_paths.get("significance"):
                f.write(f"![Pairwise Significance Heatmap]({os.path.basename(viz_paths['significance'])})\n\n")
                f.write("**Figure: Statistical Significance of Performance Differences**\n\n")
                f.write("This heatmap shows p-values from paired t-tests comparing each model pair across all datasets. ")
                f.write("Darker colors indicate more significant differences.\n\n")
                f.write("**Statistical terms explained:**\n")
                f.write("- **p-value**: Probability that observed differences occurred by chance\n")
                f.write("- **alpha**: Significance threshold (0.05 = 5% chance)\n")
                f.write("- **p < 0.05**: Differences are statistically significant\n")
                f.write("- **p >= 0.05**: Differences may be due to random variation\n\n")
                f.write("**How to interpret:**\n")
                f.write("- **Dark cells**: Strong evidence that models truly perform differently\n")
                f.write("- **Light cells**: Models perform similarly (differences likely random)\n")
                f.write("- **Diagonal**: Always white (comparing model to itself)\n\n")
                f.write("**Why it matters:** Ensures you don't choose a model based on noise. ")
                f.write("Only act on differences that are statistically significant.\n\n")
            
            f.write("**Interpretation Guide**: * p<0.05, ** p<0.01, *** p<0.001, ns = not significant\n\n")
        
        f.write("---\n\n")
        
        # Dataset-Specific Insights
        f.write("## Dataset-Specific Analysis\n\n")
        
        for ds_name in sorted(datasets.keys()):
            f.write(f"### {ds_name.capitalize()} Dataset\n\n")
            
            ds_data = datasets[ds_name]
            stats = ds_data.get("corpus_stats", {})
            corpus_chars = ds_data.get("corpus_characteristics", {})
            query_chars = ds_data.get("query_characteristics", {})
            relevance_chars = ds_data.get("relevance_characteristics", {})
            representative_queries = ds_data.get("representative_queries", [])
            best_model_name = None
            best_score_value = None
            
            # Dataset statistics
            total_pdfs = stats.get('total_pdfs', 'N/A')
            f.write(f"- **Documents (PDFs)**: {total_pdfs} original document{'s' if total_pdfs != 1 else ''}\n")
            avg_chunks_per_pdf = stats.get('avg_chunks_per_pdf', None)
            f.write(
                f"- **Chunks**: {stats.get('total_chunks', 'N/A')} text chunks "
                f"(avg {_fmt(avg_chunks_per_pdf, 1)} per document (PDF))\n"
            )
            f.write(f"- **Queries**: {stats.get('total_queries', 'N/A')} queries, ")
            f.write(f"{stats.get('total_qrels', 'N/A')} relevance judgments\n")
            
            # Difficulty assessment
            models_data = ds_data.get("models", {})
            primary_scores = [m.get("metrics", {}).get(metrics[0]) for m in models_data.values()]
            primary_scores = [s for s in primary_scores if s is not None]
            
            if primary_scores:
                mean_perf = np.mean(primary_scores)
                f.write(f"- **Difficulty**: ")
                if mean_perf > 0.7:
                    f.write("Easy ")
                elif mean_perf > 0.5:
                    f.write("Medium ")
                else:
                    f.write("Hard ")
                f.write(f"(mean {metric_display_name(metrics[0])}={mean_perf:.2f} across models)\n")
            
            # Best model for this dataset
            if ds_name in rankings and rankings[ds_name]:
                best_model, best_rank = rankings[ds_name][0]
                best_score = models_data.get(best_model, {}).get("metrics", {}).get(metrics[0], 0)
                best_model_name = best_model.split('/')[-1]
                best_score_value = best_score
                f.write(f"- **Best Model**: {best_model.split('/')[-1]} ")
                f.write(f"({metric_display_name(metrics[0])}={best_score:.4f})\n")
            
            f.write("\n")

            # Corpus characteristics
            f.write("#### Corpus Characteristics\n\n")
            corpus_table = [
                ["Source Documents (PDFs)", f"{stats.get('total_pdfs', 'N/A')}"] ,
                ["Total Chunks", f"{stats.get('total_chunks', 'N/A')}"] ,
                ["Average Chunk Length (words)", _fmt(corpus_chars.get("avg_chunk_length", None), 1)],
                ["Median Chunk Length (words)", _fmt(corpus_chars.get("median_chunk_length", None), 1)],
                ["Min Chunk Length (words)", _fmt(corpus_chars.get("min_chunk_length", None), 0)],
                ["Max Chunk Length (words)", _fmt(corpus_chars.get("max_chunk_length", None), 0)],
                ["Standard Deviation", _fmt(corpus_chars.get("std_chunk_length", None), 1)]
            ]
            f.write(tabulate(corpus_table, headers=["Metric", "Value"], tablefmt="pipe"))
            f.write("\n\n")

            # Query characteristics
            f.write("#### Query Characteristics\n\n")
            query_table = [
                ["Total Queries", f"{query_chars.get('total_queries', 'N/A')}"] ,
                ["Average Query Length (words)", _fmt(query_chars.get("avg_query_length", None), 1)],
                ["Median Query Length (words)", _fmt(query_chars.get("median_query_length", None), 1)],
                ["Min Query Length (words)", _fmt(query_chars.get("min_query_length", None), 0)],
                ["Max Query Length (words)", _fmt(query_chars.get("max_query_length", None), 0)],
                ["Standard Deviation", _fmt(query_chars.get("std_query_length", None), 1)]
            ]
            f.write(tabulate(query_table, headers=["Metric", "Value"], tablefmt="pipe"))
            f.write("\n\n")

            # Relevance distribution
            f.write("#### Relevance Distribution\n\n")
            relevance_table = [
                ["Total Relevance Judgments", f"{relevance_chars.get('total_relevance_judgments', 'N/A')}"] ,
                ["Average Relevant Documents per Query", _fmt(relevance_chars.get("avg_relevant_docs_per_query", None), 1)],
                ["Median Relevant Documents per Query", _fmt(relevance_chars.get("median_relevant_docs_per_query", None), 1)],
                ["Min Relevant Documents", _fmt(relevance_chars.get("min_relevant_docs_per_query", None), 0)],
                ["Max Relevant Documents", _fmt(relevance_chars.get("max_relevant_docs_per_query", None), 0)],
                ["Coverage Ratio", f"{_fmt(relevance_chars.get('coverage_ratio', None), 2)}%"]
            ]
            f.write(tabulate(relevance_table, headers=["Metric", "Value"], tablefmt="pipe"))
            f.write("\n\n")

            # Representative queries
            if representative_queries:
                f.write("#### Representative Query Examples\n\n")
                query_rows = []
                for item in representative_queries:
                    query_rows.append([
                        item.get("query_id", "N/A"),
                        item.get("query_text", ""),
                        item.get("relevant_docs", "N/A")
                    ])
                f.write(tabulate(query_rows, headers=["Query ID", "Query Text", "# Relevant Documents"], tablefmt="pipe"))
                f.write("\n\n")

            # Model performance metrics
            f.write("#### Embedding Performance Metrics\n\n")
            models_data = ds_data.get("models", {})
            metric_headers = ["Model"] + [f"{metric_header_name(m)}@{k_val}" for m in metrics]
            metric_rows = []
            for model_name, model_data in sorted(models_data.items()):
                short_name = model_name.split("/")[-1]
                row = [short_name]
                for metric in metrics:
                    score = model_data.get("metrics", {}).get(metric)
                    row.append(_fmt(score, 4) if isinstance(score, (int, float)) else "N/A")
                metric_rows.append(row)
            f.write(tabulate(metric_rows, headers=metric_headers, tablefmt="pipe"))
            f.write("\n\n")

            # Compute and retrieval timing
            f.write("#### Compute and Retrieval Timing\n\n")
            timing_rows = []
            for model_name, model_data in sorted(models_data.items()):
                timing = model_data.get("timing", {})
                if not isinstance(timing, dict):
                    continue

                embedding_time = timing.get("embedding_time")
                chunks_processed = timing.get("chunks_processed")
                chunks_per_second = timing.get("chunks_per_second")
                avg_time_per_chunk = timing.get("avg_time_per_chunk")
                avg_query_latency_ms = timing.get("avg_query_latency_ms")
                queries_timed = timing.get("queries_timed")

                has_embedding_data = all(
                    isinstance(value, (int, float))
                    for value in (embedding_time, chunks_per_second, avg_time_per_chunk)
                )
                has_latency_data = isinstance(avg_query_latency_ms, (int, float)) and isinstance(queries_timed, (int, float))

                if not (has_embedding_data or has_latency_data):
                    continue

                timing_rows.append([
                    model_name.split("/")[-1],
                    _fmt(embedding_time, 2) if has_embedding_data else "N/A",
                    f"{int(chunks_processed)}" if isinstance(chunks_processed, (int, float)) else "N/A",
                    _fmt(chunks_per_second, 2) if has_embedding_data else "N/A",
                    _fmt((avg_time_per_chunk or 0) * 1000, 2) if has_embedding_data else "N/A",
                    _fmt(avg_query_latency_ms, 2) if has_latency_data else "N/A",
                    f"{int(queries_timed)}" if has_latency_data else "N/A",
                ])
            if timing_rows:
                f.write(tabulate(
                    timing_rows,
                    headers=[
                        "Model",
                        "Embedding Time (s)",
                        "Chunks Processed",
                        "Chunks/sec",
                        "Avg Time per Chunk (ms)",
                        "Avg Query Latency (ms/query)",
                        "Queries Timed",
                    ],
                    tablefmt="pipe"
                ))
                f.write("\n\n")
            else:
                f.write("No timing data available for this dataset.\n\n")

            mean_metric = np.mean(primary_scores) if primary_scores else None
            summary_items = []
            if best_model_name:
                summary_items.append(
                    f"Best model: {best_model_name} ({metric_display_name(metrics[0])}={_fmt(best_score_value, 4)})"
                )
            if mean_metric is not None:
                summary_items.append(
                    f"Mean {metric_display_name(metrics[0])} across models: {_fmt(mean_metric, 4)}"
                )
            if timing_rows:
                summary_items.append(f"Timing data available for {len(timing_rows)} model(s)")
            else:
                summary_items.append("Timing data not available for this dataset")

            f.write("#### Dataset Summary Notes\n\n")
            for item in summary_items:
                f.write(f"- {item}\n")
            f.write("\n")
        
        # Add difficulty chart
        if viz_paths.get(f"difficulty_{metrics[0]}"):
            f.write(f"![Dataset Difficulty Analysis]({os.path.basename(viz_paths[f'difficulty_{metrics[0]}'])})\n\n")
            f.write("**Figure: Dataset Difficulty Assessment**\n\n")
            f.write(f"This chart shows the average {metric_display_name(metrics[0])} performance across all models for each dataset. ")
            f.write("Higher bars indicate easier datasets (better overall performance), lower bars indicate harder datasets.\n\n")
            f.write("**How to interpret:**\n")
            f.write("- **Tall bars**: Datasets where models perform well overall (easier retrieval tasks)\n")
            f.write("- **Short bars**: Datasets where all models struggle (harder retrieval tasks)\n")
            f.write("- **Consistent heights**: Similar difficulty across datasets\n")
            f.write("- **Variable heights**: Some datasets are much harder than others\n\n")
            f.write("**Why it matters:** Identifies which datasets are good benchmarks and helps explain ")
            f.write("why some models might appear better (they excel on easier datasets).\n\n")
        
        # Dataset Summary Table
        f.write("### Dataset Summary\n\n")
        
        dataset_summary = []
        for ds_name in sorted(datasets.keys()):
            ds_data = datasets[ds_name]
            stats = ds_data.get("corpus_stats", {})
            
            # Find best model for this dataset
            if ds_name in rankings and rankings[ds_name]:
                best_model = rankings[ds_name][0][0]
                best_score = ds_data.get("models", {}).get(best_model, {}).get("metrics", {}).get(metrics[0], 0)
            else:
                best_model = "N/A"
                best_score = 0
            
            # Calculate difficulty (inverse of average performance)
            models_data = ds_data.get("models", {})
            scores = [m.get("metrics", {}).get(metrics[0]) for m in models_data.values()]
            scores = [s for s in scores if s is not None]
            avg_score = np.mean(scores) if scores else 0
            difficulty = 1 - avg_score if avg_score > 0 else 0  # Higher = harder
            
            dataset_summary.append([
                ds_name,
                best_model.split("/")[-1] if best_model != "N/A" else "N/A",
                f"{best_score:.4f}",
                len(models_data),
                f"{difficulty:.2f}"
            ])
        
        f.write(tabulate(dataset_summary, 
                        headers=["Dataset", "Best Model", f"Top {metric_display_name(metrics[0])}", "Models Tested", "Difficulty"],
                        tablefmt="github"))
        f.write("\n\n")
        
        f.write("**Table: Dataset Performance Summary**\n\n")
        f.write("**Column Explanations:**\n")
        f.write("- **Dataset**: Name of the dataset evaluated\n")
        f.write("- **Best Model**: The embedding model that achieved the highest score\n")
        f.write(f"- **Top {metric_display_name(metrics[0])}**: The highest {metric_display_name(metrics[0])} score achieved on this dataset\n")
        f.write("- **Models Tested**: Number of embedding models evaluated\n")
        f.write("- **Difficulty**: Relative difficulty score (higher = more challenging)\n\n")
        
        f.write("**How to use this table:**\n")
        f.write("- **Identify dataset characteristics**: Easy datasets have high top scores, hard ones have low scores\n")
        f.write("- **Model selection guidance**: See which models excel on specific dataset types\n")
        f.write("- **Benchmark planning**: Use difficulty scores to prioritize dataset development\n\n")
        
        f.write("---\n\n")
        
        # Consistency Analysis
        f.write("## Model Consistency Across Datasets\n\n")
        f.write("This section measures how reliably each model performs across different datasets. ")
        f.write("A consistent model delivers similar performance regardless of the domain.\n\n")
        
        if viz_paths.get("consistency"):
            f.write(f"![Consistency Comparison Chart]({os.path.basename(viz_paths['consistency'])})\n\n")
            f.write("**Figure: Model Performance Consistency**\n\n")
            f.write("This bar chart shows two key consistency metrics for each model:\n")
            f.write("- **Coefficient of Variation (CV)**: Standard deviation divided by mean (lower = more consistent)\n")
            f.write("- **Worst Case Drop**: Maximum performance decrease from best to worst dataset\n\n")
            f.write("**How to interpret:**\n")
            f.write("- **Low CV values**: Model performs similarly across all datasets (reliable)\n")
            f.write("- **High CV values**: Performance varies greatly by dataset (unreliable)\n")
            f.write("- **Small worst-case drop**: Model maintains good performance even on hardest datasets\n")
            f.write("- **Large worst-case drop**: Model fails badly on some datasets\n\n")
            f.write("**Why it matters:** For production use, choose models that are consistent across domains ")
            f.write("rather than models that excel on only specific types of content.\n\n")
        
        f.write("### Detailed Consistency Metrics\n\n")
        
        cons_table = []
        for model_name in avg_ranks[:10]:  # Top 10 models
            model = model_name[0]
            short_name = model.split("/")[-1]
            cons = consistency.get(model, {})
            
            cons_table.append([
                short_name,
                f"{cons.get('coefficient_of_variation', 0):.3f}",
                f"{cons.get('worst_case_drop', 0):.3f}",
                f"{cons.get('score_range', 0):.3f}"
            ])
        
        f.write(tabulate(cons_table,
                        headers=["Model", "CV", "Worst Drop", "Score Range"],
                        tablefmt="github"))
        f.write("\n\n")
        
        f.write("**Table: Consistency Metrics Explanation**\n\n")
        f.write("**Coefficient of Variation (CV)**: Measures relative variability. CV < 0.15 indicates good consistency, ")
        f.write("CV > 0.30 indicates high variability.\n\n")
        f.write("**Worst Case Drop**: Maximum performance decrease from best to worst dataset. ")
        f.write("Values > 0.3 indicate significant performance degradation on some datasets.\n\n")
        f.write("**Score Range**: Total spread between best and worst dataset performance. ")
        f.write("Smaller ranges indicate more reliable models.\n\n")
        
        f.write("---\n\n")
        
        # Recommendations
        f.write("## Recommendations\n\n")
        f.write("### For Production Deployment\n\n")
        
        if avg_ranks:
            best_model = avg_ranks[0]
            f.write(f"1. **General Purpose**: Use {best_model[0].split('/')[-1]}\n")
            f.write(f"   - Best overall performance (avg rank {best_model[1]:.2f})\n")
            
            if best_model[0] in consistency:
                cv = consistency[best_model[0]].get("coefficient_of_variation", 0)
                if cv < 0.2:
                    f.write(f"   - Excellent consistency across domains (CV={cv:.2f})\n")
            
            if best_model[0] in model_results and metrics[0] in model_results[best_model[0]]:
                mean_score = model_results[best_model[0]][metrics[0]]["mean"]
                f.write(f"   - Strong performance (mean {metric_display_name(metrics[0])}={mean_score:.4f})\n")
        
        f.write("\n### Limitations\n\n")
        f.write(f"- Evaluation limited to {len(datasets)} datasets\n")
        f.write(f"- Single k value ({k_val}) - performance may vary at different k\n")
        f.write("- All datasets are document retrieval tasks\n")
        f.write("- Statistical power limited by number of datasets\n\n")
        
        f.write("---\n\n")
        
        # Appendix
        f.write("## Appendix\n\n")
        f.write("### A. Raw Data References\n\n")
        
        for ds_name in sorted(datasets.keys()):
            raw_path = cfg.get_latest_raw_results(ds_name)
            if raw_path:
                f.write(f"- **{ds_name}**: `{raw_path}`\n")
        
        f.write("\n### B. Configuration\n\n")
        f.write(f"- Significance Level: alpha = {cfg.aggregate_significance_level}\n")
        f.write(f"- Minimum Datasets Required: {cfg.aggregate_min_datasets}\n")
        f.write(f"- Statistical Tests Enabled: {cfg.aggregate_statistical_tests}\n")
        f.write(f"- Visualizations Enabled: {cfg.aggregate_generate_visualizations}\n")
        
        f.write("\n---\n\n")
        f.write("*Report generated by RagRetrievalBench Aggregate Reporting System*\n")

