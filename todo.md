# Practitioner-First Manuscript Revision TODO

## Scope

This checklist is exclusively for strengthening the submitted paper:

- `journal_paper/manuscript.tex`
- `journal_paper/intro.tex`
- `journal_paper/related.tex`
- `journal_paper/method.tex`
- `journal_paper/experiments.tex`
- `journal_paper/results.tex`
- `journal_paper/conclusion.tex`
- a new flat `journal_paper/discussion.tex`, if added
- `journal_paper/refs.bib`

Experimental and validation work appears below only when new evidence is necessary to support revised paper content. Do not edit the TeX files until the corresponding evidence-changing tasks are complete.

## Non-Negotiable Paper Identity

The paper's central contribution is:

> A configurable local benchmarking pipeline that helps practitioners shortlist suitable embedding models for their own corpus and project requirements by jointly considering retrieval quality, corpus language and domain, embedding/indexing speed, query latency, memory use, model size, uncertainty, and reproducibility.

The paper is a practitioner-facing benchmark-method/tool paper with a demonstration study. It is not:

- a new embedding algorithm;
- a universal embedding leaderboard;
- a causal study that isolates language or domain effects; or
- a claim that one model is best for every RAG deployment.

Language and domain must not be removed. They are important characteristics of the practitioner's corpus and therefore important inputs to benchmark design, corpus partitioning, candidate-roster design, and result interpretation. The bounded demonstrations may show language-associated or domain-associated ranking differences—or stability—but cannot attribute those outcomes solely to language or domain because each condition contains only one corpus.

## What Reframing Can and Cannot Fix

- **Primarily fixable through paper language and argument:** R1, M5, MIN1, MIN2, MIN12, MIN13, and the contribution-drift portions of R3 and M11.
- **Partly fixable through clarification but still needing analysis:** M2, M3, M4, MIN3–MIN5, MIN8, and MIN9–MIN11.
- **Not fixable by wording alone:** R2, the utility-evidence portion of R3, M1, M6–M10, and memory-aware selection. Do not disguise missing evidence with softer adjectives.

## Argument Spine to Apply Throughout the Paper

- [ ] **A1 — Start with the practitioner's decision problem.**
  - Explain that practitioners face a local candidate-selection problem: available embedding models differ in retrieval quality, language coverage, speed, latency, memory footprint, model size, licensing, and deployment compatibility.
  - Explain why generic leaderboards cannot determine the best local choice: the target corpus, information needs, preprocessing, hardware, and hard deployment constraints differ.
  - Present the pipeline as the mechanism for producing a defensible local shortlist under those conditions.

- [ ] **A2 — Define the pipeline's decision sequence in `method.tex`.**
  1. Characterize the target corpus, including language, domain, document structure, and representative information needs.
  2. State candidate eligibility requirements such as license, CPU/GPU compatibility, maximum model size, and maximum memory.
  3. Decide whether heterogeneous language/domain subsets should be evaluated separately.
  4. Construct an auditable local benchmark with queries, pooled candidates, judgments, and explicit validity checks.
  5. Evaluate the same eligible roster under a fixed protocol.
  6. Measure retrieval quality, embedding computation, index insertion, query latency, peak memory, and model size.
  7. Remove candidates that violate hard project constraints.
  8. Identify Pareto-nondominated candidates and select among them using the practitioner's stated priority.

- [ ] **A3 — Make the three datasets demonstrations of this decision process.**
  - Present each dataset as a worked local-selection case.
  - Use the English/Turkish education comparison to show that language-associated corpus differences can alter the shortlist.
  - Use the two Turkish corpora to show that a domain comparison can reveal either change or stability; the observed stability is itself useful because it prevents inventing a domain effect.
  - State that both outcomes reinforce local testing: neither difference nor transfer should be assumed in advance.

- [ ] **A4 — Replace universal winners with conditional recommendations.**
  - Report recommendations in the form: “For this corpus, roster, protocol, hardware, and priority, model X is the quality-first/latency-first/memory-first candidate.”
  - Do not write “best model” without naming the condition and decision criterion.
  - End every aggregate recommendation with its scope: evaluated corpora, evaluated roster, retrieval configuration, qrels process, and hardware.

