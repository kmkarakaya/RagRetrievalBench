# Per-Corpus Embedding-Model Selection: Manuscript Revision TODO

## Scope and Fixed Boundaries

This checklist is only for repositioning and strengthening the submitted paper:

- `journal_paper/manuscript.tex`
- `journal_paper/intro.tex`
- `journal_paper/related.tex`
- `journal_paper/method.tex`
- `journal_paper/experiments.tex`
- `journal_paper/results.tex`
- `journal_paper/conclusion.tex`
- a new flat `journal_paper/discussion.tex`
- `journal_paper/refs.bib`

The pipeline, implementation, candidate roster, datasets, qrels, experimental protocol, frozen results, and generated artifacts are complete and will not be changed. This TODO must not request:

- pipeline or configuration changes;
- new models, lexical/hybrid baselines, or rerankers;
- new queries, qrels, annotations, or human audits;
- retrieval, sensitivity, timing, or memory reruns;
- Pareto analysis, hard-constraint filtering, or new report outputs; or
- runtime-memory claims that the completed experiment did not measure.

The purpose of the revision is to make the paper's real research motivation unmistakable while reporting the completed study honestly.

## Central Research Position

Use this argument consistently from the Abstract through the Conclusion:

> A practitioner should not assume that one embedding model will be optimal for every corpus under their control. The completed pipeline evaluates the same candidate roster separately on each local corpus and reports corpus-specific retrieval-quality and operational evidence. The practitioner can therefore select different models for different corpora and priorities instead of transferring one generic or aggregate winner to every collection.

The defensible claim is **“no universally best embedding model should be assumed.”** Do not claim that the three-corpus study proves that no universal best model exists.

The reported observations demonstrate the intended use:

- `M1` is the highest-`MAP@10` and lowest-latency candidate for `education_eng`.
- `M5` is the highest-quality candidate for `education_tr` and `law_tr`.
- `M3` is a lower-latency Turkish compromise when quality is not the only priority.
- The appropriate choice can therefore vary by corpus and by quality-first versus latency-first requirements.

The dataset-level report is the primary decision artifact. The aggregate report is a secondary comparison showing cross-corpus behavior; it must not be presented as a requirement to deploy one model across every corpus.

## Role of Language and Domain

Language and domain remain important because they help practitioners decide which corpora or corpus subsets should be benchmarked separately. They are not removed from the motivation, RQs, results, or implications.

The paper must distinguish these two statements:

- **Supported:** the English and Turkish education demonstrations produce different model-family rankings, while the two Turkish demonstrations produce similar leading rankings.
- **Not supported:** language alone caused the first pattern, domain alone caused the second pattern, or language is generally more important than domain.

The practical lesson is not “language dominates domain.” It is:

> Corpus characteristics can change or preserve the recommended model in ways that should be measured rather than assumed. A practitioner managing heterogeneous corpora can run the same pipeline separately and make corpus-specific choices.

## Claim and Terminology Rules

- [x] Replace unqualified “best model” with “best-performing candidate for this corpus, evaluated roster, fixed protocol, metric, and operational priority.”
- [x] Replace “universal winner” conclusions with “corpus-specific recommendation” or “snapshot-specific aggregate ranking.”
- [x] Replace “actionable evidence,” “decision-grade,” and “sufficient to choose” with “decision-support evidence,” “preliminary screening,” or “supports a corpus-specific shortlist.”
- [x] Remove “language dominates difficulty,” “language dominates domain,” and equivalent explanatory claims.
- [x] Use “language-associated comparison” and “domain-associated comparison” for the current cases.
- [x] Use “English-oriented,” not “monolingual,” unless a primary model source verifies the stronger label.
- [x] Limit operational claims to the measurements actually reported: retrieval metrics, combined corpus embedding/insertion throughput, and combined query embedding/vector-search latency.
- [x] Mention runtime memory only as an unmeasured practitioner consideration or future extension; do not present it as an evaluated pipeline output.
- [x] State that all recommendations are conditional on the completed raw-L2 configuration, synthetic queries, LLM judgments, five-model roster, three corpora, and single CPU environment.

## Preserve the Four Research Questions

Do not delete, merge, renumber, or broadly rewrite the four RQs. Make only the following selective edits.

