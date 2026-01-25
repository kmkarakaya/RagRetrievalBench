# Aggregate Cross-Dataset Report Generation Plan (Revised)

## Overview

This plan implements aggregate reporting functionality to compare embedding model performance across multiple datasets, enabling publication-ready analysis for conference papers. The system consolidates individual dataset results into comprehensive cross-dataset statistical comparisons while preserving existing single-dataset workflows.

## Current Architecture Analysis (Verified)

### Core Components

- **`rag_benchmark.py`**: Main CLI orchestrator with dataset selection and batch processing
- **`config.py`**: Central configuration with `configure_for_dataset(name)` for dynamic path management
- **`utils/chromadb_utils.py`**: Evaluation logic returning fixed metric tuples at indices `(0:model_name, 1:MAP, 2:Recall, 3:Precision, 4:NDCG, 5:MRR)`
- **`utils/report_utils.py`**: Individual dataset reports with Markdown + visualizations (overview charts, per-metric charts, corpus stats, timing analysis)
- **`utils/document_loader.py`**: JSONL/TSV data loading with error handling
- **Multi-dataset isolation**: Separate `datasets/{name}/` directories with prefixed ChromaDB collections

### Key Characteristics (Critical Constraints)

- **Fixed metric tuple ordering**: `evaluate_with_chromadb()` returns `(MAP, Recall, Precision, NDCG, MRR)` at indices 1-5 (model_name at 0)
- **Dynamic metric display**: Config flags (`compute_map`, `compute_recall`, etc.) control report display, NOT computation (all metrics always computed)
- **Config-driven paths**: All file operations use `cfg.*` variables; never hardcode paths
- **Separate timing data lifecycle**: `timing_data_{timestamp}.json` stored/loaded independently from metrics
- **Dataset name extraction**: From directory structure `datasets/{name}/reports/` for report naming
- **Batch processing**: Google Gemini Batch API for cost-effective LLM operations

## Implementation Plan

### Phase 1: Raw Data Storage Enhancement

#### 1.1 JSON Result Storage in `utils/report_utils.py`

**Objective**: Persist structured evaluation results alongside existing reports for aggregate analysis without re-running evaluations.

**Implementation Location**: Modify `generate_benchmark_report()` in `utils/report_utils.py` (NOT `chromadb_utils.py` to maintain separation of concerns).

**Changes**:

- Add `save_raw_results: bool = True` parameter to `generate_benchmark_report()`
- Call new `save_raw_results_json()` function after report generation
- Leverage existing timing data loading pattern from `timing_data_{timestamp}.json`

**Storage Location**: `datasets/{dataset_name}/reports/raw_results_{timestamp}.json`

**JSON Structure** (aligned with existing data patterns):

```json
{
  "dataset": "education",
  "timestamp": "2026-01-25_14-30-00",
  "config": {
    "k": 10,
    "chunk_size": 512,
    "chunk_overlap": 50,
    "metric_flags": {
      "compute_map": true,
      "compute_recall": true,
      "compute_precision": true,
      "compute_ndcg": true,
      "compute_mrr": true
    }
  },
  "models": {
    "sentence-transformers/all-MiniLM-L6-v2": {
      "metrics": {
        "map": 0.7999,
        "recall": 1.0000,
        "precision": 0.4200,
        "ndcg": 0.9092,
        "mrr": 1.0000
      },
      "timing": {
        "embedding_time": 4.366600036621094,
        "docs_processed": 189,
        "docs_per_second": 43.28310319583324,
        "avg_time_per_doc": 0.023103703897466105
      }
    },
    "sentence-transformers/all-mpnet-base-v2": {
      "metrics": {
        "map": 0.4328,
        "recall": 0.8056,
        "precision": 0.3200,
        "ndcg": 0.5936,
        "mrr": 0.5333
      },
      "timing": {
        "embedding_time": 49.57649540901184,
        "docs_processed": 189,
        "docs_per_second": 3.812290450156431,
        "avg_time_per_doc": 0.2623094995185812
      }
    }
  },
  "corpus_stats": {
    "total_documents": 189,
    "total_chunks": 2945,
    "avg_chunks_per_doc": 15.58,
    "total_queries": 36,
    "total_qrels": 72,
    "avg_qrels_per_query": 2.0
  }
}
```

**Key Design Decisions**:

- **Dict structure for models** (not list): Easier lookup and merging across datasets
- **Include timing from existing JSON**: Merge timing data loaded from `timing_data_{timestamp}.json`
- **Corpus stats from document_loader**: Reuse `load_corpus()`, `load_queries()`, `load_qrels()` to compute stats
- **Preserve metric flags**: Critical for normalization in Phase 2

**Function Signature**:

```python
def save_raw_results_json(
    dataset_name: str,
    model_results: List[Tuple],  # Existing format from evaluate_with_chromadb
    timing_data: Dict[str, Dict],  # Loaded from timing_data_{timestamp}.json
    corpus_stats: Dict[str, Any],
    output_path: str
) -> None:
    """Save structured evaluation results for aggregate analysis."""
```

#### 1.2 Configuration Updates in `config.py`

**Objective**: Add aggregate-specific configuration with dataset auto-discovery.

**Changes**:

```python
# Aggregate Reporting Configuration
aggregate_results_dir = "reports/aggregate"  # Root output directory for aggregate reports
aggregate_include_datasets = []  # List of dataset names to include (empty = auto-discover all)
aggregate_exclude_datasets = []  # Datasets to exclude from aggregation
aggregate_statistical_tests = True  # Enable paired t-tests and effect size calculations
aggregate_generate_visualizations = True  # Generate cross-dataset charts
aggregate_significance_level = 0.05  # Alpha for statistical tests (p-value threshold)
aggregate_min_datasets = 2  # Minimum datasets required for aggregation
aggregate_require_identical_metrics = False  # If True, only aggregate datasets with same metric flags
```

**Helper Function** (add to `config.py`):

```python
def discover_available_datasets() -> List[str]:
    """
    Auto-discover datasets in datasets/ directory.
    Returns list of dataset names with valid corpus.jsonl files.
    """
    datasets_root = "datasets"
    if not os.path.exists(datasets_root):
        return []
  
    available = []
    for name in os.listdir(datasets_root):
        dataset_path = os.path.join(datasets_root, name)
        if os.path.isdir(dataset_path):
            corpus_file = os.path.join(dataset_path, "corpus.jsonl")
            if os.path.exists(corpus_file):
                available.append(name)
  
    return sorted(available)
```

**Dataset Path Computation** (add to `config.py`):

```python
def get_latest_raw_results(dataset_name: str) -> Optional[str]:
    """
    Find the most recent raw_results_{timestamp}.json for a dataset.
    Returns absolute path or None if not found.
    """
    reports_dir = os.path.join("datasets", dataset_name, "reports")
    if not os.path.exists(reports_dir):
        return None
  
    raw_files = [f for f in os.listdir(reports_dir) if f.startswith("raw_results_") and f.endswith(".json")]
    if not raw_files:
        return None
  
    # Sort by timestamp in filename (format: raw_results_YYYY-MM-DD_HH-MM-SS.json)
    raw_files.sort(reverse=True)
    return os.path.join(reports_dir, raw_files[0])
```

### Phase 2: Aggregate Analysis Engine

#### 2.1 Core Aggregation Module: `utils/aggregate_report_utils.py`

**Objective**: Create comprehensive cross-dataset analysis with statistical rigor.

**Module Structure**:

##### **Data Loading Functions**