- [ ] **A5 — Treat memory and model size as central only after measurement.**
  - Add peak CPU RSS for model loading, corpus embedding/indexing, and querying.
  - Add model artifact size, parameter count, embedding dimension, and license to the roster evidence.
  - Do not claim memory-aware or resource-aware selection until these values appear in Experiments and Results.
  - Do not make GPU-memory claims for a CPU-only study.

## Preserve and Recalibrate the Four Research Questions

Do not delete, merge, renumber, or replace the four RQ themes. Revise only enough to align them with the practitioner-selection goal and the available design.

- [ ] **RQ1 — Pipeline utility**
  - Proposed wording: “Can the pipeline produce a reproducible, corpus-specific shortlist of embedding models with retrieval-quality, operational-cost, resource, and uncertainty evidence for a practitioner's local collection?”
  - Preserve the existing pipeline-utility theme.
  - Do not define utility merely as “the software produced a report.” Demonstrate utility through an actual constraint-to-shortlist decision.

- [ ] **RQ2 — Language sensitivity**
  - Proposed wording: “Under a fixed benchmark protocol, how do model rankings and quality–resource trade-offs differ between the English and Turkish education demonstration corpora, and what does this imply for language-aware local shortlisting?”
  - Preserve language as an important selection factor.
  - Describe a bounded comparison between two corpora, not an isolated causal language effect.

- [ ] **RQ3 — Domain sensitivity**
  - Proposed wording: “Under a fixed benchmark protocol, how do model rankings and quality–resource trade-offs differ or remain stable between the Turkish education and law/regulation demonstration corpora, and what does this imply for domain-aware local shortlisting?”
  - Preserve domain as an important selection factor.
  - Make ranking difference and ranking stability equally valid answers.

- [ ] **RQ4 — Operational decision support**
  - Proposed wording: “How do retrieval effectiveness, embedding/indexing speed, query latency, peak memory, model size, and uncertainty alter the recommended shortlist under different project priorities and hard constraints?”
  - Preserve the operational decision-support theme while adding the resource dimensions required by the paper's actual goal.

## Section-Level Rewrite Map

- [ ] **`manuscript.tex`: title, Abstract, highlights, keywords**
  - Keep the title practitioner- and selection-oriented; consider adding “practitioner-oriented” or “constraint-aware” only if the final evidence supports those words.
  - Lead the Abstract with the local selection problem and pipeline decision output.
  - Describe the datasets as three demonstrations, not language/domain experiments.
  - Report conditional shortlist outcomes rather than a universal aggregate winner.
  - Remove “language rather than domain dominates difficulty.”
  - Mention memory only if A5 is completed.

- [ ] **`intro.tex`: motivation, gap, contributions, RQs**
  - Reorder the motivation as: local decision problem → inadequacy of generic rankings/ad hoc trials → required evidence → proposed pipeline.
  - Replace the current component-list contribution with the pipeline's decision logic and artifact contract.
  - Explain language and domain as corpus characteristics that may require separate subset evaluation.
  - Replace “sufficient to choose a model” with “supports a shortlist and an evidence-based selection subject to deployment validation.”
  - Insert the minimally recalibrated RQ1–RQ4 wording above.

- [ ] **`related.tex`: journal-level positioning**
  - Compare the proposed pipeline with BEIR/MTEB-style evaluation, TREC pooling, RAG evaluation frameworks, and simpler local evaluation workflows.
  - Focus the gap on integration for local decision support: corpus-specific benchmark construction, auditable pooled qrels, operational/resource profiling, constraint filtering, Pareto shortlisting, and reproducible artifacts.
  - Reduce unrelated application examples that do not support this gap.
  - State precisely which components are established and what their integration contributes.

- [ ] **`method.tex`: selection method, not only data processing**
  - Retain the staged benchmark-construction workflow.
  - Add the complete practitioner decision sequence from A2 after reporting.
  - Define hard constraints, eligibility filtering, Pareto dominance, and priority-based final selection.
  - Explain when language/domain subsets should be benchmarked separately.
  - Separate query-generator validity from relevance-judge validity and add the human-audit step to the method.
  - Define the intended primary similarity configuration and all reported measurements.

