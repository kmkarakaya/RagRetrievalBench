# Pre-Submission Reviewer Report

## Review Basis and Overall Recommendation

This report applies a strict, general Elsevier computer-science journal standard to the current version of the paper, **“A Local RAG Retrieval Benchmarking Pipeline for Corpus-Specific Embedding-Model Selection.”** The review covers the front matter in `journal_paper/manuscript.tex`, the six included section files, the bibliography, and—where necessary to verify claims—the released analysis and evaluation implementation.

**Likely recommendation: Reject in the present form, with encouragement to resubmit after substantial methodological revision.**

The paper addresses a relevant practitioner problem and is substantially stronger than an ordinary software-description paper. Its positive features include a clearly staged workflow, a model-independent pooled-qrels construction, preservation of positive and negative judgments, query-level uncertainty intervals, explicit limitations, operational measurements, and released artifacts. The CAS template lint also passes with no errors or warnings, so formatting compliance is not a rejection concern.

The remaining problems concern scientific validity and journal-level contribution. In particular, the central language/domain interpretation is not identifiable from the dataset design, the synthetic benchmark has no independent human validation, and the paper does not yet establish that its integrated workflow contributes sufficiently beyond established retrieval-evaluation practice. Several additional analysis choices could materially affect the reported rankings.

The current paper should **not** be criticized for using an M5-only qrels pool or for lacking query-level uncertainty analysis. Those issues have been addressed: the main qrels use a union over all five evaluated models, the older M5-only pool is retained only as a robustness comparison, and query-level bootstrap intervals are reported. The comments below concern unresolved issues in the current version.

## Reject Reasons

These are submission-blocking concerns that could independently justify rejection under a demanding journal review.

1. **The experimental design cannot identify the claimed language and domain effects.**

   - The Abstract states that “language rather than domain dominates difficulty,” and the Introduction frames RQ2 and RQ3 as language- and domain-sensitivity questions. The Results and Conclusion then use one English education corpus, one Turkish education corpus, and one Turkish law/regulation corpus to support these interpretations.
   - Language and domain are inseparable from corpus identity, source selection, document structure, document count, query-generation behavior, and qrels composition. The `law_tr` condition is especially different: it contains two long documents and 723 chunks, whereas each education corpus contains 29 documents. A difference between these datasets is not an isolated language or domain effect.
   - The paper acknowledges this confounding in the Language Effect, Domain Effect, and Limitations subsections, but the strongest statements in the Abstract, Cross-Dataset Headline Findings, and Conclusion still treat language as the dominant explanatory factor. A limitation statement does not repair an unidentifiable design.
   - The domain evidence also does not support the corresponding premise: the model ordering is preserved between the two Turkish corpora and most changes are small and mixed. This demonstrates that the pipeline can *compare* two corpora, but it does not demonstrate a domain-conditioned ranking change.
   - **Required strengthening:** either add multiple independent corpora per language and domain, preferably with a crossed or matched design, or remove causal/effect language and recast RQ2/RQ3 as descriptive case-study questions. A stronger language study would use aligned or closely matched English/Turkish content plus independent corpora; a stronger domain study would include several corpora per domain and control document structure.

2. **The benchmark ground truth is not independently validated.**

   - The Shared Evaluation Setup states that Gemini 2.5 Flash-Lite generates the synthetic queries and also judges candidate relevance. The Limitations subsection confirms that there is no human audit or human–LLM agreement analysis.
   - Model-independent pooling improves fairness among the five retrievers, but it does not validate query realism, multilingual judgment quality, label consistency, or the completeness of relevant passages. The same LLM family acting as generator and judge may also reward artifacts of its own query formulation.
   - The paper’s primary empirical outputs—model rankings, bootstrap intervals, language comparisons, and quality recommendations—are all conditional on these unvalidated queries and labels. Calling the evidence “actionable” or sufficient for model selection is therefore premature.
   - **Required strengthening:** conduct a stratified human audit across all three datasets, covering query naturalness, answerability, positive labels, hard negatives, and zero-positive queries. Use at least two knowledgeable annotators for a meaningful subset, report agreement and adjudication, compare human and LLM decisions by language, and separate generator-quality analysis from judge-quality analysis. If full validation is infeasible, narrow the contribution to automated *screening* rather than decision-grade benchmarking.