```python
def load_dataset_results(dataset_name: str) -> Optional[Dict]:
    """
    Load most recent raw_results JSON for a dataset.
    Returns None if not found or invalid.
    """
  
def load_multiple_datasets(dataset_names: List[str] = None) -> Dict[str, Dict]:
    """
    Load results for multiple datasets.
    Uses config.discover_available_datasets() if dataset_names is None.
    Validates minimum dataset count (config.aggregate_min_datasets).
    Returns: {"dataset_name": {...raw_results...}, ...}
    """

def validate_metric_compatibility(datasets: Dict[str, Dict]) -> Dict[str, Any]:
    """
    Check metric flag consistency across datasets.
    Returns validation report with warnings/errors.
    If config.aggregate_require_identical_metrics=True, raises error on mismatch.
    """
```

##### **Metric Normalization Functions**

```python
def get_common_metrics(datasets: Dict[str, Dict]) -> List[str]:
    """
    Identify metrics enabled in ALL datasets.
    Returns: ["map", "recall", "ndcg"] (intersection of enabled metrics)
    """

def normalize_model_names(datasets: Dict[str, Dict]) -> Dict[str, str]:
    """
    Handle model name variations across datasets.
    Example: "sentence-transformers/all-MiniLM-L6-v2" vs "all-MiniLM-L6-v2"
    Returns mapping: {normalized_name: canonical_name}
    """

def extract_model_scores_across_datasets(
    datasets: Dict[str, Dict],
    model_name: str,
    metric: str
) -> Dict[str, float]:
    """
    Extract scores for one model/metric across all datasets.
    Returns: {"education": 0.7999, "finance": 0.6543, ...}
    """
```

##### **Aggregation Functions**

```python
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

def calculate_average_ranks(
    rankings: Dict[str, List[Tuple[str, int]]]
) -> List[Tuple[str, float]]:
    """
    Compute mean rank across datasets for each model.
    Used for overall best model determination.
  
    Returns: [("all-MiniLM-L6-v2", 1.33), ("all-mpnet-base-v2", 2.67), ...]
    Sorted by average rank (lower is better).
    """

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
```

##### **Statistical Analysis Functions**

```python
def perform_pairwise_significance_tests(
    datasets: Dict[str, Dict],
    metric: str,
    alpha: float = None  # Uses config.aggregate_significance_level if None
) -> pd.DataFrame:
    """
    Paired t-test for all model pairs across datasets.
    Each dataset provides one paired observation.
  
    Returns DataFrame:
                            all-MiniLM-L6-v2  all-mpnet-base-v2  ...
    all-MiniLM-L6-v2                     -              0.032      ...
    all-mpnet-base-v2                 0.032                  -      ...
  
    Values are p-values (NaN on diagonal, symmetric matrix).
    """

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

def generate_win_tie_loss_matrix(
    datasets: Dict[str, Dict],
    metric: str,
    tie_threshold: float = 0.01  # Difference < 0.01 considered tie
) -> pd.DataFrame:
    """
    Win-Tie-Loss analysis across datasets.
  
    Returns DataFrame showing wins for row model vs column model:
                            all-MiniLM-L6-v2  all-mpnet-base-v2
    all-MiniLM-L6-v2                     -              "2-0-1"
    all-mpnet-base-v2                "1-0-2"                  -
  
    Format: "Wins-Ties-Losses" across datasets.
    """

def perform_friedman_test(
    datasets: Dict[str, Dict],
    metric: str
) -> Tuple[float, float]:
    """
    Friedman test for overall differences across multiple models and datasets.
    Non-parametric alternative to repeated measures ANOVA.
  
    Returns: (chi_square_statistic, p_value)
    """
```

#### 2.2 Visualization Generation Functions

**Objective**: Create publication-ready cross-dataset visualizations following existing matplotlib patterns.

```python
def generate_cross_dataset_radar_chart(
    model_results: Dict[str, Dict],
    metrics: List[str],
    output_dir: str,
    top_n_models: int = 5
) -> str:
    """
    Multi-axis radar chart comparing top models across metrics.
    Each metric axis shows mean score across datasets with error bars (std).
  
    Returns: Path to saved PNG file.
    """

def generate_model_ranking_heatmap(
    rankings: Dict[str, List[Tuple[str, int]]],
    output_dir: str
) -> str:
    """
    Heatmap showing model ranks per dataset.
    Rows: Models, Columns: Datasets, Values: Rank (1=best)
    Color scale: Green (rank 1) to Red (worst rank)
  
    Returns: Path to saved PNG file.
    """

def generate_performance_distribution_plots(
    model_results: Dict[str, Dict],
    metric: str,
    output_dir: str
) -> str:
    """
    Combined box plot + violin plot for score distributions across datasets.
    One subplot per model showing score distribution.
  
    Returns: Path to saved PNG file.
    """

def generate_dataset_difficulty_chart(
    datasets: Dict[str, Dict],
    metric: str,
    output_dir: str
) -> str:
    """
    Bar chart showing mean model performance per dataset.
    Datasets sorted by mean score to identify "easy" vs "hard" datasets.
    Error bars show std across models.
  
    Returns: Path to saved PNG file.
    """

def generate_pairwise_significance_heatmap(
    significance_matrix: pd.DataFrame,
    output_dir: str,
    alpha: float = 0.05
) -> str:
    """
    Heatmap of p-values with significance indicators.
    Color: White (p>0.05) to Dark Red (p<0.001)
    Annotations: "***" (p<0.001), "**" (p<0.01), "*" (p<0.05), "ns" (not significant)
  
    Returns: Path to saved PNG file.
    """

def generate_consistency_comparison_chart(
    consistency_scores: Dict[str, Dict],
    output_dir: str
) -> str:
    """
    Grouped bar chart comparing consistency metrics across models.
    Groups: coefficient_of_variation, rank_stability, worst_case_drop
  
    Returns: Path to saved PNG file.
    """
```

### Phase 3: Report Generation

#### 3.1 Aggregate Report Generator: `generate_aggregate_report()`

**Objective**: Create publication-ready aggregate report in Markdown format.

**Main Function Signature**:

```python
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
```

**Report Structure** (Markdown sections):

##### **1. Executive Summary**

```markdown
# Cross-Dataset Embedding Model Comparison Report
*Generated: 2026-01-25 14:30:00*

## Executive Summary

### Datasets Analyzed
- **education**: 189 documents, 36 queries, 72 qrels
- **finance**: 156 documents, 42 queries, 84 qrels
- **Total**: 2 datasets, 345 documents, 78 queries

### Overall Best Performers (by Average Rank)
1. **sentence-transformers/all-MiniLM-L6-v2** (Avg Rank: 1.5)
   - Best on: education (MAP=0.80), finance (NDCG=0.85)
   - Consistency Score: 0.92 (excellent)
   
2. **sentence-transformers/all-mpnet-base-v2** (Avg Rank: 2.5)
   - Best on: finance (Recall=0.95)
   - Consistency Score: 0.78 (good)

### Key Findings
- **Statistical Significance**: all-MiniLM-L6-v2 significantly outperforms all-mpnet-base-v2 on MAP across datasets (p=0.032, Cohen's d=0.85)
- **Dataset Difficulty**: Finance dataset is harder (mean MAP=0.62 vs education=0.74)
- **Performance Variability**: all-MiniLM-L6-v2 shows most consistent performance (CV=0.12)
```

##### **2. Methodology**

```markdown
## Methodology

### Evaluation Setup
- **Retrieval Method**: ChromaDB vector search with cosine similarity
- **k Value**: 10 (consistent across all datasets)
- **Chunking**: 512 tokens with 50-token overlap
- **Metrics Computed**: MAP, Recall@k, Precision@k, NDCG@k, MRR

### Statistical Analysis Methods
- **Paired t-tests**: Comparing models across datasets (α=0.05)
- **Effect Size**: Cohen's d for practical significance
- **Consistency Metrics**: Coefficient of variation, rank stability
- **Multiple Testing Correction**: Bonferroni correction applied (adjusted α=0.0083 for 6 comparisons)

### Models Evaluated
[Table with model names, parameters, embedding dimensions]
```