- [ ] **`experiments.tex`: demonstrate how a practitioner configures the pipeline**
  - Explain why the three corpora and final model/baseline roster are useful demonstrations.
  - Report dataset provenance, licenses, structural differences, generated/scored query counts, qrels counts, and audit design.
  - Report model eligibility attributes: language coverage, license, size, dimension, parameters, device compatibility, and memory.
  - Report the final retrieval geometry, baselines, sensitivity settings, repeated timing protocol, and hardware.
  - Avoid claiming that fixed settings isolate language or domain.

- [ ] **`results.tex`: organize results around shortlist decisions**
  - Replace “Cross-Dataset Headline Findings” with a practitioner-shortlist overview.
  - Present per-corpus quality, operational/resource evidence, eligible models, and Pareto shortlist.
  - Rename “Language Effect” and “Domain Effect Within Turkish” as descriptive corpus-comparison subsections.
  - Remove invalid all-metric consistency results and unsupported significance language.
  - Add human-audit, sensitivity, pool-coverage, and repeated-timing findings.
  - End each RQ subsection with a direct, bounded answer.

- [ ] **new `discussion.tex`: explain implications without repeating Results**
  - Add a top-level Discussion after Results.
  - Discuss why local corpus evidence changes—or sometimes preserves—the shortlist.
  - Explain how language and domain should influence corpus partitioning and candidate selection without causal overreach.
  - Compare the pipeline with existing benchmark approaches.
  - Separate practitioner implications, methodological contribution, validity threats, and transfer limits.

- [ ] **`conclusion.tex`: answer the four RQs conditionally**
  - Lead with the practitioner selection pipeline, not M5's aggregate performance.
  - Give one bounded answer for each RQ.
  - Remove bootstrap p-value claims, “language dominates,” “actionable” without validation, and universal model recommendations.
  - State that the three datasets demonstrate how the pipeline is used; they do not estimate population language/domain effects.

## Reject-Level Comments

### [ ] R1 — Language/domain conclusions are confounded

- **Resolution type:** Manuscript reframing; no deletion of language/domain or RQ2/RQ3.
- **Paper locations:** Abstract; `intro.tex`; dataset design in `experiments.tex`; language/domain subsections in `results.tex`; `discussion.tex`; `conclusion.tex`.
- **Actions:**
  - Remove “language effect,” “domain effect,” “language dominates difficulty,” and causal variants from headings and claims.
  - Rename the subsections to “Language-Associated Comparison of the Education Corpora” and “Domain-Associated Comparison of the Turkish Corpora.”
  - Preserve the observed ranking differences across the education corpora and the observed stability across the Turkish corpora.
  - Explain that corpus identity also includes source selection, structure, scale, queries, and qrels, so language/domain are plausible selection factors but not isolated causes.
  - Make the practitioner implication explicit: represent important language/domain subsets in the local benchmark instead of assuming either difference or transfer.
- **Done when:** Language and domain remain prominent in model selection, but no sentence claims that this three-corpus design identifies their independent effects.

### [ ] R2 — Synthetic queries and LLM judgments lack human validation

- **Resolution type:** New evidence plus manuscript revision; wording alone is insufficient.
- **Paper locations:** query/qrels method in `method.tex`; audit protocol in `experiments.tex`; audit results and errors in `results.tex`; validity discussion in `discussion.tex` and `conclusion.tex`.
- **Actions:**
  - Audit 15 generated queries per dataset for naturalness, answerability, specificity, and seed-copying.
  - Have two language-qualified annotators independently assess at least 50 query–chunk pairs per dataset, balanced across LLM-positive and LLM-negative labels and including difficult negatives.
  - Include zero-positive queries and a residual sample of unpooled chunks.
  - Report raw agreement, Cohen's kappa, adjudicated agreement with the LLM, language-specific results, and representative errors.
  - Until this evidence exists, call the output “automated preliminary screening,” not decision-grade or reliable model selection.
- **Done when:** The paper distinguishes generator quality from judgment quality and calibrates its selection claims to measured human agreement.

### [ ] R3 — Novelty and practitioner utility are not demonstrated