3. **The journal-level novelty and utility claims are not demonstrated against credible alternatives.**

   - RQ1 defines pipeline utility as the ability to produce a ranked summary and preserve artifacts. The experiment then demonstrates that the implemented pipeline produces those outputs. This is close to a self-fulfilling criterion rather than an evaluation of scientific or practical utility.
   - The proposed workflow integrates established components: PDF extraction, recursive chunking, LLM query generation, pooled relevance judging, Sentence-Transformers embeddings, vector retrieval, standard IR metrics, and report generation. Integration can be valuable, but the paper does not compare the workflow with BEIR/MTEB-style evaluation tooling, TREC-style pooling practice, existing RAG evaluation frameworks, or a simpler local benchmark script.
   - There is no study of setup effort, error reduction, reproducibility improvement, practitioner decision quality, or report usefulness. There is also no ablation showing which proposed reporting or governance components materially improve model selection.
   - **Required strengthening:** explicitly identify the novel technical or methodological contribution and evaluate it. Suitable evidence could include a comparison with established benchmark workflows, an ablation of the proposed artifact/reporting layers, a reproducibility study across independent runs or practitioners, or a scoped user study. If the contribution is primarily engineering, target and frame the paper as a software/tool article and provide the software-quality evidence expected by that article type.

## Major Revision Reasons

These issues may not independently require rejection, but each requires substantive analysis or rewriting before submission.

1. **Re-evaluate the retrieval geometry; non-normalized squared-L2 comparison may distort model rankings.**

   - The Experiments section reports “default non-normalized encoding” and ChromaDB’s squared-Euclidean (`L2`) space. The implementation likewise constructs `SentenceTransformerEmbeddingFunction` without requesting normalization and sets `hnsw:space` to `l2`.
   - L2 distance and cosine similarity yield the same ranking only for vectors with equal norms or explicit normalization. The configuration comment that the two “typically produce the same ordering” is not a methodological guarantee for non-normalized embeddings, especially across different model families and dimensions.
   - The five models are commonly evaluated with cosine similarity or normalized embeddings. Using raw L2 may mix semantic direction with model-specific vector-norm behavior, so the headline ranking could be configuration-specific.
   - **Required revision:** rerun the full comparison with normalized cosine retrieval and, ideally, each model’s recommended similarity. Report rank correlations and score changes across L2, normalized L2, and cosine settings. If the ranking changes, revise all model-selection conclusions; if it is stable, present that result as a sensitivity check.

2. **Correct the bootstrap sample-size description and disclose zero-positive-query handling.**

   - The Statistical Decision Support subsection, bootstrap table caption, and forest-plot caption repeatedly say that the analysis covers 150 queries.
   - The released query-level scoring code drops queries with no relevant documents, matching the Sentence-Transformers evaluator. The frozen bootstrap artifact used for the reported values contains 48 scored `education_eng` queries and 50 for each Turkish dataset: **148 scored queries, not 150**.
   - Excluding zero-positive queries changes the estimand and can inflate success and effectiveness estimates. The paper currently reports 50 generated queries per dataset without explaining the smaller evaluation denominator.
   - **Required revision:** report generated, judged, positive-bearing, excluded, and scored query counts separately for every dataset; explain why queries are excluded; and perform a sensitivity analysis using an explicit policy for zero-positive queries. Correct all “150-query” statistical claims to the actual denominator.

3. **Revise the inferential analysis and the interpretation of bootstrap “p-values.”**

   - The reported paired procedure bootstraps the observed per-query differences and defines a two-sided tail proportion around zero. This is useful for interval estimation but is not clearly a null-centered hypothesis test. The manuscript calls the result a two-sided bootstrap p-value without specifying the exact test construction.
   - Four M5-versus-model comparisons are reported after M5 is selected as the best observed model, with no multiplicity adjustment. The additional `education_eng` comparison is also highlighted as significant.
   - Queries are treated as independent even though they are nested within three datasets and originate from chunks within a small number of source documents. Pooling all scored queries ignores dataset and document clustering and may understate uncertainty.
   - **Required revision:** make confidence intervals primary; use a valid paired permutation/randomization test if p-values are retained; apply a stated multiplicity procedure such as Holm correction; and use a hierarchical or cluster bootstrap that resamples datasets/documents and then queries where the design permits. Report dataset-specific effects before any pooled estimate.

4. **Remove or redesign the “all-metric” consistency diagnostics.**

   - The Cross-Dataset Headline Findings calculate one coefficient of variation, worst drop, and score range over all six metrics and all three datasets.
   - MAP, recall, precision, NDCG, MRR, and success rate have different definitions, baselines, variances, and numerical scales. Treating their raw values as one commensurate set makes the resulting CV and range difficult to interpret. A high range may reflect the expected difference between precision and success rate rather than cross-dataset instability.
   - These diagnostics are used to claim that M5 has the “smallest consistency penalty,” so the problem affects a headline finding rather than a decorative table.
   - **Required revision:** calculate stability separately for each metric across datasets, or use within-condition ranks or normalized deviations before aggregation. Predefine the aggregation rule and justify why it measures robustness. Remove the current diagnostics if a valid interpretation cannot be established.