- [x] **RQ1 — Pipeline utility**
  - Change only “on a local document collection” to “on each local document collection.”
  - Preserve the existing retrieval-quality, operational-cost, and query-level-uncertainty elements.
  - Interpret the answer through the three separate dataset reports, not merely through the aggregate report.

- [x] **RQ2 — Language sensitivity**
  - Preserve the existing RQ wording and theme.
  - Clarify immediately afterward that it is answered through a bounded comparison of the English and Turkish education corpora, not a causal language experiment.

- [x] **RQ3 — Domain sensitivity**
  - Minimally replace “domain-conditioned ranking changes” with “domain-associated ranking differences or stability.”
  - Keep the domain-sensitivity theme and number.
  - Treat the preserved Turkish ranking as a valid answer rather than a failed expected result.

- [x] **RQ4 — Operational decision support**
  - Preserve the existing wording and theme.
  - Define “operational cost” using only the reported embedding/insertion throughput and query latency.
  - Do not add memory, model-size, Pareto, or constraint-filtering claims.

## Section-by-Section Repositioning

### [x] Title, Abstract, Highlights, and Keywords — `manuscript.tex`

- Preserve the current title unless a final consistency audit finds a conflict; it already emphasizes corpus-specific selection.
- Open the Abstract with the practitioner problem: one organization may control several corpora, and the suitable embedding model may differ across them.
- Present the pipeline as an automated, repeatable way to build one benchmark report per corpus.
- Use the concrete per-corpus outcomes (`M1` for English quality/latency; `M5` for Turkish quality; `M3` as a Turkish latency compromise).
- Make aggregate `M5` performance secondary.
- Replace “language rather than domain dominates difficulty” with the observed difference-versus-stability wording.
- Retain the limitations of synthetic queries, LLM qrels, raw L2, and the bounded roster.
- Ensure highlights emphasize per-corpus evaluation, different possible selections, shared-protocol comparability, and auditable reports.

### [x] Introduction and Contributions — `intro.tex`

- Reorder the motivation:
  1. practitioners often manage multiple heterogeneous corpora;
  2. generic leaderboards or one previous local result cannot determine every corpus's suitable model;
  3. evaluating candidates independently on each corpus is costly and inconsistent when done manually;
  4. the completed pipeline automates the shared-protocol comparison and reporting process.
- Replace the current component-list emphasis with the decision problem solved by those components.
- State that language, domain vocabulary, document structure, and operational priorities motivate separate corpus runs.
- Present the four contributions as:
  1. a repeatable per-corpus benchmark-construction workflow;
  2. shared-protocol candidate comparison on each corpus;
  3. dataset-level and secondary aggregate reporting of retrieval quality and measured operational behavior;
  4. preserved benchmark artifacts for inspection and report regeneration.
- Apply only the selective RQ edits above.
- Redefine pipeline utility as producing comparable corpus-specific evidence, not proving that the software improves human decisions.

### [x] Related Work and Positioning — `related.tex`

- Identify the contribution as integration and automation for local per-corpus selection, not a new IR metric, embedding model, or ranking algorithm.
- Compare the paper conceptually with BEIR/MTEB-style benchmarks, TREC pooling, RAG evaluation frameworks, and ad hoc local scripts.
- Emphasize the gap the completed pipeline addresses: turning a practitioner's own corpus into reusable queries, pooled judgments, comparable model results, timing summaries, and a dataset-level report under one workflow.
- Reduce application-paper lists that do not support this positioning.
- State that the evaluation roster and fixed protocol demonstrate the method rather than exhaust current retrieval alternatives.

### [x] Method — `method.tex`

- Preserve the implemented stage sequence exactly.
- Strengthen the explanation that every corpus is processed in isolation and receives separate queries, qrels, indexes, results, and reports.
- State that a practitioner with multiple corpora repeats the same completed workflow for each corpus.
- Explain that the per-corpus report supports corpus-specific selection; the aggregate report is optional comparative context.
- Do not add eligibility filtering, Pareto selection, memory profiling, or any unimplemented decision stage.
- Keep language/domain partitioning as a practitioner choice when a larger collection is heterogeneous.

### [x] Experiments — `experiments.tex`