- **Resolution type:** Contribution reframing plus comparative evidence.
- **Paper locations:** `intro.tex`, `related.tex`, `method.tex`, `experiments.tex`, `results.tex`, and `discussion.tex`.
- **Actions:**
  - State that novelty lies in the integrated local decision method and artifact contract, not in individual IR components or a new retrieval algorithm.
  - Add a comparison table against BEIR/MTEB-style tooling, TREC pooling, RAG evaluation frameworks, and a simple local benchmark workflow.
  - Compare local-corpus setup, language/domain partitioning, pooled qrels, human-audit support, operational/resource profiling, hard-constraint filtering, Pareto shortlisting, and reproducible outputs.
  - Add one worked practitioner scenario: corpus characteristics and constraints → eligible candidates → benchmark evidence → Pareto set → quality-first, latency-first, and memory-first choices.
  - Add a deterministic rerun result showing whether fixed inputs reproduce the reported scores and shortlist.
  - If no practitioner/user study is conducted, do not claim that the workflow improves practitioner decision quality; claim only demonstrated decision support.
- **Done when:** A reviewer can identify the method/tool contribution, its difference from credible alternatives, and a concrete decision produced by it.

## Major Revision Comments

### [ ] M1 — Retrieval geometry may distort comparisons

- **Resolution type:** Reanalysis before rewriting.
- **Paper locations:** retrieval method in `method.tex`; configuration in `experiments.tex`; all affected tables/figures in `results.tex`; interpretation in `discussion.tex` and `conclusion.tex`.
- **Actions:**
  - Make normalized cosine the primary common protocol unless model documentation justifies another primary setting.
  - Compare raw L2, normalized L2, cosine, and model-recommended similarity where feasible.
  - Report score changes, per-corpus rank correlations, shortlist/Pareto changes, and any model whose recommendation changes.
  - Remove the claim that L2 and cosine “typically” preserve ordering for non-normalized embeddings.
- **Done when:** Every selection conclusion is based on a defensible primary geometry and its sensitivity is visible.

### [ ] M2 — The paper says 150 queries although 148 are scored

- **Resolution type:** Factual correction and sensitivity clarification.
- **Paper locations:** query-accounting table in `experiments.tex`; statistical prose/captions in `results.tex`; summaries in Abstract and `conclusion.tex`.
- **Actions:**
  - Report per dataset: generated queries, judged queries, positive-bearing queries, zero-positive queries, excluded queries, and scored queries.
  - State the evaluator's zero-positive policy and the estimand it produces.
  - Use 148 only if the final qrels still yield 48/50/50 scored queries; otherwise propagate the final counts everywhere.
  - Add a sensitivity result for a clearly defined alternative zero-positive policy.
- **Done when:** Prose, tables, figures, and captions use one correct denominator and explain exclusions.

### [ ] M3 — Bootstrap p-values and dependence are not defensible

- **Resolution type:** Statistical reanalysis and claim calibration.
- **Paper locations:** statistical protocol in `experiments.tex`; intervals/tests in `results.tex`; statistical claims in Abstract and `conclusion.tex`.
- **Actions:**
  - Make paired confidence intervals the primary uncertainty evidence.
  - Remove the current bootstrap “p-values” and “significant/separated” wording.
  - If p-values are retained, use a valid paired randomization/permutation test and Holm correction.
  - Report dataset-specific effects before any aggregate.
  - Use document-aware resampling where query provenance permits; describe the limits of only three datasets instead of implying population inference.
  - Label aggregate intervals as conditional on the demonstration corpora and qrels.
- **Done when:** The paper distinguishes descriptive uncertainty from population-level inference and respects query/document/dataset structure.

### [ ] M4 — All-metric consistency diagnostics are invalid

- **Resolution type:** Remove and redesign.
- **Paper locations:** definitions in `intro.tex`; aggregate table and prose in `results.tex`; claims in `conclusion.tex`.
- **Actions:**
  - Delete the raw cross-metric CV, worst-drop, score-range, and “smallest consistency penalty” claims.
  - Do not combine MAP, recall, precision, NDCG, MRR, and success as commensurate observations.
  - Report stability separately for the primary metric, or use within-condition ranks with a justified aggregation rule.
  - Replace the consistency table with a decision table covering quality, throughput, latency, memory, model size, eligibility, and Pareto status.
- **Done when:** No headline statistic is driven by mixing incompatible metric scales.

