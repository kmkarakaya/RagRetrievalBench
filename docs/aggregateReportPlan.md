# Aggregate Cross-Dataset Report Generation Plan

## Overview
This plan outlines the implementation of aggregate reporting functionality to compare embedding model performance across multiple datasets. The system will enable publication-ready analysis for conference papers by aggregating individual dataset results into comprehensive cross-dataset comparisons.

## Current Architecture Analysis

### Core Components
- **`rag_benchmark.py`**: Main CLI orchestrator with dataset selection and batch processing
- **`config.py`**: Central configuration with dataset-specific paths and metric flags
- **`utils/chromadb_utils.py`**: Evaluation logic returning metric tuples `(MAP, Recall, Precision, NDCG, MRR)`
- **`utils/report_utils.py`**: Individual dataset report generation with Markdown output and visualizations
- **`utils/document_loader.py`**: Data loading from JSONL/TSV files
- **Multi-dataset isolation**: Separate ChromaDB collections and report directories per dataset

### Key Characteristics
- **Dynamic metric indexing**: Metrics enabled via config flags (`compute_map`, `compute_recall`, etc.)
- **Fixed tuple ordering**: `evaluate_with_chromadb()` returns metrics in consistent order
- **Config-driven paths**: `configure_for_dataset(name)` sets dataset-specific file paths
- **Batch processing**: Cost-effective LLM operations via Google Gemini Batch API

## Implementation Plan

### Phase 1: Raw Data Storage Enhancement

#### 1.1 JSON Result Storage in `utils/chromadb_utils.py`
**Objective**: Store raw evaluation results per dataset for programmatic aggregation.

**Changes**:
- Modify `evaluate_with_chromadb()` to optionally save results to JSON
- Add parameter `save_raw_results: bool = False`
- Create JSON structure preserving metric metadata:

```json
{
  "dataset": "education",
  "timestamp": "2026-01-25_14-30-00",
  "config": {
    "k": 10,
    "compute_map": true,
    "compute_recall": true,
    "compute_precision": true,
    "compute_ndcg": true,
    "compute_mrr": true
  },
  "models": [
    {
      "name": "sentence-transformers/all-MiniLM-L6-v2",
      "metrics": {
        "map": 0.8234,
        "recall": 0.9123,
        "precision": 0.7456,
        "ndcg": 0.8567,
        "mrr": 0.6234
      },
      "timing": {
        "embedding_time": 2.5,
        "docs_processed": 100,
        "docs_per_second": 40.0,
        "avg_time_per_doc": 0.025
      }
    }
  ],
  "corpus_stats": {
    "total_documents": 150,
    "total_chunks": 2340,
    "avg_chunks_per_doc": 15.6
  }
}
```

**File**: `utils/chromadb_utils.py`
- Add `save_raw_results` parameter to `evaluate_with_chromadb()`
- Create `save_evaluation_results()` function
- Use `config.raw_results_file` for output path

#### 1.2 Configuration Updates in `config.py`
**Objective**: Add aggregate report configuration options.

**Changes**:
- Add aggregate report paths:
  ```python
  aggregate_results_dir = "reports/aggregate"
  aggregate_raw_data_dir = "reports/aggregate/raw"
  ```
- Add aggregate report settings:
  ```python
  aggregate_include_datasets = []  # Empty means all available
  aggregate_statistical_tests = True
  aggregate_generate_visualizations = True
  ```

### Phase 2: Aggregate Analysis Engine

#### 2.1 Core Aggregation Module: `utils/aggregate_report_utils.py`
**Objective**: Create comprehensive cross-dataset analysis functions.

**Functions to implement**:

**Data Loading**:
- `load_dataset_results(dataset_name: str) -> Dict`: Load JSON results for a dataset
- `load_multiple_datasets(dataset_names: List[str] = None) -> Dict[str, Dict]`: Load results for multiple datasets

**Aggregation Logic**:
- `aggregate_model_performance(datasets: Dict[str, Dict]) -> Dict[str, Dict]`: Aggregate metrics per model across datasets
- `normalize_metrics_across_datasets(datasets: Dict[str, Dict]) -> Dict[str, Dict]`: Handle different metric configurations

**Statistical Analysis**:
- `calculate_model_rankings(datasets: Dict[str, Dict], metric: str) -> Dict[str, List]`: Rank models per dataset
- `perform_significance_tests(model_a: str, model_b: str, datasets: Dict[str, Dict], metric: str) -> Dict`: Paired t-tests across datasets
- `calculate_consistency_scores(model_results: Dict[str, List]) -> Dict[str, float]`: Measure model performance consistency

**Visualization Generation**:
- `generate_cross_dataset_comparison_chart(model_results: Dict, output_dir: str) -> Dict[str, str]`: Radar/spider charts
- `generate_model_ranking_heatmap(rankings: Dict, output_dir: str) -> str`: Heatmap of model rankings across datasets
- `generate_performance_distribution_plots(model_results: Dict, output_dir: str) -> Dict[str, str]`: Box plots, violin plots