- Present the three datasets as demonstrations selected to create meaningful corpus variation, not as a design that isolates language or domain effects.
- Explain that the same five-model roster and fixed protocol were applied independently to all three corpora to demonstrate comparable per-corpus selection.
- Preserve the completed setup and results without requesting reruns.
- Correct the query-accounting prose: 150 queries were generated, while the statistical scoring uses 148 positive-bearing queries (48/50/50).
- Explicitly scope the operational measurements as combined, single-run, same-machine evidence:
  - embedding throughput includes corpus embedding plus index insertion;
  - query latency includes query embedding plus vector search.
- State that runtime memory was not measured.
- Present model popularity as one pragmatic roster-construction choice, not evidence that the roster is comprehensive.

### [x] Results — `results.tex`

- Replace “Cross-Dataset Headline Findings” with “Corpus-Specific Selection Outcomes.”
- Lead with a compact corpus-to-recommendation interpretation:
  - `education_eng`: `M1` for both highest `MAP@10` and lowest latency;
  - `education_tr`: `M5` quality-first, `M3` lower-latency compromise;
  - `law_tr`: `M5` quality-first, `M3` lower-latency compromise.
- Explain that the different English/Turkish selections demonstrate why one model should not be assumed for all corpora.
- Explain that the same Turkish shortlist demonstrates that local evaluation can also confirm transfer or stability.
- Move aggregate mean ranking after the per-corpus outcomes and label it secondary.
- Rename:
  - “Language Effect” → “Language-Associated Comparison of the Education Corpora”
  - “Domain Effect Within Turkish” → “Domain-Associated Comparison of the Turkish Corpora”
- Remove all-metric CV, worst-drop, score-range, and “consistency penalty” columns and claims; retain only existing interpretable aggregate columns such as average rank, mean `MAP@10`, and wins.
- Remove bootstrap p-values, “significant,” “separated,” and equivalent inferential claims; retain confidence intervals as descriptive, snapshot-conditional uncertainty.
- Correct every “150 queries” statistical caption to “148 scored queries,” while separately retaining “150 generated queries.”
- Narrow candidate-pool language from “not an artifact” and “decisively confirmed” to “the ordering was stable across the two tested pool constructions.”
- Keep timing interpretations conditional on the compound, single-machine measurements.
- Add a prose-only worked practitioner scenario using the existing results; do not invent a new algorithm or output.

### [x] Discussion — new `discussion.tex`

- Add a top-level Discussion after Results with four subsections:
  1. **Practitioner implications:** different corpora under one organization may justify different embedding models.
  2. **Language- and domain-aware corpus partitioning:** these characteristics motivate separate evaluation but are not isolated causes in the current design.
  3. **Contribution relative to prior workflows:** value lies in automated local benchmark construction, shared-protocol execution, and reporting.
  4. **Validity and transfer limits:** synthetic evidence, no human validation, raw L2, bounded roster, fixed parameters, incomplete pool, and single-machine timing.
- Explain that `M1`/`M5`/`M3` recommendations illustrate how to read the reports, not permanent deployment prescriptions.
- State explicitly that aggregate `M5` performance does not override corpus-specific choices.

### [x] Conclusion and Limitations — `conclusion.tex`

- Lead with the completed pipeline's per-corpus selection purpose.
- Answer RQ1 using the separate corpus reports.
- Answer RQ2 with the observed English/Turkish ranking difference, bounded to the two education corpora.
- Answer RQ3 with the observed Turkish-domain stability, bounded to the two Turkish corpora.
- Answer RQ4 using only retrieval quality, embedding/insertion throughput, query latency, and descriptive uncertainty.
- Remove universal-winner, significance, “language dominates,” and deployment-guarantee wording.
- Conclude that practitioners should benchmark each materially distinct corpus rather than transfer one generic or aggregate winner automatically.
- Keep unavailable validation, alternative geometry, stronger baselines, parameter sensitivity, repeated timing, immutable archiving, and memory measurement as explicit limitations or future work—not completed capabilities.

## Reviewer Comment Mapping

Every entry below is a manuscript response using the frozen evidence. “Residual risk” means wording can reduce overclaiming but cannot fully satisfy a reviewer who requires new experiments.

## Reject-Level Comments

### [x] R1 — Language/domain conclusions are confounded

- **Paper locations:** Abstract, Introduction, Experiments, Results comparison subsections, Discussion, Conclusion.
- **Content action:** Reposition language/domain as reasons for separate corpus evaluation; report the observed difference and stability without causal attribution.
- **Evidence boundary:** One corpus per condition cannot isolate language or domain.
- **Completion criterion:** Language and domain remain prominent, but “effect,” “dominates,” and causal explanations are absent.
- **Residual risk:** Reduced substantially through correct framing.

