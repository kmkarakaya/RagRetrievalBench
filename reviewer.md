# Reviewer Report

## Recommendation

**Decision: Reject in the current form, with encouragement to resubmit after major methodological revision.**

The paper addresses a relevant practical problem: selecting embedding models for local RAG retrieval under language, domain, and operational constraints. The manuscript is clearly organized, the pipeline framing is useful for practitioners, and the inclusion of timing, raw-result preservation, and uncertainty-aware interpretation is a strength. However, the current evidence is not strong enough for journal acceptance. The main limitations are methodological rather than cosmetic: the relevance judgments are produced without human validation, the candidate pool used for qrels construction appears to depend on one of the evaluated models, the benchmark is very small, and the statistical analysis is underpowered. These issues directly affect the credibility of the reported model rankings and the claimed language/domain effects.

My recommendation is therefore **reject**, not because the topic is unimportant, but because the current experimental design cannot support the strength of the journal-level claims. A substantially revised version could become publishable if it validates the qrels, removes or controls the model-dependent candidate-pool bias, expands the benchmark, and reports enough implementation detail for independent reproduction.

## Summary of the Paper

The paper presents a local benchmarking pipeline for corpus-specific embedding-model selection in RAG systems. The proposed workflow ingests local documents, chunks them, generates synthetic queries, constructs qrels using an LLM judge, builds model-specific vector indexes, evaluates retrieval quality at `k=10`, and generates dataset-level and aggregate reports. The empirical snapshot covers three datasets: English education, Turkish education, and Turkish law/regulation. Five Sentence Transformers models are evaluated using six retrieval metrics and timing measurements.

The main empirical findings are that English education results are relatively clustered, Turkish datasets favor multilingual models, legal/regulatory Turkish is harder than Turkish education, and no single model dominates both retrieval quality and latency. The paper positions the contribution as a reproducible practitioner-facing decision-support pipeline rather than a universal embedding leaderboard.

## Overall Strengths

The paper is motivated by a real deployment problem. Local RAG systems often do need corpus-specific embedding selection, and generic leaderboards are insufficient for operational decisions.

The manuscript avoids claiming universal model superiority and repeatedly bounds the findings to the reported snapshot. This restraint is appropriate and should be kept.

The pipeline structure is understandable. The staged workflow from ingestion to reporting is useful, especially the separation between raw result artifacts and human-readable reports.

The inclusion of operational metrics is valuable. Query latency and chunking throughput are relevant to embedding-model selection and are often omitted from retrieval papers.

The paper attempts to include statistical decision support rather than relying only on descriptive tables. Even though the current statistical design is weak, the intent is appropriate.

## Major Concerns

### 1. The qrels construction protocol may bias the evaluation toward M5

The manuscript states that `M5` is "also used to support candidate retrieval during qrels construction" while also being one of the evaluated models. This is a serious methodological problem. If qrels are constructed from a candidate pool retrieved by `M5`, then the set of potentially relevant chunks is conditioned on what `M5` can retrieve. Other models are judged against relevance evidence that may omit relevant passages they retrieve but `M5` did not include in the candidate pool.

This can inflate `M5`'s apparent performance or at least make the comparison asymmetric. The problem is especially important because `M5` is reported as the strongest aggregate model and the strongest Turkish model. The paper cannot treat this as a neutral benchmark unless it shows that the qrels candidate pool is model-independent, pooled across all evaluated models, or validated against a sufficiently broad retrieval source.

Required revision:

- Build qrels from a pooled retrieval set across all evaluated models, a strong external retriever, lexical BM25 plus dense retrieval, or human-selected candidate passages.
- Re-run the evaluation after removing any privileged role for an evaluated model.
- Report whether rankings change under pooled qrels.
- If `M5` remains the best model, show that the result survives this correction.

### 2. Synthetic queries and LLM-generated qrels are not validated

The paper relies on an LLM for both query generation and binary relevance judgment. This is scalable, but the current manuscript provides no empirical validation of the generated queries or qrels. There is no human audit, no inter-annotator agreement, no human--LLM agreement, no examples of accepted/rejected qrels, and no analysis of judge errors.

This weakens the central claim that the pipeline produces reliable model-selection evidence. The related work correctly notes that LLM judges can be imperfect and language-sensitive, but the paper does not operationalize that caution in its own experiment.

Required revision:

- Include a sampled human audit of generated queries and relevance labels.
- Report agreement measures or at least a structured error analysis.
- Provide representative query/qrels examples for each dataset.
- Report the prompt, model settings, temperature, batch mode behavior, and any retry or filtering logic.
- Distinguish query-generation validity from relevance-judgment validity; these are separate risks.