#### 2.2 Statistical Methods
**Objective**: Implement robust statistical comparison methods.

**Key Functions**:
- `paired_t_test(scores_a: List[float], scores_b: List[float]) -> Tuple[float, float]`: Statistical significance testing
- `cohen_d_effect_size(scores_a: List[float], scores_b: List[float]) -> float`: Effect size calculation
- `calculate_win_tie_loss_matrix(model_results: Dict[str, Dict]) -> pd.DataFrame`: Win-tie-loss analysis across datasets

### Phase 3: Report Generation

#### 3.1 Aggregate Report Generator
**Objective**: Create publication-ready aggregate reports.

**Main Function**: `generate_aggregate_report(datasets: List[str], output_dir: str) -> str`

**Report Structure**:
1. **Executive Summary**
   - Overall best performing models across datasets
   - Key findings and statistical significance
   - Dataset characteristics summary

2. **Methodology**
   - Datasets included and their characteristics
   - Evaluation metrics and configurations
   - Statistical analysis methods

3. **Cross-Dataset Model Comparison**
   - Average performance rankings
   - Performance consistency analysis
   - Statistical significance results

4. **Dataset-Specific Insights**
   - Best models per dataset
   - Performance variations
   - Dataset difficulty analysis

5. **Visualizations**
   - Cross-dataset performance radar charts
   - Model ranking heatmaps
   - Performance distribution plots
   - Statistical significance matrices

#### 3.2 CLI Integration in `rag_benchmark.py`
**Objective**: Add aggregate report generation to CLI.

**New CLI Flags**:
- `--generate-aggregate-report`: Generate aggregate report across datasets
- `--aggregate-datasets DATASET1,DATASET2`: Specify datasets to include (default: all)
- `--aggregate-output-dir DIR`: Custom output directory for aggregate reports

**Example Usage**:
```bash
# Generate aggregate report for all datasets
python rag_benchmark.py --generate-aggregate-report

# Generate aggregate report for specific datasets
python rag_benchmark.py --generate-aggregate-report --aggregate-datasets education,medical,legal

# Custom output directory
python rag_benchmark.py --generate-aggregate-report --aggregate-output-dir reports/conference_paper
```

### Phase 4: Testing and Validation

#### 4.1 Unit Tests in `tests/test_aggregate_report_utils.py`
**Objective**: Comprehensive testing of aggregate functionality.

**Test Coverage**:
- Data loading from multiple JSON files
- Metric aggregation with different configurations
- Statistical significance testing
- Visualization generation (mocked)
- Error handling for missing datasets/inconsistent metrics

#### 4.2 Integration Tests
**Objective**: End-to-end testing of aggregate report generation.

**Test Scenarios**:
- Aggregate report with 2+ datasets
- Handling datasets with different metric configurations
- Statistical analysis validation
- CLI integration testing

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
- Sample aggregate report Markdown file
- Example visualizations
- Statistical analysis examples

## Implementation Timeline

### Week 1: Foundation
- [ ] JSON result storage in `chromadb_utils.py`
- [ ] Configuration updates in `config.py`
- [ ] Basic data loading functions in `aggregate_report_utils.py`

### Week 2: Core Aggregation
- [ ] Aggregation logic implementation
- [ ] Statistical analysis functions
- [ ] Basic visualization generation

### Week 3: Report Generation
- [ ] Aggregate report generator
- [ ] CLI integration
- [ ] Advanced visualizations

### Week 4: Testing & Polish
- [ ] Comprehensive unit tests
- [ ] Integration testing
- [ ] Documentation updates
- [ ] Example reports

## Risk Mitigation

### Technical Risks
1. **Metric Configuration Inconsistencies**: Handle via normalization functions that detect and align metric sets
2. **Memory Usage**: Process datasets sequentially for large-scale aggregation
3. **Statistical Validity**: Implement proper statistical tests with validation

### Operational Risks
1. **Dataset Availability**: Graceful handling of missing/corrupted dataset results
2. **Performance**: Optimize aggregation for large numbers of datasets/models
3. **Backward Compatibility**: Ensure existing individual reports continue to work

## Success Criteria

1. **Functionality**: Generate aggregate reports comparing 3+ datasets with statistical analysis
2. **Quality**: Publication-ready visualizations and statistically sound comparisons
3. **Integration**: Seamless CLI integration with existing workflow
4. **Testing**: 90%+ test coverage for aggregate functionality
5. **Documentation**: Complete user guide and examples

## Dependencies

- **matplotlib** for advanced visualizations
- **scipy** for statistical testing
- **pandas** for data manipulation
- **numpy** for numerical computations

## Future Enhancements

1. **Interactive Web Reports**: HTML-based interactive visualizations
2. **Automated Model Selection**: ML-based model recommendation across datasets
3. **Performance Prediction**: Train models to predict performance on new datasets
4. **Real-time Aggregation**: Streaming updates as individual evaluations complete