##### **3. Cross-Dataset Model Comparison**

```markdown
## Cross-Dataset Model Comparison

### Overall Performance Rankings (by MAP)
[Table showing average ranks, mean scores, std across datasets]

| Model                                  | Avg Rank | Mean MAP | Std | CV   | Datasets Won |
|----------------------------------------|----------|----------|-----|------|--------------|
| sentence-transformers/all-MiniLM-L6-v2 | 1.5      | 0.7271   | 0.08| 0.12 | 1            |
| sentence-transformers/all-mpnet-base-v2| 2.5      | 0.6192   | 0.13| 0.21 | 1            |

### Statistical Significance Matrix (MAP)
[Heatmap visualization + table with p-values]
```

Include:

- Pairwise significance test results table
- Win-Tie-Loss matrix
- Effect size interpretations

##### **4. Metric-Specific Analysis**

```markdown
## Detailed Metric Analysis

### Mean Average Precision (MAP)
[Radar chart, distribution plots, significance heatmap]

**Key Insights**:
- Best model: all-MiniLM-L6-v2 (mean=0.73)
- Largest gap: 0.15 between top 2 models (p=0.032)
- Dataset variation: education (0.80) > finance (0.65)

### NDCG@10
[Similar structure for each enabled metric]
```

Repeat for all common metrics across datasets.

##### **5. Dataset-Specific Insights**

```markdown
## Dataset-Specific Analysis

### Education Dataset
- **Difficulty**: Easy (mean MAP=0.74 across models)
- **Best Model**: all-MiniLM-L6-v2 (MAP=0.80, +8% over mean)
- **Model Agreement**: High (rank correlation=0.92 with finance)

[Per-dataset performance table]

### Finance Dataset
- **Difficulty**: Hard (mean MAP=0.62 across models)
- **Best Model**: all-MiniLM-L6-v2 (MAP=0.65, +5% over mean)
- **Model Agreement**: High (rank correlation=0.92 with education)

### Dataset Difficulty Ranking
[Bar chart showing mean performance per dataset]
```

##### **6. Performance Consistency Analysis**

```markdown
## Model Consistency Across Datasets

### Consistency Metrics
[Table with CV, rank stability, worst-case drop for each model]

[Visualization: Grouped bar chart comparing consistency metrics]

**Interpretation**:
- **Most Consistent**: all-MiniLM-L6-v2 (CV=0.12, maintains top-2 rank in all datasets)
- **Most Variable**: all-mpnet-base-v2 (CV=0.21, rank varies from 1 to 4)
```

##### **7. Timing and Efficiency Analysis**

```markdown
## Embedding Performance Comparison

### Speed vs Accuracy Trade-off
[Scatter plot: x=docs/second, y=mean MAP, bubble size=model size]

### Efficiency Ranking
[Table sorted by efficiency score = MAP / avg_time_per_doc]

| Model                                  | Mean MAP | Docs/Sec | Efficiency Score |
|----------------------------------------|----------|----------|------------------|
| sentence-transformers/all-MiniLM-L6-v2 | 0.7271   | 43.3     | 31.48            |
| sentence-transformers/all-mpnet-base-v2| 0.6192   | 3.8      | 2.35             |
```

##### **8. Recommendations and Discussion**

```markdown
## Recommendations

### For Production Deployment
1. **General Purpose**: Use all-MiniLM-L6-v2
   - Best overall performance (avg rank 1.5)
   - Excellent consistency across domains
   - Fast inference (43 docs/sec)

2. **High-Recall Scenarios**: Consider all-mpnet-base-v2
   - Best recall on finance dataset (0.95)
   - Trade-off: 10x slower embedding

### Domain-Specific Guidance
- **Education Domain**: All models perform well (easy dataset)
- **Finance Domain**: Requires stronger models (harder dataset)

### Limitations
- Limited to 2 datasets (minimum for statistical tests)
- All datasets are document retrieval tasks (generalization unclear)
- Single k value (10) - performance may vary at different k

## Future Work
- Evaluate on additional domain-specific datasets
- Test various k values (5, 20, 50, 100)
- Incorporate query difficulty analysis
- Explore ensemble methods
```

##### **9. Appendix**

```markdown
## Appendix

### A. Raw Data References
- Education: `datasets/education/reports/raw_results_2026-01-25_14-30-00.json`
- Finance: `datasets/finance/reports/raw_results_2026-01-25_14-25-00.json`

### B. Statistical Test Details
[Full tables with test statistics, degrees of freedom, confidence intervals]

### C. Visualization Gallery
- Figure 1: Cross-dataset radar chart
- Figure 2: Model ranking heatmap
- Figure 3: Performance distribution plots
- Figure 4: Dataset difficulty comparison
- Figure 5: Pairwise significance heatmap
- Figure 6: Consistency comparison chart
- Figure 7: Speed vs accuracy scatter plot
```

#### 3.2 CLI Integration in `rag_benchmark.py`

**Objective**: Seamlessly integrate aggregate reporting into existing CLI.

**New CLI Arguments**:

```python
# Add to argument parser in main()
parser.add_argument(
    '--generate-aggregate-report',
    action='store_true',
    help='Generate cross-dataset aggregate performance report'
)
parser.add_argument(
    '--aggregate-datasets',
    type=str,
    default=None,
    help='Comma-separated list of datasets to include (e.g., education,finance). Default: all available'
)
parser.add_argument(
    '--aggregate-output-dir',
    type=str,
    default=None,
    help='Custom output directory for aggregate report. Default: reports/aggregate'
)
parser.add_argument(
    '--aggregate-metrics',
    type=str,
    default=None,
    help='Comma-separated metrics to analyze (e.g., map,ndcg). Default: common metrics across datasets'
)
parser.add_argument(
    '--aggregate-pdf',
    action='store_true',
    help='Convert aggregate report to PDF using pandoc'
)
```

**Execution Logic** (add to `main()` in `rag_benchmark.py`):

```python
if args.generate_aggregate_report:
    print("=" * 80)
    print("GENERATING AGGREGATE CROSS-DATASET REPORT")
    print("=" * 80)
  
    # Parse dataset list
    dataset_names = None
    if args.aggregate_datasets:
        dataset_names = [d.strip() for d in args.aggregate_datasets.split(',')]
        print(f"\nDatasets to include: {', '.join(dataset_names)}")
    else:
        dataset_names = cfg.discover_available_datasets()
        print(f"\nAuto-discovered datasets: {', '.join(dataset_names)}")
  
    # Validate minimum datasets
    if len(dataset_names) < cfg.aggregate_min_datasets:
        print(f"\nERROR: Need at least {cfg.aggregate_min_datasets} datasets for aggregation.")
        print(f"Found: {len(dataset_names)} datasets")
        return
  
    # Parse metrics
    metrics = None
    if args.aggregate_metrics:
        metrics = [m.strip() for m in args.aggregate_metrics.split(',')]
  
    # Generate report
    from utils.aggregate_report_utils import generate_aggregate_report
  
    report_path = generate_aggregate_report(
        dataset_names=dataset_names,
        output_dir=args.aggregate_output_dir,
        metrics=metrics,
        generate_pdf=args.aggregate_pdf
    )
  
    print(f"\n{'='*80}")
    print(f"Aggregate report generated: {report_path}")
    if args.aggregate_pdf:
        pdf_path = report_path.replace('.md', '.pdf')
        print(f"PDF report: {pdf_path}")
    print(f"{'='*80}\n")
  
    return  # Exit after generation
```