### [x] R2 — Synthetic queries and LLM qrels lack human validation

- **Paper locations:** Abstract, Method, Experiments, Results, Discussion, Limitations.
- **Content action:** Describe the completed output as automated preliminary screening and decision support; clearly separate query generation from relevance judging; remove “validated,” “reliable,” “actionable,” and “sufficient.”
- **Evidence boundary:** No human audit or human–LLM agreement is available.
- **Completion criterion:** Every quality/ranking claim is explicitly conditional on synthetic queries and LLM judgments.
- **Residual risk:** High; wording cannot replace independent validation.

### [x] R3 — Novelty and utility are not demonstrated

- **Paper locations:** Introduction, Related Work, Method, Results worked scenario, Discussion.
- **Content action:** Define the contribution as integrated automation for per-corpus selection; add a conceptual capability comparison and demonstrate use through the existing three report outcomes.
- **Evidence boundary:** No user study, setup-effort comparison, or independent-practitioner evaluation exists.
- **Completion criterion:** The paper claims demonstrated workflow capability, not improved human decision quality or algorithmic novelty.
- **Residual risk:** Moderate; repositioning strengthens identity but does not create comparative user evidence.

## Major Revision Comments

### [x] M1 — Raw non-normalized L2 retrieval geometry

- **Paper locations:** Experiments, Results, Discussion, Conclusion.
- **Content action:** State the exact geometry prominently; remove any cosine-equivalence claim; qualify all rankings as conditional on raw L2.
- **Evidence boundary:** No cosine/model-recommended-similarity rerun will be added.
- **Completion criterion:** No conclusion generalizes the ordering beyond the completed retrieval configuration.
- **Residual risk:** High; wording cannot establish geometry robustness.

### [x] M2 — 150 generated versus 148 scored queries

- **Paper locations:** Experiments query-accounting table; statistical Results prose/tables/figures; Conclusion.
- **Content action:** Distinguish generated, positive-bearing, excluded, and scored counts; state 48/50/50 scored queries and explain zero-positive exclusion.
- **Evidence boundary:** Use the existing frozen query-level artifact.
- **Completion criterion:** All statistical denominators say 148; corpus workload descriptions may correctly say 150 generated.
- **Residual risk:** Low after correction.

### [x] M3 — Bootstrap p-values, multiplicity, and clustering

- **Paper locations:** Statistical Results subsection, Abstract, Discussion, Conclusion.
- **Content action:** Remove p-values and significance language; retain confidence intervals as descriptive snapshot uncertainty; discuss query/document/dataset dependence.
- **Evidence boundary:** No new randomization, multiplicity-adjusted, hierarchical, or cluster-aware analysis.
- **Completion criterion:** The paper makes no population-inference or formal-significance claim.
- **Residual risk:** Moderate because the remaining intervals still reflect the completed analysis design.

### [x] M4 — Invalid all-metric consistency diagnostics

- **Paper locations:** Introduction definitions, aggregate Results table/prose, Conclusion.
- **Content action:** Remove cross-metric CV, worst drop, score range, and consistency-penalty interpretation.
- **Evidence boundary:** Do not introduce a replacement composite statistic.
- **Completion criterion:** Only directly interpretable existing metrics/ranks remain.
- **Residual risk:** Low after removal.

### [x] M5 — RQ3 conflicts with domain stability

- **Paper locations:** RQ3, domain comparison, Discussion, Conclusion.
- **Content action:** Ask about differences or stability and answer with the preserved Turkish ranking.
- **Evidence boundary:** Stability is case-specific and does not show that domain is irrelevant.
- **Completion criterion:** RQ3 and its answer agree without changing the RQ's domain-sensitivity theme.
- **Residual risk:** Low after reframing.

### [x] M6 — Weak baselines and bounded model roster

- **Paper locations:** Related Work, Experiments roster rationale, Discussion, Limitations.
- **Content action:** Present the five models as a practical demonstration roster; remove “sufficient” and comprehensive-baseline wording; explain that selections are only among the evaluated candidates.
- **Evidence boundary:** No lexical, hybrid, reranking, domain-adapted, or newer multilingual baseline will be added.
- **Completion criterion:** The paper never implies that the roster represents all available embedding/retrieval options.
- **Residual risk:** High; roster expansion is not replaceable by prose.