### 3. The benchmark is too small for the claimed language/domain analysis

The empirical snapshot contains only three datasets and 150 synthetic queries. The `law_tr` dataset has only two source documents, even though it produces many chunks. This is not enough to support strong conclusions about language sensitivity or domain sensitivity. The paper does state that claims are snapshot-bounded, but it still frames the results as evidence for language and domain effects.

The design has only one English education dataset, one Turkish education dataset, and one Turkish legal/regulatory dataset. Language and domain are therefore confounded with dataset identity, source collection, document structure, document count, chunk distribution, and query generation artifacts. The paper cannot isolate "language effect" from "this English dataset versus this Turkish dataset," nor "domain effect" from "these two Turkish collections with different document structures."

Required revision:

- Add more datasets per language and per domain.
- Include at least multiple English and Turkish corpora in the same domain, and multiple Turkish domains with more than one source collection each.
- Treat current language/domain claims as illustrative case observations unless the dataset design is expanded.
- Report confidence intervals or bootstrap intervals over queries, not only dataset-level aggregates.

### 4. Statistical testing is underpowered and partly misleading

The statistical decision-support section is a useful idea, but the implementation is not convincing. The Friedman test and paired t-tests are computed over only three dataset-level observations. A paired t-test with `n=3` is not reliable evidence for model superiority, and the paper itself notes the limitation. However, Table `tbl:statistical_decision_support` still labels `M5 vs. M3` as significant under the report configuration.

This risks giving readers a false sense of inferential support. The more appropriate unit of analysis should likely be query-level performance, with care taken for dataset clustering, or a hierarchical/bootstrap analysis that respects dataset and query structure.

Required revision:

- Avoid reporting ordinary paired t-tests over three dataset-level points as decision-grade evidence.
- Use query-level paired tests within each dataset, bootstrap confidence intervals, randomization tests, or hierarchical models.
- Apply multiple-comparison correction if many model pairs are tested.
- Report effect sizes with uncertainty intervals, not only p-values.
- Make the statistical output clearly advisory until the benchmark includes more independent datasets.

### 5. Reproducibility claims exceed the details provided

The paper repeatedly emphasizes reproducibility, but important experimental details are missing from the manuscript. The reader needs enough detail to reproduce both the quality and timing results.

Missing or under-specified details include:

- hardware and compute environment;
- CPU/GPU use;
- library versions;
- ChromaDB index configuration;
- exact random seeds and sampling method for seed chunks;
- LLM prompt templates;
- LLM decoding parameters;
- PDF text extraction method;
- text normalization rules;
- duplicate or near-duplicate handling;
- whether timing includes embedding, vector search, network calls, or only local retrieval;
- whether caches were warmed;
- whether models were run on the same device and precision.

The public repository may contain some of this information, but a journal paper should summarize the key reproducibility conditions in the manuscript itself.

## Section-by-Section Critique

## Title

The title, **"Benchmarking of Embedding Models,"** is too broad and underspecified. The paper is not a general embedding-model benchmark; it is a local RAG retrieval benchmarking pipeline with a small multilingual/domain-specific demonstration. A better title would mention local RAG, corpus-specific model selection, or reproducible retrieval benchmarking.

Suggested direction:

**"A Local RAG Retrieval Benchmarking Pipeline for Corpus-Specific Embedding Model Selection"**

## Abstract

The abstract is clear, but it overstates the maturity of the evidence. Phrases such as "supports transparent local model selection" and "one reproducible workflow" are acceptable as goals, but the abstract should also disclose the core limitation: qrels are synthetic and LLM-judged without reported human validation.

The abstract reports that `M5` is the strongest aggregate candidate. Because `M5` is also used during qrels construction, this result should not be foregrounded without a caveat. The abstract should either mention that qrels are generated from an automated candidate pool or defer model-specific claims until the evaluation protocol is strengthened.

## Highlights and Keywords

The highlights are serviceable but generic. The first two highlights describe the pipeline, and the third says validation on three datasets shows dataset-dependent ranking differences. The word "validation" is too strong given the lack of human qrels validation. "Demonstration" or "case study" would be more accurate.

The keywords are appropriate but could include `RAG Evaluation`, `Synthetic Queries`, or `Relevance Judgments` because these are central to the paper.

## Introduction

The introduction motivates the problem well. It correctly argues that public leaderboards do not replace corpus-specific evaluation. The research questions are clear and aligned with the later sections.