**Example Usage**:

```bash
# Generate aggregate report for all available datasets
python rag_benchmark.py --generate-aggregate-report

# Specific datasets only
python rag_benchmark.py --generate-aggregate-report --aggregate-datasets education,finance

# Custom output directory with PDF generation
python rag_benchmark.py --generate-aggregate-report --aggregate-output-dir reports/paper --aggregate-pdf

# Focus on specific metrics
python rag_benchmark.py --generate-aggregate-report --aggregate-metrics map,ndcg

# Combined with dataset evaluation (run evaluation first, then aggregate)
python rag_benchmark.py --dataset education --evaluate
python rag_benchmark.py --dataset finance --evaluate
python rag_benchmark.py --generate-aggregate-report
```

**Backward Compatibility**:

- Existing `--evaluate` workflow unchanged
- Individual dataset reports still generated
- Aggregate report reads from saved raw_results JSON (no re-evaluation)
- Can run aggregate report independently anytime after individual evaluations

### Phase 4: Testing and Validation

#### 4.1 Unit Tests: `tests/test_aggregate_report_utils.py`

**Objective**: Comprehensive testing of aggregate functionality with edge case coverage.

**Test Structure**:

```python
import pytest
import json
import os
from utils.aggregate_report_utils import *
import config as cfg

class TestDataLoading:
    """Test raw results loading and validation."""
  
    def test_load_dataset_results_valid(self, tmp_path):
        """Test loading valid raw_results JSON."""
      
    def test_load_dataset_results_missing_file(self):
        """Test graceful handling of missing dataset."""
      
    def test_load_multiple_datasets_auto_discovery(self, tmp_path):
        """Test auto-discovery of available datasets."""
      
    def test_validate_metric_compatibility_identical(self):
        """Test validation when all metrics match."""
      
    def test_validate_metric_compatibility_partial_overlap(self):
        """Test with partial metric overlap (should use intersection)."""
      
    def test_validate_metric_compatibility_no_overlap(self):
        """Test error when no common metrics."""


class TestMetricNormalization:
    """Test metric and model name normalization."""
  
    def test_get_common_metrics_full_overlap(self):
        """Test when all datasets have same metrics."""
      
    def test_get_common_metrics_partial_overlap(self):
        """Test intersection of different metric sets."""
      
    def test_normalize_model_names_variations(self):
        """Test handling of model name variations."""
      
    def test_extract_model_scores_across_datasets(self):
        """Test score extraction for aggregation."""


class TestAggregationFunctions:
    """Test cross-dataset aggregation logic."""
  
    def test_aggregate_model_performance_basic(self):
        """Test basic aggregation (mean, std, min, max)."""
      
    def test_aggregate_model_performance_missing_model(self):
        """Test when model exists in some but not all datasets."""
      
    def test_calculate_model_rankings_single_metric(self):
        """Test ranking computation per dataset."""
      
    def test_calculate_average_ranks(self):
        """Test average rank calculation across datasets."""
      
    def test_calculate_consistency_scores(self):
        """Test CV, rank stability, worst-case drop calculations."""


class TestStatisticalAnalysis:
    """Test statistical significance testing."""
  
    def test_pairwise_significance_tests_basic(self):
        """Test paired t-test matrix generation."""
      
    def test_pairwise_significance_tests_insufficient_data(self):
        """Test error when < 2 datasets (can't pair)."""
      
    def test_calculate_effect_sizes(self):
        """Test Cohen's d calculation and interpretation."""
      
    def test_generate_win_tie_loss_matrix(self):
        """Test win-tie-loss counting with tie threshold."""
      
    def test_perform_friedman_test(self):
        """Test Friedman test for overall differences."""
      
    def test_bonferroni_correction(self):
        """Test multiple testing correction."""


class TestVisualizationGeneration:
    """Test visualization creation (with mocked matplotlib)."""
  
    @pytest.fixture
    def mock_matplotlib(self, monkeypatch):
        """Mock matplotlib to avoid actual file creation."""
      
    def test_generate_cross_dataset_radar_chart(self, mock_matplotlib, tmp_path):
        """Test radar chart generation."""
      
    def test_generate_model_ranking_heatmap(self, mock_matplotlib, tmp_path):
        """Test heatmap generation."""
      
    def test_generate_performance_distribution_plots(self, mock_matplotlib, tmp_path):
        """Test box/violin plots."""
      
    def test_generate_dataset_difficulty_chart(self, mock_matplotlib, tmp_path):
        """Test difficulty comparison chart."""
      
    def test_generate_pairwise_significance_heatmap(self, mock_matplotlib, tmp_path):
        """Test significance matrix heatmap."""
      
    def test_generate_consistency_comparison_chart(self, mock_matplotlib, tmp_path):
        """Test consistency metrics chart."""


class TestReportGeneration:
    """Test end-to-end aggregate report generation."""
  
    def test_generate_aggregate_report_basic(self, tmp_path):
        """Test full report generation with 2 datasets."""
      
    def test_generate_aggregate_report_custom_metrics(self, tmp_path):
        """Test report with subset of metrics."""
      
    def test_generate_aggregate_report_insufficient_datasets(self):
        """Test error when < minimum datasets."""
      
    def test_generate_aggregate_report_pdf_conversion(self, tmp_path):
        """Test PDF generation (if pandoc available)."""


class TestErrorHandling:
    """Test edge cases and error scenarios."""
  
    def test_corrupted_json_handling(self, tmp_path):
        """Test graceful handling of malformed JSON."""
      
    def test_missing_required_fields(self, tmp_path):
        """Test validation of JSON structure."""
      
    def test_inconsistent_model_sets(self):
        """Test when datasets have different models evaluated."""
      
    def test_zero_variance_scores(self):
        """Test statistical functions with no variation (avoid divide by zero)."""
      
    def test_single_model_evaluation(self):
        """Test when only one model evaluated (no pairwise comparisons)."""
```

**Test Data Fixtures** (in `conftest.py`):

```python
@pytest.fixture
def sample_raw_results_education():
    """Sample raw results for education dataset."""
    return {
        "dataset": "education",
        "timestamp": "2026-01-25_14-30-00",
        "config": {...},
        "models": {...},
        "corpus_stats": {...}
    }

@pytest.fixture
def sample_raw_results_finance():
    """Sample raw results for finance dataset."""
  
@pytest.fixture
def create_temp_datasets(tmp_path):
    """Create temporary dataset structure with raw_results JSON files."""
```

**Coverage Goals**:

- **Line Coverage**: >90%
- **Branch Coverage**: >85%
- **Edge Cases**: All error paths tested
- **Integration**: End-to-end report generation

#### 4.2 Integration Tests: `tests/test_aggregate_integration.py`

**Objective**: Test full workflow with real (but minimal) data.

**Test Scenarios**:

```python
class TestAggregateIntegration:
    """Integration tests with realistic data."""
  
    def test_full_workflow_two_datasets(self, tmp_path):
        """
        End-to-end test:
        1. Create 2 minimal datasets (10 docs each)
        2. Run evaluations
        3. Generate individual reports with raw_results
        4. Generate aggregate report
        5. Validate all outputs exist
        """
      
    def test_incremental_aggregation(self, tmp_path):
        """
        Test adding new dataset:
        1. Generate aggregate for datasets A, B
        2. Evaluate dataset C
        3. Re-generate aggregate for A, B, C
        4. Validate C included in new report
        """
      
    def test_mixed_metric_configurations(self, tmp_path):
        """
        Test with datasets having different enabled metrics:
        - Dataset A: MAP, Recall, NDCG
        - Dataset B: MAP, NDCG, MRR
        - Expected: Aggregate only on common (MAP, NDCG)
        """
      
    def test_cli_integration(self):
        """
        Test CLI flags:
        1. Run with --generate-aggregate-report
        2. Validate output paths
        3. Check PDF generation (if available)
        """
```