### [x] M7 — No protocol sensitivity analysis

- **Paper locations:** Experiments, Results, Discussion, Limitations, Future Work.
- **Content action:** Call the study a fixed-protocol demonstration; condition recommendations on chunking, query count, pool depth, raw L2, and `k=10`; remove robustness-to-defaults implications.
- **Evidence boundary:** No sensitivity reruns will be added.
- **Completion criterion:** Fixed parameters are never described as optimal or recommendation-invariant.
- **Residual risk:** High for a benchmark-method paper.

### [x] M8 — Candidate-pool completeness

- **Paper locations:** Method, Experiments, pool-robustness Results, Discussion.
- **Content action:** Retain the observed positive-yield increase and tested ordering stability; remove completeness, unbiasedness, and general reusability claims.
- **Evidence boundary:** Relevant chunks missed by every evaluated model remain unjudged; qrels are roster-conditional.
- **Completion criterion:** The paper says only that the ordering survived the two tested constructions.
- **Residual risk:** Moderate to high without residual judging or external retrievers.

### [x] M9 — Timing reproducibility

- **Paper locations:** Experiments timing scope, Results timing tables, Discussion, Limitations.
- **Content action:** Describe timing as compound, single-run, single-machine, relative evidence; remove hardware-independent or statistically stable implications.
- **Evidence boundary:** No repetitions, dispersion, detailed component timing, or additional hardware data.
- **Completion criterion:** Timing supports illustrative quality–speed trade-offs only.
- **Residual risk:** High for operational recommendations.

### [x] M10 — Mutable reproducibility package

- **Paper locations:** Method reproducibility paragraph, Experiments reproducibility table, data/code-availability statement, Discussion.
- **Content action:** Describe exactly what is currently available and distinguish implementation availability from immutable experimental archiving.
- **Evidence boundary:** Do not claim DOI-backed or independently durable reproduction unless such an identifier already exists.
- **Completion criterion:** The paper does not overstate a live repository as a permanent experimental record.
- **Residual risk:** Moderate to high if no immutable release exists.

### [x] M11 — Benchmark positioning and missing Discussion

- **Paper locations:** Related Work, new Discussion, Conclusion.
- **Content action:** Add foundational benchmark/pooling positioning, a concise capability comparison, and the four-part Discussion specified above.
- **Evidence boundary:** Compare documented capabilities without implying an empirical head-to-head evaluation.
- **Completion criterion:** Methodological contribution, empirical demonstration, practitioner implication, and validity limits are clearly separated.
- **Residual risk:** Low to moderate after a strong rewrite.

## Minor Revision Comments

### [x] MIN1 — Recalibrate Abstract and highlights

- **Action:** Center per-corpus selection, report conditional outcomes, remove “language dominates,” and describe automated preliminary screening.
- **Completion criterion:** Aggregate `M5` is secondary and no decision-grade claim remains.

### [x] MIN2 — Standardize “English-oriented”

- **Action:** Replace reader-facing “monolingual” with “English-oriented.”
- **Completion criterion:** Terminology is consistent across every TeX section and caption.

### [x] MIN3 — Define retrieval metrics

- **Action:** Add concise definitions for MAP@10, Recall@10, Precision@10, NDCG@10, MRR@10, and Success@10, including zero-positive handling.
- **Completion criterion:** A reader can interpret each reported value without inspecting code.

### [x] MIN4 — Clarify aggregation rules

- **Action:** Define dataset macro means, average rank, aggregate mean `MAP@10`, and weighted query latency using the existing calculation.
- **Completion criterion:** Every aggregate column has an explicit interpretation.

### [x] MIN5 — Relabel qrels counts

- **Action:** Rename “Qrels” to “Positive qrels” and state total judged positive/negative pairs in prose or a note.
- **Completion criterion:** Positive labels are not confused with all judgments.

### [x] MIN6 — Expose model identities

- **Action:** Add short model names alongside `M1`–`M5` in standalone tables, figures, or captions.
- **Completion criterion:** A reader can understand each central result without searching backward.

### [x] MIN7 — Reduce redundant visuals