The weakness is that key terms remain vague. "Actionable evidence," "pipeline utility," "consistency diagnostics," and "statistical decision support" are not defined operationally. The reader should know in advance what would count as successful pipeline utility beyond producing reports.

The contribution claims are also broader than the empirical support. The paper claims cross-dataset comparability, but the datasets are too few and too confounded to support robust comparability claims. The introduction should distinguish between the pipeline contribution and the empirical demonstration more sharply.

Recommended revisions:

- Define what "actionable" means in measurable terms.
- State that the empirical study is a small demonstration, not a validation across language/domain conditions.
- Add a short limitations preview in the introduction, especially around synthetic qrels.

## Related Work

The related work section is extensive and current, but it reads more like an annotated literature list than a focused argument. Many studies are summarized in sequence without enough synthesis of how they differ from the proposed pipeline.

The section should more directly position this paper against established retrieval benchmark practices, especially pooling, qrels construction, BEIR-style benchmark design, MTEB-style embedding evaluation, and RAG evaluation frameworks. The paper cites many recent RAG and embedding studies, but the methodological benchmark-design issue is the core of this paper and deserves more focused treatment.

The discussion of LLM-as-judge work is useful, but it creates a problem for the manuscript: the paper acknowledges judge reliability concerns in prior work, then does not validate its own judge. The related work should be connected to concrete design choices in the method.

Recommended revisions:

- Shorten descriptive summaries and organize the section around methodological gaps.
- Add a focused discussion of qrels pooling and retrieval-evaluation benchmark construction.
- Use the LLM-judge literature to justify a validation protocol, not only to motivate automation.
- Clarify how the current work differs from existing RAG benchmark/reporting tools beyond being local and practitioner-facing.

## Method

The method section is readable and the workflow is understandable. The staged artifacts are a strength.

However, the method lacks enough procedural specificity. The description says seed chunks are sampled, queries are generated, candidates are retrieved, and an LLM assigns binary labels. For a benchmark paper, this is not enough. The details of sampling, prompting, candidate retrieval, judging, and qrels filtering are central to validity.

The most serious method issue is the qrels candidate-pool construction. A bounded candidate pool of 20 is small, and if it is produced by `M5`, then qrels coverage is model-dependent. This undermines fair comparison.

The method also lacks baselines for the pipeline itself. Since the contribution is a benchmarking workflow, the reader needs to know why this workflow is better than simpler alternatives such as:

- manual query/qrels sampling;
- BM25 or hybrid candidate pooling;
- pooled dense retrieval over all candidate models;
- existing BEIR/MTEB-style evaluation tooling;
- direct use of public benchmarks plus local smoke tests.

Recommended revisions:

- Specify the full qrels construction algorithm.
- Use model-pooled candidate retrieval or a model-independent retriever.
- Report prompts and judging criteria.
- Include a human audit protocol.
- Add sensitivity analysis for candidate-pool size, chunk size, query count, and retrieval cutoff.

## Experiments

The experiment section is the weakest part of the paper from a journal-review standpoint. The experimental snapshot is too small and too confounded to carry the stated empirical claims.

The dataset design has three main problems.

First, language is confounded with dataset identity. There is one English education corpus and one Turkish education corpus. Differences may reflect language, source-document differences, translation differences, policy-document structure, or query generation differences.

Second, domain is confounded with corpus structure. The Turkish law dataset has only two source documents but 723 chunks, while the Turkish education dataset has 29 documents and 619 chunks. The law result may reflect document length, document type, chunk density, or qrels generation difficulty rather than legal-domain difficulty.

Third, 50 synthetic queries per dataset is limited. The paper should justify why 50 queries are enough or show stability curves indicating that rankings stabilize as query count increases.

The model roster is reasonable as an initial open-source baseline, but it is narrow. The paper evaluates only Sentence Transformers models, with no BM25, hybrid retrieval, reranker, current commercial embedding model, or domain-adapted model. That is acceptable if framed as a pipeline demonstration, but not if the paper aims to make substantive model-selection findings.

The timing results are interesting, but the lack of hardware and runtime details makes them hard to interpret. Query latency in milliseconds is meaningless without device, batching, cache, index, and measurement details.

Recommended revisions:

- Expand the dataset set or narrow the empirical claims.
- Add query-count stability analysis.
- Add at least one lexical baseline such as BM25 and preferably a hybrid baseline.
- Report hardware and timing methodology.
- Explain why the selected models are sufficient for the paper's target readership.

## Results