5. **Reconcile RQ3 and the conclusion with the actual domain result.**

   - RQ3 asks whether the pipeline can expose domain-conditioned ranking changes. The Domain Effect subsection reports that the ranking is preserved and that changes are small and mixed.
   - The Conclusion nevertheless says the language and domain analyses answer RQ2 and RQ3 by showing that embedding behavior “changes materially when the corpus changes.” That description fits the language comparison but not the reported domain comparison.
   - **Required revision:** answer RQ3 directly as a null or inconclusive finding for this snapshot. Distinguish “the pipeline can display a comparison” from “the experiment demonstrates a domain effect.” Align the Abstract, contribution claims, Results, Conclusion, and publication plan with the same bounded interpretation.

6. **Add stronger baselines and a more defensible model roster.**

   - The model set contains five Sentence-Transformers models selected largely by download popularity. It lacks a lexical baseline, a hybrid baseline, a reranking condition, a domain-adapted model, and stronger current multilingual embedding models.
   - A BM25 baseline is important for detecting whether dense retrieval is actually needed for these regulatory corpora. A hybrid baseline would also connect the paper to realistic RAG deployment practice.
   - **Required revision:** add at least BM25, a reproducible hybrid configuration, and one competitive contemporary multilingual model. Explain inclusion criteria using model capabilities, licensing, resource requirements, and target deployment constraints rather than download count alone.

7. **Perform sensitivity analyses for the fixed protocol choices.**

   - The experiment uses one chunk size and overlap, 50 queries per dataset, a top-20-per-model judgment pool, L2 retrieval, and `k=10`. These are described as practitioner defaults and deferred to future work.
   - The paper’s contribution is a benchmarking method, so showing that conclusions are not artifacts of its own default parameters is central rather than optional future work.
   - **Required revision:** at minimum report query-count stability curves, pool-depth saturation or residual-judging results, chunking sensitivity, retrieval-cutoff sensitivity, and similarity-function sensitivity. Show whether the top model and recommended shortlist remain stable.

8. **Strengthen the candidate-pool robustness analysis.**

   - The pooled-qrels construction is a real improvement, and the increase in positive judgments over the M5-only pool is informative.
   - However, an unchanged ranking under a narrower, known-biased pool does not establish that the five-model pool is complete or unbiased. Relevant chunks missed by every evaluated model remain unjudged, and the pool is optimized for the same closed roster later evaluated.
   - **Required revision:** measure pool saturation as systems or depth are added, include a lexical or external retriever in the pool, and manually judge a random sample of unpooled corpus chunks or residual results. State clearly that the qrels support evaluation of the pooled systems and may not be reusable for arbitrary future systems without additional judging.

9. **Make timing results statistically and operationally reproducible.**

   - Timing is reported from a single CPU machine and described as cold, but the paper does not provide the CPU model, RAM, thread settings, storage, number of repetitions, warm-up policy, or variability.
   - “Embedding throughput” includes corpus embedding and insertion into ChromaDB, while “query latency” includes query embedding and vector search. These compound measures are useful operationally but do not isolate model inference from storage behavior.
   - **Required revision:** run repeated trials, report medians and dispersion, separate cold-start and warm-query behavior, disclose complete hardware/thread configuration, and separate embedding computation from index insertion where possible. Define the weighting used for aggregate latency.

10. **Create a durable, independently executable reproducibility package.**

    - The paper cites a live GitHub repository and run identifiers, but a mutable repository URL is not a permanent experimental record. Gemini service behavior and model aliases can also change.
    - **Required revision:** publish a tagged release or archived DOI with the exact commit, environment lockfile, prompts, frozen queries/qrels, raw results, analysis scripts, seeds, checksums, and a one-command reproduction path. Record the exact Gemini model identifier and service date. State which stages can be reproduced without new paid or nondeterministic API calls.

11. **Strengthen benchmark-method positioning and add a real Discussion section.**

    - Related Work is broad but reads partly as a list of recent RAG applications. It gives insufficient attention to foundational IR benchmark construction, TREC pooling, BEIR, the original MTEB work, and reusable evaluation-tool comparisons.
    - Results currently carry most of the interpretation, while the Conclusion repeats several findings. A separate Discussion should compare the findings with prior multilingual retrieval evidence, explain unexpected results, distinguish methodological and empirical contributions, and discuss transfer limits.
    - **Required revision:** add the missing benchmark-method literature, include a concise comparison table of related systems and capabilities, and move cross-study interpretation into a dedicated Discussion.