#### 4.3 Validation Tests: `tests/test_statistical_validity.py`

**Objective**: Validate statistical test correctness against known results.

```python
class TestStatisticalValidity:
    """Validate statistical calculations against known answers."""
  
    def test_paired_ttest_known_result(self):
        """Test against scipy.stats.ttest_rel reference implementation."""
      
    def test_cohens_d_known_result(self):
        """Test Cohen's d against published examples."""
      
    def test_friedman_test_known_result(self):
        """Test against scipy.stats.friedmanchisquare."""
      
    def test_cv_calculation(self):
        """Validate coefficient of variation formula."""
```

### Phase 5: Documentation and Examples

#### 5.1 Update README.md

**Objective**: Document aggregate reporting workflow.

**Sections to add**:

- Aggregate report generation guide
- Example commands and outputs
- Interpretation of statistical results
- Publication-ready formatting tips

#### 5.2 Example Aggregate Report

**Objective**: Create sample output for reference.

**Deliverables**:

- Sample aggregate report Markdown fileExample visualizations
- Statistical analysis examples

## Implementation Timeline (Revised)

### Week 1: Foundation & Data Persistence

**Goals**: Establish raw results storage and configuration infrastructure

**Tasks**:

- [ ] **Day 1-2**: Implement `save_raw_results_json()` in `utils/report_utils.py`

  - Modify `generate_benchmark_report()` to call save function
  - Add timing data merging logic
  - Compute and include corpus statistics
  - Test with existing education/finance datasets
- [ ] **Day 3**: Update `config.py` with aggregate settings

  - Add aggregate-specific configuration variables
  - Implement `discover_available_datasets()`
  - Implement `get_latest_raw_results()`
  - Write unit tests for config functions
- [ ] **Day 4-5**: Create initial `utils/aggregate_report_utils.py`

  - Implement data loading functions (load_dataset_results, load_multiple_datasets)
  - Implement validation functions (validate_metric_compatibility)
  - Write comprehensive tests for Phase 1
  - Generate raw_results for existing datasets by re-running evaluations

**Deliverables**: Raw JSON results storage working, config infrastructure complete, basic data loading tested

### Week 2: Core Aggregation & Statistical Analysis

**Goals**: Implement aggregation logic and statistical testing

**Tasks**:

- [ ] **Day 1-2**: Metric normalization and extraction

  - Implement `get_common_metrics()`
  - Implement `normalize_model_names()`
  - Implement `extract_model_scores_across_datasets()`
  - Test with datasets having different metric configurations
- [ ] **Day 3-4**: Aggregation functions

  - Implement `aggregate_model_performance()`
  - Implement `calculate_model_rankings()`
  - Implement `calculate_average_ranks()`
  - Implement `calculate_consistency_scores()`
  - Write unit tests for all aggregation functions
- [ ] **Day 5**: Statistical analysis functions

  - Implement `perform_pairwise_significance_tests()` using scipy.stats
  - Implement `calculate_effect_sizes()` with Cohen's d
  - Implement `generate_win_tie_loss_matrix()`
  - Implement `perform_friedman_test()`
  - Validate against known statistical results

**Deliverables**: Complete aggregation engine, validated statistical tests, >85% test coverage

### Week 3: Visualization & Report Generation

**Goals**: Create visualizations and full report generator

**Tasks**:

- [ ] **Day 1-2**: Visualization functions (following matplotlib patterns from `report_utils.py`)

  - Implement `generate_cross_dataset_radar_chart()`
  - Implement `generate_model_ranking_heatmap()`
  - Implement `generate_performance_distribution_plots()`
  - Test visualization output quality
- [ ] **Day 3**: Additional visualizations

  - Implement `generate_dataset_difficulty_chart()`
  - Implement `generate_pairwise_significance_heatmap()`
  - Implement `generate_consistency_comparison_chart()`
  - Test with real education/finance data
- [ ] **Day 4-5**: Report generator

  - Implement `generate_aggregate_report()` with all sections
  - Create Markdown formatting functions for tables/sections
  - Add PDF conversion support (pandoc)
  - Test full report generation with 2 datasets

**Deliverables**: Complete visualization suite, working aggregate report generator, sample report

### Week 4: CLI Integration, Testing & Documentation

**Goals**: Integration, comprehensive testing, documentation

**Tasks**:

- [ ] **Day 1**: CLI integration in `rag_benchmark.py`

  - Add argument parser flags (--generate-aggregate-report, --aggregate-datasets, etc.)
  - Implement execution logic in main()
  - Test CLI with various flag combinations
  - Validate backward compatibility with existing workflows
- [ ] **Day 2**: Integration tests

  - Write `tests/test_aggregate_integration.py`
  - Test full workflow: evaluate → save raw results → aggregate
  - Test mixed metric configurations
  - Test incremental aggregation (adding new datasets)
- [ ] **Day 3**: Statistical validation tests

  - Write `tests/test_statistical_validity.py`
  - Validate against scipy reference implementations
  - Test edge cases (zero variance, single model, etc.)
  - Achieve >90% overall test coverage
- [ ] **Day 4**: Documentation

  - Update README.md with aggregate reporting section
  - Create usage examples and best practices guide
  - Document interpretation of statistical results
  - Add troubleshooting section
- [ ] **Day 5**: Polish and example generation

  - Generate example aggregate report with real data
  - Create gallery of visualizations for documentation
  - Performance optimization (if needed)
  - Code review and cleanup

**Deliverables**: Fully integrated system, >90% test coverage, complete documentation, example reports

## Risk Mitigation (Updated)

### Technical Risks

1. **Metric Configuration Inconsistencies**

   - **Risk**: Datasets evaluated with different enabled metrics (e.g., education has MAP+NDCG, finance has MAP+Recall)
   - **Mitigation**:
     - Implement `get_common_metrics()` to identify intersection
     - Support two modes via `config.aggregate_require_identical_metrics`:
       - `False` (default): Use metric intersection, warn about excluded metrics
       - `True`: Error if any metric mismatch detected
     - Store original metric flags in raw_results JSON for validation
   - **Status**: Addressed in Phase 2.1
2. **Model Name Variations**

   - **Risk**: Same model referenced differently (e.g., "all-MiniLM-L6-v2" vs "sentence-transformers/all-MiniLM-L6-v2")
   - **Mitigation**: Implement `normalize_model_names()` with fuzzy matching and user-configurable aliases
   - **Fallback**: Require exact name matches, document naming conventions
   - **Status**: Addressed in Phase 2.1