### [ ] M5 — RQ3 does not match the observed domain result

- **Resolution type:** RQ-preserving reinterpretation.
- **Paper locations:** RQ3 in `intro.tex`; Turkish-domain subsection in `results.tex`; `discussion.tex`; `conclusion.tex`.
- **Actions:**
  - Keep RQ3 and revise it to ask whether rankings differ or remain stable.
  - Answer RQ3 directly: the two Turkish demonstrations preserve the leading order and show small/mixed score changes.
  - Explain that stability is a useful pipeline output but is not evidence that domain never matters.
  - Remove the statement that behavior “changes materially” for the domain comparison.
- **Done when:** RQ3 remains domain-focused and its answer agrees with the actual table.

### [ ] M6 — Baselines and model roster are too weak

- **Resolution type:** Evidence expansion plus roster rationale.
- **Paper locations:** roster selection in `experiments.tex`; baseline and shortlist results in `results.tex`; implications in `discussion.tex`.
- **Actions:**
  - Add BM25 as a lexical baseline.
  - Add one reproducible hybrid BM25+dense configuration.
  - Add at least one competitive contemporary multilingual embedding model, such as BGE-M3 if licensing and CPU feasibility are acceptable.
  - Explain why reranking or a domain-adapted model is included or explicitly outside the embedding-selection scope.
  - Define roster inclusion using language coverage, license, model size, memory, hardware compatibility, and deployment relevance—not download count alone.
  - Keep lexical/hybrid baselines contextually separate from the embedding-model shortlist.
- **Done when:** The paper can show whether dense embedding selection improves on lexical retrieval and how a stronger candidate affects the shortlist.

### [ ] M7 — Fixed protocol choices lack sensitivity analysis

- **Resolution type:** Reanalysis plus bounded interpretation.
- **Paper locations:** sensitivity design in `experiments.tex`; stability results in `results.tex`; implications/limits in `discussion.tex`.
- **Actions:**
  - Compare similarity configurations from M1.
  - Report `k={5,10,20}`.
  - Report query-count stability at 20, 30, 40, and all scored queries using fixed-seed repeated subsampling.
  - Report candidate-pool depths 5, 10, and 20.
  - Add a limited chunking sensitivity analysis using at least two plausible size/overlap alternatives.
  - Report top-model, rank-correlation, eligibility, and Pareto-set stability—not only score changes.
- **Done when:** The paper shows which pipeline defaults preserve or alter the practitioner recommendation.

### [ ] M8 — Candidate-pool robustness remains incomplete

- **Resolution type:** Pool-coverage analysis and claim restriction.
- **Paper locations:** pooling method in `method.tex`; pool design in `experiments.tex`; saturation/residual results in `results.tex`; limits in `discussion.tex`.
- **Actions:**
  - Build the final pool using all evaluated dense models plus lexical/hybrid systems where methodologically appropriate.
  - Report unique pool size, system overlap, cumulative positive yield, and saturation as systems/depth are added.
  - Human-judge a random residual sample of unpooled chunks for audited queries.
  - Replace “not an artifact of pool construction” with the narrower claim that rankings were stable across the tested pool variants.
  - State that qrels support the evaluated roster and may need expansion for future retrievers.
- **Done when:** Pool coverage is measured and the qrels reuse boundary is explicit.

### [ ] M9 — Timing and operational evidence are not reproducible

- **Resolution type:** Repeated measurement and clearer decomposition.
- **Paper locations:** measurement protocol/hardware table in `experiments.tex`; operational tables in `results.tex`; transfer limits in `discussion.tex`.
- **Actions:**
  - Use one discarded warm-up followed by at least five measured runs per model/dataset.
  - Report median and IQR.
  - Separate model load, corpus embedding, index insertion, query embedding, vector search, and combined warm-query latency.
  - Measure peak CPU RSS for loading, indexing, and querying.
  - Record CPU, RAM, cores/threads, storage, OS, device, and thread settings.
  - Define any cross-dataset weighting formula.
- **Done when:** Every operational recommendation has repetitions, dispersion, measurement scope, and hardware context.

### [ ] M10 — Reproducibility evidence is mutable or incomplete