## Minor Revision Reasons

1. **Calibrate the strongest front-matter claims.** The Abstract says language rather than domain “dominates difficulty” and that the workflow supports uncertainty-aware model selection. Until the confounding, qrels validation, and statistical issues are addressed, use “the two Turkish case-study corpora produced similar rankings” and “supports preliminary screening” rather than explanatory or decision-grade wording.

2. **Use “English-oriented” consistently instead of alternating with “monolingual.”** The paper itself notes that the English-trained models are not strictly monolingual. The shorter label should not imply a tokenizer or training-data property that was not verified.

3. **Define every metric precisely.** State the exact AP@10 denominator, treatment of relevant documents beyond the cutoff, handling of queries without positives, and whether `Success@10` is identical to the evaluator’s `Accuracy@10`. A compact equation or referenced definition would improve reproducibility.

4. **Clarify aggregation rules.** Define whether mean MAP is a macro-average over datasets or a pooled query average, how average rank is calculated, and how weighted latency is weighted. Because each dataset currently has 50 generated queries but only 48–50 scored queries, the choice matters.

5. **Relabel the dataset statistics table.** The “Qrels” column contains positive judgments only, whereas the text also discusses thousands of stored negative judgments. Rename it “Positive qrels” and add total judged pairs or direct readers to a judgment-distribution table.

6. **Expose model identities more often.** M1–M5 make dense tables readable, but key figures and standalone passages should include short model names or a clear cross-reference to the roster so readers do not have to search backward.

7. **Reduce redundant figures and tables.** Several per-dataset metric-profile figures repeat the adjacent numerical tables, and multiple conceptual workflow diagrams convey closely related sequences. Retain figures that reveal a pattern unavailable from the table and move secondary automated-report examples to supplementary material.

8. **Deepen the qualitative error analysis.** The current subsection gives one English positive/negative example and briefly summarizes Turkish questions, but it does not show model-specific retrieval failures, judge disagreements, or difficult false positives. Add comparable examples for every dataset and connect them to the quantitative findings.

9. **Use an unambiguous provenance date.** Replace `01/01/2026` with ISO format (`2026-01-01`) or a written date to avoid day/month ambiguity.

10. **Document dataset redistribution rights.** State the source licenses or permissions, whether extracted text can legally be redistributed, and any terms affecting reproducibility. If full documents cannot be redistributed, provide acquisition scripts and checksums.

11. **Audit bibliography accuracy and relevance.** Correct the foundational RAG citation metadata, verify incomplete or preprint-style entries, and reconsider references whose topics do not directly support embedding retrieval claims. Add primary citations for BEIR, MTEB, and classical pooling rather than relying mainly on recent application papers and websites.

12. **Separate evidence from promotional wording.** Phrases such as “decisively,” “straightforward,” “actionable,” and “sufficient to choose a model” should be reserved for validated findings. Prefer neutral descriptions of what the snapshot shows.

13. **State the intended article type and target audience.** The acceptance bar differs for a research article, software article, benchmark paper, and practitioner case study. The current paper mixes all four identities, which makes the novelty claim difficult to evaluate.

14. **Check journal-specific front-matter limits before submission.** The abstract is dense, the keyword list contains eight items, and some journals limit highlights by length or count. CAS compliance alone does not guarantee compliance with the selected journal’s guide for authors.

## Prioritized Strengthening Checklist

1. **Validate the benchmark evidence:** complete a stratified human audit of queries and qrels, report agreement and errors, and disclose zero-positive queries.
2. **Correct the retrieval setup:** rerun with normalized cosine/model-recommended similarity and document ranking stability.
3. **Fix the empirical claims:** expand to a matched/multi-corpus language–domain design or recast RQ2/RQ3 as descriptive case observations.
4. **Repair the statistical analysis:** use the true 148-query denominator, hierarchical/cluster-aware uncertainty, valid paired tests, and multiplicity control.
5. **Replace the all-metric consistency statistics:** use metric-specific or normalized/rank-based stability measures.
6. **Demonstrate comparative value:** add BM25, hybrid, and stronger current embedding baselines; compare the workflow with established benchmark tooling.
7. **Run sensitivity analyses:** vary similarity, chunking, query count, pool depth, and retrieval cutoff.
8. **Make timing and reproduction durable:** repeat timing trials and archive an exact tagged/DOI-backed experimental package.
9. **Rewrite for internal consistency:** align the Abstract, RQs, Results, Discussion, Conclusion, and limitations with the evidence actually supported.
10. **Complete final presentation checks:** audit references and licenses, reduce redundant artifacts, compile the final CAS PDF, and inspect the rendered paper before submission.