3. **Statistical Test Validity**

   - **Risk**: Insufficient datasets for meaningful statistical tests (n<3 for paired t-test)
   - **Mitigation**:
     - Enforce `config.aggregate_min_datasets = 2` (minimum for paired test)
     - For n<5, add warning about low statistical power
     - Provide effect sizes (Cohen's d) alongside p-values for practical significance
   - **Status**: Addressed in config + Phase 2.1
4. **Memory Usage with Large Datasets**

   - **Risk**: Loading many large raw_results JSON files simultaneously
   - **Mitigation**:
     - Process datasets sequentially for aggregation (generator pattern if needed)
     - Raw results JSON is compact (only metrics, not full corpus)
     - Monitor and optimize if >10 datasets
   - **Status**: Low priority (current scale: 2-5 datasets)
5. **Visualization Rendering Failures**

   - **Risk**: matplotlib errors with edge cases (e.g., single model, zero variance)
   - **Mitigation**:
     - Wrap all plotting functions in try-except with graceful fallback
     - Skip visualizations on error, continue report generation
     - Log errors for debugging
   - **Status**: Addressed in Phase 3 design

### Operational Risks

1. **Missing Raw Results Files**

   - **Risk**: User runs `--generate-aggregate-report` before evaluations complete
   - **Mitigation**:
     - Implement `get_latest_raw_results()` to check file existence
     - Provide clear error messages listing missing datasets
     - Suggest running `--evaluate` for missing datasets
   - **Status**: Addressed in Phase 1.2
2. **Dataset Discovery Ambiguity**

   - **Risk**: `discover_available_datasets()` includes incomplete/test datasets
   - **Mitigation**:
     - Require valid corpus.jsonl as minimum criterion
     - Validate presence of queries.jsonl and qrels.tsv (warn if missing)
     - Support explicit `--aggregate-datasets` flag to override auto-discovery
   - **Status**: Addressed in Phase 1.2 + Phase 3.2
3. **Backward Compatibility**

   - **Risk**: Changes break existing single-dataset evaluation workflow
   - **Mitigation**:
     - Make raw results saving opt-in initially (`save_raw_results=False` in `generate_benchmark_report()`)
     - Enable by default after testing (opt-out via config flag)
     - Aggregate reporting is entirely separate CLI path (no impact on `--evaluate`)
   - **Status**: Design principle established
4. **PDF Generation Dependency**

   - **Risk**: pandoc not installed, PDF generation fails
   - **Mitigation**:
     - Make PDF optional (--aggregate-pdf flag)
     - Check pandoc availability before attempting conversion
     - Provide clear installation instructions in error message
     - Markdown report always generated (primary output)
   - **Status**: Addressed in Phase 3.1
5. **Performance Degradation**

   - **Risk**: Aggregate report generation takes too long (>60 seconds for 5 datasets)
   - **Mitigation**:
     - Profile critical paths (statistical tests, visualizations)
     - Cache intermediate results if possible
     - Parallel visualization generation (matplotlib backend issues permitting)
     - Optimize only if actually needed (premature optimization)
   - **Status**: Monitor in testing phase

### Data Quality Risks

1. **Inconsistent k Values Across Datasets**

   - **Risk**: Education evaluated at k=10, finance at k=20
   - **Mitigation**:
     - Store k value in raw_results config
     - Validate k consistency in `validate_metric_compatibility()`
     - If different: warn user, proceed with comparison (note limitation in report)
   - **Status**: Addressed in Phase 2.1
2. **Different Embedding Models Per Dataset**

   - **Risk**: Education has 5 models, finance has 3 (only 2 overlap)
   - **Mitigation**:
     - Aggregate only common models across all datasets
     - Report which models excluded and why
     - Require minimum 2 common models for meaningful comparison
   - **Status**: Addressed in Phase 2.1
3. **Corrupted or Malformed JSON**

   - **Risk**: Raw results JSON file damaged or incomplete
   - **Mitigation**:
     - JSON schema validation on load
     - Skip corrupted datasets with warning (don't fail entire aggregation)
     - Log detailed error for user debugging
   - **Status**: Addressed in Phase 4.1 (error handling tests)

## Success Criteria (Detailed)

### 1. Functionality Requirements

- ✅ Generate aggregate reports comparing **≥2 datasets** with statistical analysis
- ✅ Support datasets with **different metric configurations** (use intersection)
- ✅ Handle **partial model overlap** across datasets (aggregate common models only)
- ✅ Produce **7 distinct visualization types** (radar, heatmap, distribution, difficulty, significance, consistency, efficiency)
- ✅ Calculate **5+ statistical measures** (p-values, effect sizes, win-tie-loss, rankings, consistency scores)
- ✅ Auto-discover available datasets or accept explicit list
- ✅ Generate both Markdown and optional PDF output

### 2. Quality Requirements

- ✅ **Publication-ready visualizations**: 300 DPI, clear labels, colorblind-safe palettes
- ✅ **Statistically sound comparisons**:
  - Paired t-tests with proper assumptions checked
  - Bonferroni correction for multiple comparisons
  - Effect sizes reported alongside p-values
  - Warnings for low statistical power (n<5 datasets)
- ✅ **Professional report formatting**:
  - Executive summary with key findings
  - Proper citations of statistical methods
  - Clear interpretation guidance
  - Limitations section
- ✅ **Reproducibility**: All raw data paths referenced in appendix

### 3. Integration Requirements

- ✅ **Seamless CLI integration**: New flags follow existing argument patterns
- ✅ **No workflow disruption**: Existing `--evaluate` unchanged, aggregate is separate path
- ✅ **Config-driven behavior**: Respects all config.py settings (significance level, min datasets, etc.)
- ✅ **Backward compatible**: Old reports continue to work, raw results saving is opt-in initially

### 4. Testing Requirements

- ✅ **Test coverage**:
  - Unit tests: >90% line coverage, >85% branch coverage
  - Integration tests: Full workflow tested end-to-end
  - Statistical validation: All formulas verified against scipy
- ✅ **Edge case handling**:
  - Single model, zero variance, missing data, corrupted JSON all tested
  - Graceful degradation (skip visualizations on error, continue report)
- ✅ **Performance tests**: Aggregate generation completes in <60s for 5 datasets

### 5. Documentation Requirements

- ✅ **User guide**:
  - Complete workflow examples (evaluate → aggregate)
  - CLI flag reference
  - Interpretation guide for statistical results
- ✅ **Developer documentation**:
  - Function docstrings for all public APIs
  - Architecture diagram showing data flow
  - Contributing guidelines for adding new metrics/visualizations
- ✅ **Example outputs**:
  - Sample aggregate report (Markdown + PDF)
  - Gallery of all 7 visualization types
  - Interpretation walkthrough

### 6. Performance Requirements

- ✅ **Speed**:
  - Load 5 datasets with 10 models each: <5s
  - Statistical analysis: <10s
  - Visualization generation: <20s
  - Total report generation: <60s
- ✅ **Memory**: Peak memory <2GB for 10 datasets (scalability validated)
- ✅ **File size**: Aggregate report <5MB (including embedded images if HTML)

### Acceptance Criteria Checklist

**Phase 1 Complete When**:

- [ ] Raw results JSON saved automatically during evaluation
- [ ] JSON structure validated with schema
- [ ] Config functions (discover_datasets, get_latest_raw_results) working
- [ ] At least 2 real datasets have raw_results files

**Phase 2 Complete When**:

- [ ] Load and aggregate metrics for education + finance datasets
- [ ] Statistical tests return valid p-values and effect sizes
- [ ] Consistency scores calculated correctly
- [ ] Unit tests pass with >85% coverage

**Phase 3 Complete When**:

- [ ] All 7 visualization types generate valid PNG files
- [ ] Full aggregate report generated with all sections
- [ ] Report renders correctly to PDF via pandoc
- [ ] Sample report reviewed and approved

**Phase 4 Complete When**:

- [ ] All CLI flags work as documented
- [ ] Integration tests pass (full workflow)
- [ ] README updated with examples
- [ ] Code review completed
- [ ] User can successfully generate aggregate report following docs

## Dependencies (Verified)

### Current Dependencies (Already Installed in `ragbenchmark` Conda Environment)

- ✅ **numpy**: Numerical operations, array handling
- ✅ **matplotlib**: Visualization generation (radar charts, heatmaps, plots)
- ✅ **tabulate**: Markdown table formatting (already used in report_utils.py)

### New Dependencies Required

- ⚠️ **scipy** (`scipy.stats`): Statistical testing (t-tests, Friedman test, effect sizes)

  - Installation: `conda install scipy` or `pip install scipy`
  - Version: ≥1.7.0 recommended
- ⚠️ **pandas** (optional but recommended):

  - DataFrame manipulation for significance matrices, win-tie-loss tables
  - Makes code cleaner for tabular operations
  - Installation: `conda install pandas` or `pip install pandas`
  - Version: ≥1.3.0 recommended
  - **Note**: Can implement without pandas using nested dicts/lists, but less readable

### Optional Dependencies

- 📄 **pandoc** (system dependency, not Python package):

  - PDF generation from Markdown
  - Installation: Download from https://pandoc.org/installing.html
  - Windows: `choco install pandoc` or `scoop install pandoc`
  - Check: `pandoc --version`
  - **Graceful degradation**: If not installed, skip PDF generation, only create Markdown
- 📊 **seaborn** (optional enhancement):

  - Better default matplotlib styles
  - Enhanced heatmap aesthetics
  - Installation: `conda install seaborn`
  - **Not required**: Can achieve same results with pure matplotlib

### Installation Instructions

**For developers** (add to `requirements.txt`):

```txt
scipy>=1.7.0
pandas>=1.3.0
```

**For users** (update README):

```bash
# Activate environment
conda activate ragbenchmark

# Install new dependencies
conda install scipy pandas

# Optional: Install pandoc for PDF generation (system-level)
# Windows: choco install pandoc
# macOS: brew install pandoc
# Linux: sudo apt-get install pandoc
```

### Dependency Validation

**Add to `config.py` or `aggregate_report_utils.py`**:

```python
def check_aggregate_dependencies():
    """
    Check if required dependencies for aggregate reporting are installed.
    Raises ImportError with installation instructions if missing.
    """
    missing = []
  
    try:
        import scipy
    except ImportError:
        missing.append("scipy (install: conda install scipy)")
  
    try:
        import pandas
    except ImportError:
        missing.append("pandas (install: conda install pandas)")
  
    if missing:
        raise ImportError(
            f"Aggregate reporting requires additional packages:\n" +
            "\n".join(f"  - {pkg}" for pkg in missing) +
            "\n\nInstall all: conda install scipy pandas"
        )
  
    # Check optional dependencies
    try:
        import subprocess
        subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Warning: pandoc not found. PDF generation will be disabled.")
        print("Install: https://pandoc.org/installing.html")
```

Call `check_aggregate_dependencies()` at start of `generate_aggregate_report()`.

## Appendix

### A. Design Decisions and Rationale

#### Why Store Raw Results in `report_utils.py` Instead of `chromadb_utils.py`?

**Decision**: Implement `save_raw_results_json()` in `report_utils.py`, not `chromadb_utils.py`.

**Rationale**:

- **Separation of concerns**: `chromadb_utils.py` handles evaluation logic only
- **Data aggregation point**: `report_utils.py` already combines metrics + timing data
- **Timing data availability**: Timing data loaded in report generation, not evaluation
- **Minimal changes**: Leverage existing `generate_benchmark_report()` flow
- **Testing simplicity**: Mock fewer dependencies when testing report generation

#### Why Dict Structure for Models Instead of List?

**Decision**: Store models as `{"model_name": {...}}` dict, not `[{"name": "...", ...}]` list.

**Rationale**:

- **Faster lookups**: O(1) access by model name during aggregation
- **Easier merging**: Combine datasets without nested loops
- **Cleaner code**: `results["education"]["models"]["all-MiniLM-L6-v2"]["metrics"]["map"]`
- **Natural JSON structure**: Matches common API response patterns

#### Why Paired T-Tests for 2+ Datasets?

**Decision**: Use paired t-test treating each dataset as one paired observation.

**Rationale**:

- **Paired design**: Same models evaluated on different datasets (natural pairing)
- **Controls for model differences**: Each model is its own control
- **Statistical validity**: Appropriate for repeated measures (≥2 datasets)
- **Standard practice**: Common in ML benchmarking literature
- **Alternative**: Friedman test for non-parametric option (also implemented)

#### Why Equal Weighting Across Datasets?

**Decision**: Treat each dataset equally in aggregation (unweighted mean), regardless of size.

**Rationale**:

- **Domain importance**: Small specialized dataset can be as important as large general one
- **Simplicity**: Easier interpretation (mean across datasets)
- **Avoids bias**: Prevents domination by single large dataset
- **Future flexibility**: Can add weighted mode later if needed via config flag
- **Statistical validity**: Equal weighting maintains independence assumption

#### Why Intersection of Metrics Instead of Union?

**Decision**: Aggregate only metrics enabled in ALL datasets (intersection).

**Rationale**:

- **Fair comparison**: Can't rank models on metrics not computed everywhere
- **Statistical validity**: Paired tests require complete data
- **User clarity**: Clear error messages about missing metrics
- **Flexibility**: User can re-evaluate datasets with consistent metrics if needed
- **Alternative**: Support `--aggregate-require-identical-metrics=True` for strict validation

### B. Glossary of Statistical Terms

- **MAP (Mean Average Precision)**: Average of precision scores at each relevant document position
- **NDCG (Normalized Discounted Cumulative Gain)**: Measures ranking quality with position discounting
- **MRR (Mean Reciprocal Rank)**: Average of 1/rank for first relevant document
- **Paired t-test**: Statistical test for differences between paired observations (same models, different datasets)
- **Cohen's d**: Effect size measure (standardized mean difference); small (<0.5), medium (0.5-0.8), large (>0.8)
- **Friedman test**: Non-parametric alternative to repeated measures ANOVA for ranked data
- **Bonferroni correction**: Adjusts p-value threshold to control family-wise error rate in multiple comparisons
- **Coefficient of Variation (CV)**: Ratio of standard deviation to mean (normalized variability measure)
- **Rank stability**: Consistency of model rankings across datasets (1 = perfect consistency, 0 = random)
- **Win-Tie-Loss**: Count of datasets where model A beats/ties/loses to model B

### C. Reference Implementations

#### Cohen's d Formula

```python
def cohen_d(scores_a: List[float], scores_b: List[float]) -> float:
    """
    Cohen's d effect size for two groups.
    d = (mean_a - mean_b) / pooled_std
    """
    mean_a, mean_b = np.mean(scores_a), np.mean(scores_b)
    n_a, n_b = len(scores_a), len(scores_b)
    var_a, var_b = np.var(scores_a, ddof=1), np.var(scores_b, ddof=1)
  
    # Pooled standard deviation
    pooled_std = np.sqrt(((n_a - 1) * var_a + (n_b - 1) * var_b) / (n_a + n_b - 2))
  
    return (mean_a - mean_b) / pooled_std if pooled_std > 0 else 0.0
```

#### Paired T-Test Usage

```python
from scipy.stats import ttest_rel

# Example: Compare two models across 3 datasets
model_a_scores = [0.75, 0.68, 0.82]  # MAP on education, finance, medical
model_b_scores = [0.70, 0.65, 0.78]

t_statistic, p_value = ttest_rel(model_a_scores, model_b_scores)

if p_value < 0.05:
    print(f"Significant difference (p={p_value:.3f})")
else:
    print(f"No significant difference (p={p_value:.3f})")
```

#### Bonferroni Correction

```python
def bonferroni_alpha(alpha: float, num_comparisons: int) -> float:
    """Adjusted alpha for multiple comparisons."""
    return alpha / num_comparisons

# Example: 5 models = 10 pairwise comparisons
adjusted_alpha = bonferroni_alpha(0.05, 10)  # 0.005
```

### D. Example Report Excerpt

**Sample Cross-Dataset Comparison Table**:

```markdown
| Model                                  | Education (MAP) | Finance (MAP) | Mean  | Std   | Rank |
|----------------------------------------|-----------------|---------------|-------|-------|------|
| sentence-transformers/all-MiniLM-L6-v2 | 0.7999          | 0.6543        | 0.7271| 0.103 | 1    |
| sentence-transformers/all-mpnet-base-v2| 0.4328          | 0.8056        | 0.6192| 0.264 | 2    |

**Interpretation**: all-MiniLM-L6-v2 achieves higher mean MAP (0.73 vs 0.62) with better consistency (std=0.10 vs 0.26).
```

**Sample Statistical Significance Matrix**:

```markdown
|                  | all-MiniLM-L6-v2 | all-mpnet-base-v2 | all-distilroberta-v1 |
|------------------|------------------|-------------------|----------------------|
| all-MiniLM-L6-v2 | -                | 0.032*            | 0.001**              |
| all-mpnet-base-v2| 0.032*           | -                 | 0.156                |
| all-distilroberta| 0.001**          | 0.156             | -                    |

*p < 0.05, **p < 0.01, ***p < 0.001
```

### E. FAQ

**Q: Can I aggregate datasets with different k values?**
A: Yes, but with a warning. The system will note the k mismatch in the report's limitations section. For rigorous comparison, re-evaluate datasets with consistent k.

**Q: What if two datasets have no models in common?**
A: Error: "No common models found across datasets. Cannot generate aggregate report." Solution: Evaluate overlapping models or use separate reports.

**Q: How do I add a new statistical test?**
A: 1) Implement function in `aggregate_report_utils.py`, 2) Add test in `tests/test_aggregate_report_utils.py`, 3) Call from `generate_aggregate_report()`, 4) Document in report methodology section.