- **Resolution type:** Manuscript reproducibility contract backed by an immutable artifact.
- **Paper locations:** reproducibility method in `method.tex`; exact conditions in `experiments.tex`; data/code-availability statement in `manuscript.tex`.
- **Actions:**
  - State the exact commit/release/DOI that corresponds to the reported paper.
  - List the included environment lockfile, prompts, fixed queries/qrels, pool provenance, raw rankings/results, seeds, checksums, and table/figure generation path.
  - Record exact model revisions and the exact Gemini identifier and service date.
  - Distinguish deterministic reproduction from stages requiring new LLM calls.
  - Give one concise command or command sequence for reproducing the paper's deterministic results.
- **Done when:** The paper points to an immutable, independently executable evidence snapshot rather than a mutable repository URL.

### [ ] M11 — Benchmark positioning is weak and Discussion is missing

- **Resolution type:** Literature/argument revision and new paper section.
- **Paper locations:** `related.tex`, `refs.bib`, new `discussion.tex`, and `manuscript.tex` section inclusion.
- **Actions:**
  - Add primary BEIR, original MTEB, TREC pooling, benchmark-governance, and relevant RAG evaluation citations.
  - Replace the list of application papers with a capability/gap comparison centered on local selection.
  - Create a Discussion with four parts: practitioner implications; relation to prior benchmark methods; validity threats; transferability.
  - Move cross-study interpretation out of Results and repeated findings out of Conclusion.
- **Done when:** The journal contribution and its limits are explicit relative to established evaluation practice.

## Minor Revision Comments

### [ ] MIN1 — Recalibrate Abstract and highlights

- **Paper locations:** `manuscript.tex`.
- **Action:** Lead with corpus- and constraint-specific shortlisting; describe three demonstrations; replace “language dominates” with the observed conditional patterns; use “preliminary screening” until human validation is reported; mention memory only after measurement.

### [ ] MIN2 — Use “English-oriented” consistently

- **Paper locations:** all reader-facing TeX sections.
- **Action:** Remove “monolingual” unless verified by primary model documentation; use “English-oriented” and “multilingual” consistently.

### [ ] MIN3 — Define every retrieval metric

- **Paper locations:** `method.tex` or `experiments.tex`, with concise reminders in `results.tex`.
- **Action:** Define MAP@k, recall@k, precision@k, NDCG@k, MRR@k, and Success@k; specify AP denominator, binary relevance, cutoff behavior, positives beyond `k`, zero-positive handling, and whether Success@k equals evaluator Accuracy@k.

### [ ] MIN4 — Define aggregation and ranking

- **Paper locations:** `method.tex`, `experiments.tex`, and Results captions.
- **Action:** Define per-query and per-dataset macro means, any equal-dataset aggregate, average rank, weighted latency, constraint eligibility, and Pareto directions.

### [ ] MIN5 — Distinguish positive qrels from all judgments

- **Paper locations:** dataset statistics in `experiments.tex`.
- **Action:** Rename “Qrels” to “Positive qrels” and add total judged pairs, negative labels, zero-positive queries, and mean positives per scored query.

### [ ] MIN6 — Expose model identities

- **Paper locations:** roster table in `experiments.tex`; figures/tables in `results.tex`.
- **Action:** Keep compact IDs but show short model names in every standalone decision table/figure; identify lexical and hybrid baselines clearly.

### [ ] MIN7 — Remove redundant visuals

- **Paper locations:** `method.tex`, `experiments.tex`, and `results.tex`.
- **Action:** Keep one primary pipeline diagram; keep tables for exact values and figures only for uncertainty, sensitivity, or Pareto patterns; move repetitive auto-generated profiles out of the main paper.

### [ ] MIN8 — Deepen qualitative error analysis

- **Paper locations:** `results.tex` and `discussion.tex`.
- **Action:** For every corpus, show one success, one model-specific semantic near-miss, one difficult negative or judge disagreement, and which systems retrieved it; connect these examples to language/domain characteristics without treating them as causal proof.

### [ ] MIN9 — Use ISO dates

- **Paper locations:** provenance subsection/table in `experiments.tex`.
- **Action:** Replace `01/01/2026` with `2026-01-01` and use ISO dates consistently.

### [ ] MIN10 — Document licenses and redistribution