- **Action:** Retain visuals that support per-corpus decisions or cross-corpus patterns; remove or relocate repetitive auto-generated metric profiles.
- **Completion criterion:** Each retained figure adds information not already clear from an adjacent table.

### [x] MIN8 — Calibrate qualitative examples

- **Action:** Use existing examples to illustrate corpus-grounded queries and near misses; do not claim unreported model-specific error frequencies or human judge disagreement.
- **Completion criterion:** Qualitative prose stays within the available artifacts.

### [x] MIN9 — Use ISO provenance dates

- **Action:** Replace `01/01/2026` with `2026-01-01`.
- **Completion criterion:** No ambiguous numeric date remains.

### [x] MIN10 — State dataset redistribution limits

- **Action:** Report known source ownership, retrieval provenance, and any verified redistribution limitations; do not invent licenses or permissions.
- **Completion criterion:** Data availability is accurate about what can and cannot be redistributed.

### [x] MIN11 — Audit bibliography

- **Action:** Correct foundational RAG metadata, verify cited entries, add primary BEIR/MTEB/pooling sources where used, and remove references that do not support the revised positioning.
- **Completion criterion:** Every citation supports the nearby claim and resolves in `refs.bib`.

### [x] MIN12 — Remove promotional wording

- **Action:** Replace “decisively,” “straightforward,” “actionable,” “sufficient,” “reliable,” “dominant,” and similar terms with neutral conditional descriptions.
- **Completion criterion:** Conclusions describe only measured behavior.

### [x] MIN13 — State article identity

- **Action:** Consistently identify the work as a practitioner-facing benchmark-method/tool paper demonstrated on three corpora.
- **Completion criterion:** The paper does not alternate among algorithm, universal benchmark, software report, and causal language/domain study identities.

### [ ] MIN14 — Check target-journal front matter

- **Action:** After journal selection, check abstract length, highlights, keywords, declarations, and data/code-statement requirements.
- **Completion criterion:** The final front matter satisfies both CAS and the selected journal's guide.

## Revision Order

### P0 — Lock the paper's argument and claim boundaries

- [x] Apply the central research position and language/domain role.
- [x] Preserve the four RQs with only the specified selective edits.
- [x] Remove unsupported causal, universal-winner, memory, Pareto, and decision-grade claims.
- [x] Correct the 150-generated/148-scored distinction.
- [x] Remove bootstrap p-values/significance and invalid all-metric consistency claims.

### P1 — Reorganize the paper around existing per-corpus evidence

- [x] Revise in this order: Method → Experiments → Results → Discussion → Related Work → Introduction → Abstract/highlights → Conclusion.
- [x] Make dataset-level outcomes primary and aggregate results secondary.
- [x] Add the existing-results practitioner scenario without introducing new calculations.
- [x] Add explicit evidence boundaries and residual risks.

### P2 — Presentation and submission checks

- [ ] Complete MIN2–MIN14.
- [x] Check all table/figure captions, labels, prose references, citation keys, and terminology.
- [x] Verify that no revised text implies a pipeline or experiment that was not actually implemented.

## Final Acceptance Gates

- [x] `todo.md` contains exactly 3 reject, 11 major, and 14 minor reviewer mappings.
- [x] No task requests code, configuration, pipeline, candidate-roster, qrels, annotation, rerun, timing-instrumentation, memory, or new-output changes.
- [x] RQ1–RQ4 remain numbered and recognizable; only RQ1 and RQ3 receive the specified minimal edits.
- [x] The primary narrative supports separate model choices for separate corpora controlled by one practitioner.
- [x] The worked interpretation uses only existing evidence: `M1` for `education_eng`; `M5` quality-first and `M3` lower-latency for the Turkish corpora.
- [x] Aggregate `M5` is presented as secondary cross-corpus context, not a universal deployment choice.
- [x] Language and domain remain important benchmark-partitioning and interpretation dimensions without causal claims.
- [x] No current-capability claim mentions runtime memory, Pareto analysis, hard constraints, or unimplemented selection stages.
- [x] Every unresolved methodological objection is explicitly labeled as a residual risk rather than falsely “resolved” through wording.
- [x] Only after the later TeX revision is complete, run:

  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1 -CompilePdf
  ```

- [x] Confirm 0 CAS lint errors, successful PDF compilation, resolved references, and readable tables/figures.