**Q: Can I exclude specific datasets from aggregation?**
A: Yes: `--aggregate-datasets education,finance` (include only these) or set `config.aggregate_exclude_datasets = ["test_dataset"]`.

**Q: Does aggregate reporting re-run evaluations?**
A: No. It reads from saved `raw_results_{timestamp}.json` files. Evaluations must be run first with `--evaluate`.

**Q: What if raw_results JSON is missing for a dataset?**
A: Error: "Missing raw results for dataset 'X'. Run evaluation first: python rag_benchmark.py --dataset X --evaluate"

**Q: Can I customize the report format?**
A: Yes. Edit `generate_aggregate_report()` in `aggregate_report_utils.py`. The Markdown structure is fully customizable. For major changes, consider creating a new report template function.

### F. Related Documentation

- **Multi-Dataset Implementation**: [multidatasetplan_v2.md](multidatasetplan_v2.md)
- **Benchmark Workflow**: [benchmark_workflow.md](benchmark_workflow.md)
- **MAP Calculation Details**: [MAP_CALCULATION_SUMMARY.md](MAP_CALCULATION_SUMMARY.md)
- **Testing Strategy**: [test_plan.md](test_plan.md)

---

**Document Version**: 2.0 (Revised January 25, 2026)
**Status**: Ready for Implementation
**Next Review**: After Phase 1 Completion