- **Paper locations:** provenance subsection in `experiments.tex`; data-availability statement in `manuscript.tex`.
- **Action:** State source owner, URL/citation, retrieval date, license/terms, redistribution status, transformations, and reconstruction procedure where source documents cannot be redistributed.

### [ ] MIN11 — Correct and strengthen references

- **Paper locations:** `refs.bib`, `intro.tex`, and `related.tex`.
- **Action:** Correct foundational RAG metadata; verify DOI/venue/status; remove weakly related citations; add primary BEIR, MTEB, and pooling sources; ensure every cited claim is supported.

### [ ] MIN12 — Remove promotional wording

- **Paper locations:** all reader-facing TeX sections.
- **Action:** Replace “decisively,” “straightforward,” “actionable,” “sufficient,” “reliable,” “dominant,” and similar terms with measured, conditional wording.

### [ ] MIN13 — State article type and audience

- **Paper locations:** title/Abstract, `intro.tex`, `related.tex`, and `discussion.tex`.
- **Action:** Identify the paper consistently as a practitioner-facing benchmark-method/tool contribution with a demonstration study; disavow algorithmic novelty and universal rankings.

### [ ] MIN14 — Check journal front-matter limits

- **Paper locations:** Abstract, highlights, and keywords in `manuscript.tex`.
- **Action:** After journal selection, check abstract length, highlight count/length, keyword count, declarations, data/code statement, and section-order requirements.

## Priority Order

### P0 — Correct claims and analysis foundations

- [ ] Lock the paper identity and four RQs.
- [ ] Complete M1–M5.
- [ ] Remove unsupported memory, causal language/domain, universal-winner, significance, and all-metric-consistency claims.

### P1 — Generate evidence required by the paper's main goal

- [ ] Complete R2, R3 evidence, M6–M10, and A5.
- [ ] Finalize the candidate roster and primary retrieval configuration before rebuilding pooled judgments.
- [ ] Complete human audit, sensitivity analysis, pool analysis, repeated timing, memory profiling, and model-size collection.
- [ ] Freeze one internally consistent evidence snapshot for all paper tables and figures.

### P2 — Rewrite the paper around practitioner selection

- [ ] Revise in this order: `method.tex` → `experiments.tex` → `results.tex` → `discussion.tex` → `related.tex` → `intro.tex` → Abstract/highlights → `conclusion.tex`.
- [ ] Apply R1, M5, M11, MIN1, MIN8, MIN12, and MIN13 during the rewrite.
- [ ] Give each RQ a direct, bounded answer.

### P3 — Presentation and submission checks

- [ ] Complete MIN2–MIN7, MIN9–MIN11, and MIN14.
- [ ] Verify that every table/figure has a caption, label, and explicit role in the surrounding argument.
- [ ] Verify numerical consistency, terminology, citations, and claim scope.

## Final Manuscript Acceptance Gates

- [ ] All 3 reject, 11 major, and 14 minor reviewer comments are mapped above.
- [ ] The practitioner selection pipeline is the unmistakable central contribution from title through Conclusion.
- [ ] RQ1–RQ4 remain distinct; RQ2 and RQ3 retain language and domain as important selection dimensions.
- [ ] The three datasets are presented as demonstrations, not causal language/domain experiments.
- [ ] The paper shows how corpus properties and project constraints produce an eligible/Pareto shortlist.
- [ ] Memory-aware claims are supported by measured peak CPU RSS and model-size evidence, or removed.
- [ ] Human validation is reported, or claims are explicitly limited to preliminary automated screening.
- [ ] Primary retrieval results use a defensible similarity configuration with sensitivity evidence.
- [ ] Query counts, qrels counts, statistical denominators, operational measurements, tables, and prose agree.
- [ ] No invalid all-metric consistency statistic or unsupported bootstrap p-value remains.
- [ ] The Discussion distinguishes methodological contribution, empirical observations, practitioner implications, and validity limits.
- [ ] The data/code-availability statement identifies an immutable evidence snapshot.
- [ ] Run the full CAS check only after the TeX revision is complete:

  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1 -CompilePdf
  ```

- [ ] Confirm 0 CAS lint errors, successful PDF compilation, resolved citations/references, and readable tables/figures.