The results are clearly presented and the tables are easy to read. The paper does a good job separating dataset-level results, language comparison, domain comparison, quality-speed tradeoff, and statistical decision support.

The problem is not presentation; it is evidential validity. Many reported interpretations are plausible, but not established by the design.

Specific concerns:

- The claim that `education_eng` is easiest and `law_tr` is hardest may be true, but difficulty is influenced by qrels construction, document length, query generation, source type, and chunk distribution.
- The language-effect section compares only two education corpora, so it cannot isolate language from dataset-specific differences.
- The domain-effect section compares only two Turkish corpora with very different document structure, so it cannot isolate domain from corpus structure.
- The quality-speed section is useful, but timing results lack reproducibility details.
- The consistency diagnostics table uses terms such as "All-metric CV," "Worst drop," and "Score range" without enough definition in the surrounding text.
- The statistical section should not label any pairwise result as significant when only three dataset-level observations drive the test.

The paper should also discuss whether `Success@10` near 1.00 on `education_eng` indicates that the query/qrels task may be too easy or too directly generated from chunks. Synthetic queries generated from seed chunks can produce retrieval tasks that are less representative of real user information needs.

Recommended revisions:

- Re-run results with unbiased pooled qrels.
- Add per-query uncertainty intervals.
- Add examples of successes and failures.
- Include an error analysis for low-performing models and hard queries.
- Define all aggregate diagnostics precisely.
- Reframe language/domain results as preliminary observations unless more datasets are added.

## Conclusion and Future Work

The conclusion is appropriately cautious in several places and acknowledges the small snapshot, synthetic qrels, and need for human audit. This is good, but some of these acknowledged limitations are central enough that they should be addressed before publication rather than deferred to future work.

In particular, human audit of qrels quality should not be future work for a paper whose empirical evidence depends on LLM-generated qrels. Similarly, compute-environment details should not be future work when timing results are part of the paper's contribution.

The conclusion should be shortened after revision and should avoid restating results that remain methodologically uncertain.

## Presentation, Style, and Structure

The manuscript is generally well written, but it is repetitive. The same points recur many times: local benchmarking, fit-for-purpose selection, fixed protocol, statistical caution, and no universal model ranking. This makes the paper longer than necessary without adding evidence.

The figures appear to be conceptual workflow diagrams. They are useful, but the paper includes many workflow/reporting figures relative to the amount of empirical validation. The journal version would benefit from fewer conceptual diagrams and more validation artifacts, such as qrels examples, error analysis, and stability plots.

The manuscript should avoid saying "validation" when it means "demonstration." The current experiment demonstrates the pipeline; it does not fully validate the benchmark.

## Minor Issues

- The title is too generic.
- The paper should define `qrels` at first use for readers outside IR.
- The phrase "query-construction judge" is awkward; query generation and relevance judging should be separated terminologically.
- `M2` is described as a higher-capacity monolingual baseline; the paper should be precise about model training language and intended use rather than relying on broad family labels.
- The paper should explain whether `M5` was used only for qrels candidate retrieval or also in other upstream stages.
- The retrieved candidate pool size of 20 needs justification.
- The paper should report whether non-relevant judgments are stored and used, or whether only relevant qrels are retained.
- The source retrieval date is given, but the exact curated document list should be referenced or summarized.
- The manuscript contains a possible hidden encoding artifact before the `Results` section in the compiled TeX source.
- The bibliography and citations should be checked carefully because the related work relies heavily on very recent sources.

## Required Changes Before Acceptance

The paper should not be accepted without the following changes:

1. Rebuild qrels using a model-independent or pooled candidate-generation strategy.
2. Add human validation or a rigorous audit of synthetic queries and qrels.
3. Expand the dataset design or substantially narrow the language/domain claims.
4. Replace underpowered dataset-level t-tests with more appropriate uncertainty analysis.
5. Report full reproducibility details for prompts, seeds, sampling, hardware, software, timing, and indexing.
6. Add sensitivity analyses for query count, candidate-pool size, chunk size, and retrieval cutoff.
7. Include qualitative examples and error analysis.

## Final Assessment

The paper has a useful practical direction and could become a strong applied/reproducibility contribution. In its current form, however, the benchmark evidence is too fragile for acceptance. The most serious issue is that the relevance judgments appear to be constructed through a candidate pool involving an evaluated model, which undermines the fairness of the reported rankings. Combined with unvalidated LLM qrels, only three datasets, and weak statistical testing, this prevents the paper from supporting its main empirical claims at journal standard.

**Final decision: Reject.**
