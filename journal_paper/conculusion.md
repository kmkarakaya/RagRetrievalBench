# Conclusion

This journal draft demonstrates the effectiveness of an end-to-end embedding benchmarking pipeline for local dataset evaluation and practical model selection. The frozen multi-dataset snapshot generated on 2026-03-05 shows that embedding behavior is dataset-dependent and that local benchmarking is necessary for fit-for-purpose deployment decisions. [Aggregate_Report_2026_03_05]

The run demonstrates language-sensitive variation (`education_eng` vs `education_tr`) and domain-sensitive variation (`education_tr` vs `law_tr`) under one fixed setup with 3 datasets and 5 models. The pipeline also exposes quality-speed tradeoffs through joint reporting of retrieval metrics and operational metrics. [Aggregate_Report_2026_03_05][Raw_Education_Eng_2026_03_05][Raw_Education_Tr_2026_03_05][Raw_Law_Tr_2026_03_05]

The main outcome is practical utility: the generated reports provide automatic benchmarking reports across various metrics and well-structured dynamic report outputs (timestamped markdown/pdf + visualizations), enabling cross-dataset comparison for dataset-specific model selection and helping users choose the best suitable embedding model for user/application requirements.

The implementation is publicly available at `https://github.com/kmkarakaya/RagRetrievalBench.git`, and the workflow is intended to be pipeline reusable by any developer. [GitHub_RagRetrievalBench]

Dataset provenance has been documented for this draft:
- Education datasets: TED University regulations/guidelines URL, retrieved on 01/01/2026.
- Law dataset: BDDK regulations URL, retrieved on 01/01/2026.
[TED_Regulations][BDDK_Mevzuat]

## Boundaries and Pending Validation

Supported claims are bounded to:
- the three evaluated datasets
- the frozen run timestamps
- the configured metrics and retrieval setup

Pending items before submission-quality lock:
1. Light human qrels audit (sampling protocol and agreement metric)
2. Compute environment appendix (CPU/GPU/RAM/software versions)

Current manuscript state:
- Draft evidence complete, validation appendix pending.

## Future Work

1. Expand provenance appendix to per-document source mapping and add human-audit validity appendix.
2. Add sensitivity analyses for query count and candidate pool settings.
3. Extend cross-dataset evaluation with additional Turkish and multilingual domains.
4. Test robustness under alternative chunking and retrieval cutoff settings.