### Phase 5: Advanced Features (Post-Launch)

#### High Priority (Next 2-3 Months)

1. **Interactive HTML Reports**

   - **Motivation**: Enable exploration without re-running analysis
   - **Features**:
     - Plotly.js interactive charts (zoom, hover, filter)
     - Collapsible sections for dataset details
     - Model comparison selector (dynamic chart updates)
     - Export subsections as standalone images
   - **Dependencies**: `plotly`, `jinja2` for templating
   - **Estimated Effort**: 2 weeks
2. **Query Difficulty Analysis**

   - **Motivation**: Understand performance variation across query types
   - **Features**:
     - Categorize queries by difficulty (mean MAP across models)
     - Per-model performance on hard vs easy queries
     - Query length correlation analysis
     - Cross-dataset query difficulty comparison
   - **Implementation**: Extend raw_results JSON with per-query metrics
   - **Estimated Effort**: 1 week
3. **Confidence Intervals for Metrics**

   - **Motivation**: Better uncertainty quantification than std alone
   - **Features**:
     - Bootstrap confidence intervals (95% CI) for mean metrics
     - Visualize CI as error bands on charts
     - Report CI in aggregation tables
   - **Dependencies**: scipy.stats for bootstrap
   - **Estimated Effort**: 3 days
4. **Multi-k Analysis**

   - **Motivation**: Understand how k affects model rankings
   - **Features**:
     - Evaluate at k=[5, 10, 20, 50, 100] simultaneously
     - Generate k-specific aggregate reports
     - Rank stability across k values
     - Optimal k recommendation per dataset
   - **Implementation**: Modify raw_results to store multi-k metrics
   - **Estimated Effort**: 1 week

#### Medium Priority (3-6 Months)

5. **Automated Model Selection**

   - **Motivation**: Recommend best model for new dataset characteristics
   - **Features**:
     - Train meta-model: dataset features → expected model performance
     - Features: corpus size, avg doc length, domain (NLP classification)
     - Predict top-3 models for unseen dataset before evaluation
     - Validation: Leave-one-dataset-out cross-validation
   - **Dependencies**: scikit-learn for meta-model
   - **Estimated Effort**: 2 weeks
6. **Statistical Power Analysis**

   - **Motivation**: Determine required datasets for conclusive comparisons
   - **Features**:
     - Compute statistical power for each pairwise comparison
     - Recommend minimum datasets needed for target power (0.8)
     - Effect size detectability analysis
     - Sample size planning for new datasets
   - **Dependencies**: statsmodels for power analysis
   - **Estimated Effort**: 1 week
7. **Cost-Performance Trade-off Analysis**

   - **Motivation**: Include deployment costs in recommendations
   - **Features**:
     - Inference cost estimation (time × hardware cost)
     - Pareto frontier: accuracy vs cost
     - ROI calculation: accuracy gain vs cost increase
     - Budget-constrained recommendations
   - **Implementation**: Add cost model config per model
   - **Estimated Effort**: 4 days
8. **Temporal Analysis** (for evolving datasets)

   - **Motivation**: Track model performance over time as datasets grow
   - **Features**:
     - Time-series plots of metrics across evaluation dates
     - Detect performance degradation
     - Dataset drift analysis
     - Trend forecasting (ARIMA models)
   - **Implementation**: Store historical raw_results, track timestamps
   - **Estimated Effort**: 1 week

#### Low Priority / Research (6+ Months)

9. **Ensemble Method Recommendations**

   - **Motivation**: Combine models for better performance
   - **Features**:
     - Test simple ensembles (voting, averaging, stacking)
     - Optimal ensemble selection per dataset
     - Cross-dataset ensemble generalization
   - **Estimated Effort**: 2 weeks
10. **Domain Adaptation Analysis**

    - **Motivation**: Understand transfer learning potential
    - **Features**:
      - Similarity matrix between datasets (domain distance)
      - Predict model performance on target from source domain
      - Few-shot learning: fine-tune on small target samples
    - **Estimated Effort**: 3 weeks
11. **Real-time Aggregation Dashboard**

    - **Motivation**: Live updates as evaluations complete
    - **Features**:
      - Web dashboard (FastAPI + Vue.js)
      - Streaming evaluation results
      - Live aggregate statistics
      - Notification on significant changes
    - **Dependencies**: FastAPI, websockets, frontend framework
    - **Estimated Effort**: 4 weeks
12. **Cross-Lingual / Multi-Modal Extensions**

    - **Motivation**: Expand beyond English text retrieval
    - **Features**:
      - Multi-language dataset support
      - Image-text retrieval aggregation
      - Audio-text retrieval
      - Modality-specific metrics
    - **Estimated Effort**: Ongoing research
