# TODO: Canonical Reviewer-Driven Revision Plan

This is the single working revision checklist for the paper.

`review_action_items.md` is no longer a parallel action list. It is kept only as a short reference note indicating that this file is the canonical plan derived from `reviewer.md`.

## How to use this file

This TODO list turns the reviewer report into concrete revision actions. Each item includes:

- the reviewer concern it addresses;
- the paper sections to update;
- the specific change to make;
- the effort level:
  `easy`, `medium`, `hard`, or `need new data or new experiments`.

The paper's main goals should stay fixed while working through this list:

- `RQ1`: show that the pipeline can generate usable decision-support evidence for local embedding selection;
- `RQ2`: show whether the pipeline can expose language-conditioned ranking changes under one fixed protocol;
- `RQ3`: show whether the pipeline can expose domain-conditioned ranking changes under one fixed protocol;
- `RQ4`: show how the pipeline combines retrieval quality, operational cost, and uncertainty-aware reporting.

## Priority Order

### Blockers first

- [ ] `A6` Resolve the `M5` qrels candidate-pool bias issue.
- [ ] `A7` Add validation or audit evidence for synthetic queries and LLM-generated qrels.
- [ ] `A12` Rework the statistical decision-support section.
- [ ] `A9` Add reproducibility details for prompts, sampling, hardware, software, and timing.
- [ ] `A15` Reframe current language/domain findings as bounded case observations unless new data are added.

### Next text and organization pass

- [ ] `A1` Reframe the title, abstract, and highlights around the real contribution.
- [ ] `A2` Define key terms operationally in the Introduction.
- [ ] `A3` Narrow the framing of `RQ2` and `RQ3`.
- [ ] `A4` Reorganize the Related Work around benchmark-design gaps.
- [ ] `A5` Fully specify the qrels construction algorithm.
- [ ] `A10` Justify the shared parameter choices.
- [ ] `A13` Define the custom aggregate diagnostics.
- [ ] `A21` Add a limitations subsection.
- [ ] `A22` Reduce repetition and tighten evidence-to-claim alignment.
- [ ] `A23` Fix minor terminology and presentation issues.
- [ ] `A24` Audit citations and source recency carefully.

### Stronger resubmission path

- [ ] `A11` Add sensitivity analyses.
- [ ] `A14` Add query-level uncertainty displays.
- [ ] `A16` Expand the dataset set if keeping strong language/domain claims.
- [ ] `A17` Add lexical or hybrid retrieval baselines.
- [ ] `A19` Add workload-stability justification for 50 queries per dataset.
- [ ] `A20` Add an error-analysis subsection.

## Action Items

### A1. Reframe the title and front matter

- Reviewer concern:
  The title is too broad, and the abstract/highlights overstate the maturity of the evidence.
- Sections to update:
  `journal_paper/manuscript.tex`, `journal_paper/intro.tex`, `journal_paper/abstract.tex`
- Action:
  Change the title so it explicitly says this is a local RAG retrieval benchmarking pipeline for corpus-specific embedding-model selection.
  Rewrite the abstract so it says the paper demonstrates the pipeline on a fixed snapshot rather than broadly validating embedding selection.
  Replace `validation` in the highlights with `demonstration` or `case study`.
  Add one abstract sentence that the current snapshot uses synthetic queries and LLM-generated qrels and should be interpreted as bounded evidence.
- Why:
  The paper's real contribution is the workflow, not a universal embedding ranking.
- Effort:
  `easy`

### A2. Define key terms in the Introduction

- Reviewer concern:
  Terms such as `actionable evidence`, `pipeline utility`, `consistency diagnostics`, and `statistical decision support` are not operationally defined.
- Sections to update:
  `journal_paper/intro.tex`
- Action:
  Add a short paragraph defining each term in measurable decision-support terms.
  Rewrite the RQ framing so the reader can tell what counts as answering `RQ1`-`RQ4`.
- Why:
  Some reviewer objections come from imprecise framing rather than missing experiments.
- Effort:
  `easy`

### A3. Narrow the current framing of `RQ2` and `RQ3`

- Reviewer concern:
  The reviewer reads the paper as making stronger language/domain claims than the snapshot can support.
- Sections to update:
  `journal_paper/intro.tex`, `journal_paper/results.tex`, `journal_paper/conclusion.tex`
- Action:
  Reword `RQ2` and `RQ3` so they ask whether the pipeline can expose language- and domain-conditioned ranking changes within this bounded snapshot.
  Replace broad causal phrasing in Results and Conclusion with snapshot-bounded phrasing.
- Why:
  This aligns the claims with the actual scope of the experiment.
- Effort:
  `easy`

### A4. Reorganize the Related Work

- Reviewer concern:
  The Related Work section reads like a literature list instead of a benchmark-design argument.
- Sections to update:
  `journal_paper/related.tex`
- Action:
  Rebuild the section around four threads:
  local/practitioner-facing RAG evaluation;
  synthetic query and qrels construction;
  cross-language/cross-domain embedding selection;
  reproducibility and benchmark governance.
  Add a focused paragraph on qrels pooling / candidate-pool construction as a benchmark-design issue.
  End with a shorter gap statement tied directly to `RQ1`-`RQ4`.
- Why:
  The paper should read as a benchmark-method paper, not as a broad survey.
- Effort:
  `medium`

### A5. Fully specify the qrels construction algorithm

- Reviewer concern:
  The method does not explain the benchmark-construction procedure precisely enough.
- Sections to update:
  `journal_paper/method.tex`, `journal_paper/experiments.tex`
- Action:
  Add an explicit algorithm or numbered workflow for:
  seed-chunk sampling;
  query generation;
  candidate retrieval;
  relevance judging;
  qrels assembly;
  storage of positive and negative judgments.
  Clarify duplicate handling, whether the seed chunk can reappear, and how candidate ranking is formed before judgment.
- Why:
  A workflow paper needs a reproducible procedure, not only a conceptual narrative.
- Effort:
  `medium`

### A6. Resolve the `M5` candidate-pool bias issue

- Reviewer concern:
  `M5` appears to help construct the qrels candidate pool while also being evaluated.
- Sections to update:
  `journal_paper/method.tex`, `journal_paper/experiments.tex`, `journal_paper/results.tex`, `journal_paper/conclusion.tex`
- Action:
  First confirm the implementation.
  If `M5` alone supplies the candidate pool, rebuild qrels using a model-independent or pooled candidate-generation strategy:
  pooled dense top-k across all evaluated models;
  BM25 plus dense pooling;
  an external retriever not included in the benchmarked roster.
  Then rerun the benchmark and report whether rankings change.
  If the implementation is already broader and the wording is just misleading, rewrite the table and prose so that the protocol is unambiguous.
- Why:
  This is the most serious reviewer objection and the largest technical threat to a resubmission.
- Effort:
  `need new data or new experiments`

### A7. Add validation or audit evidence for synthetic queries and qrels

- Reviewer concern:
  The paper gives no human validation for generated queries or LLM-generated relevance labels.
- Sections to update:
  `journal_paper/experiments.tex`, `journal_paper/results.tex`, `journal_paper/conclusion.tex`
- Action:
  Add a subsection such as `Validation of Synthetic Queries and Qrels`.
  Minimum acceptable version:
  manually audit a sample from each dataset and report clearly correct / ambiguous / incorrect cases.
  Stronger version:
  add a second annotator and report agreement.
  Distinguish:
  query-quality validation;
  qrels-quality validation.
- Why:
  This is necessary if the paper wants to claim reliable decision-support evidence.
- Effort:
  `need new data or new experiments`

### A8. Add representative qualitative examples

- Reviewer concern:
  The paper gives no concrete examples of generated queries, judged chunks, or difficult cases.
- Sections to update:
  `journal_paper/results.tex`, optionally `journal_paper/experiments.tex`
- Action:
  Add one compact table or figure with one query example per dataset, one positive judged chunk, one ambiguous or near-miss chunk, and a short explanation.
- Why:
  The reviewer needs to see what the benchmark task actually looks like.
- Effort:
  `medium`

### A9. Add a reproducibility details table

- Reviewer concern:
  Reproducibility is claimed, but the paper omits key implementation details.
- Sections to update:
  `journal_paper/experiments.tex`, `journal_paper/method.tex`
- Action:
  Add a table with:
  hardware;
  CPU/GPU;
  RAM;
  OS;
  Python and library versions;
  ChromaDB version/config;
  PDF/text extraction tool;
  random seed policy;
  LLM version;
  prompt location;
  decoding settings;
  cache behavior;
  exact timing measurement scope.
- Why:
  This is a high-value fix and much of the information likely already exists.
- Effort:
  `medium`

### A10. Justify the parameter choices

- Reviewer concern:
  Parameter settings such as 50 queries, candidate pool 20, chunk size 1000, and `k=10` are not justified.
- Sections to update:
  `journal_paper/experiments.tex`, `journal_paper/method.tex`
- Action:
  Add a short rationale paragraph for each major shared setting.
  If the settings come from the conference version, repo defaults, or practical operating constraints, state that explicitly.
- Why:
  It makes the benchmark look designed rather than arbitrary.
- Effort:
  `easy`

### A11. Add sensitivity analyses

- Reviewer concern:
  The paper does not show whether rankings are robust to key design choices.
- Sections to update:
  `journal_paper/experiments.tex`, `journal_paper/results.tex`, `journal_paper/conclusion.tex`
- Action:
  Add a limited sensitivity study around:
  query count;
  candidate-pool size;
  chunk size;
  retrieval cutoff.
  Suggested minimum:
  query counts `25 / 50 / 100`;
  candidate pools `10 / 20 / 40`;
  cutoff `5 / 10 / 20`;
  one smaller and one larger chunk size.
- Why:
  This strengthens `RQ1` and `RQ4` by showing whether the shortlist is stable.
- Effort:
  `need new data or new experiments`

### A12. Rework the statistical decision-support section

- Reviewer concern:
  The current Friedman and paired t-tests over three datasets are underpowered and potentially misleading.
- Sections to update:
  `journal_paper/results.tex`, `journal_paper/conclusion.tex`
- Action:
  Remove or demote the current pairwise t-test claims.
  Replace them with query-level bootstrap intervals, permutation tests, or another uncertainty method that respects the actual data structure.
  If the current data are all that is available, present this section as descriptive uncertainty support rather than inferential evidence.
- Why:
  The present statistics are easy for reviewers to attack and do not add enough value.
- Effort:
  `need new data or new experiments`

### A13. Define the custom aggregate diagnostics

- Reviewer concern:
  `All-metric CV`, `Worst drop`, and `Score range` are not defined well enough.
- Sections to update:
  `journal_paper/results.tex`, optionally `journal_paper/method.tex`
- Action:
  Add a short explanatory paragraph and, if needed, compact formulas or a footnote.
  Explain why these summaries matter for practitioner decision support.
- Why:
  This is mostly a communication gap and can be fixed cheaply.
- Effort:
  `easy`

### A14. Add query-level uncertainty displays

- Reviewer concern:
  Dataset-level tables hide variability.
- Sections to update:
  `journal_paper/results.tex`
- Action:
  Add bootstrap confidence intervals, boxplots, violin plots, or per-query delta summaries for the main retrieval metric.
- Why:
  This supports the decision-support framing better than the current three-point inferential analysis.
- Effort:
  `need new data or new experiments`

### A15. Reframe dataset findings as case observations

- Reviewer concern:
  Language and domain findings are stronger than the current dataset design supports.
- Sections to update:
  `journal_paper/results.tex`, `journal_paper/conclusion.tex`
- Action:
  Rewrite stronger statements so they are clearly bounded to this dataset snapshot.
  Add one limitation sentence at the start of the language-effect and domain-effect subsections that these are within-snapshot comparisons, not population-level effects.
- Why:
  This is the lowest-cost way to keep the current paper honest if the dataset scope remains unchanged.
- Effort:
  `easy`

### A16. Expand the dataset set if strong claims are retained

- Reviewer concern:
  Three datasets are too few to support stronger cross-language and cross-domain claims.
- Sections to update:
  `journal_paper/experiments.tex`, `journal_paper/results.tex`, `journal_paper/conclusion.tex`
- Action:
  Add more corpora per language and per domain before making stronger generalizations.
  Target:
  at least two corpora per language-domain cell that matters to the argument.
- Why:
  This is the real path to defending `RQ2` and `RQ3` as journal-strength empirical claims.
- Effort:
  `need new data or new experiments`

### A17. Add lexical or hybrid baselines

- Reviewer concern:
  The model roster is too narrow and dense-only.
- Sections to update:
  `journal_paper/experiments.tex`, `journal_paper/results.tex`, `journal_paper/related.tex`
- Action:
  Add BM25 at minimum, and a simple hybrid baseline if feasible.
  Reframe the roster discussion so it is either clearly scoped as an open-weight dense benchmark or broadened into a more practitioner-realistic comparison.
- Why:
  This makes `RQ1` more credible from a deployment perspective.
- Effort:
  `need new data or new experiments`

### A18. Explain the model roster and family labels more carefully

- Reviewer concern:
  Terms such as `monolingual` and `multilingual` may be too coarse.
- Sections to update:
  `journal_paper/experiments.tex`, `journal_paper/results.tex`
- Action:
  Refine the descriptions of `M1`-`M5` based on model documentation.
  Clarify whether the labels are shorthand for discussion or strict model-training claims.
- Why:
  It removes visible technical imprecision.
- Effort:
  `easy`

### A19. Add a workload-stability justification for 50 queries

- Reviewer concern:
  The reviewer questions whether 50 synthetic queries per dataset are enough.
- Sections to update:
  `journal_paper/experiments.tex`, `journal_paper/results.tex`
- Action:
  Best version:
  add a stability curve showing whether rankings settle as the query count increases.
  Lower-effort fallback:
  add a clear rationale that 50 is a baseline demonstration size and not a universal benchmark prescription.
- Why:
  It answers or narrows one of the core scale objections.
- Effort:
  `need new data or new experiments`

### A20. Add an error-analysis subsection

- Reviewer concern:
  The paper lacks failure patterns, ambiguous cases, and difficulty analysis.
- Sections to update:
  `journal_paper/results.tex`
- Action:
  Add a short subsection with failure types and examples.
  Include a note on whether near-perfect `Success@10` on `education_eng` suggests the task may be too easy or too close to seed chunks.
- Why:
  This addresses the reviewer's concern that the benchmark may be overly synthetic or too easy in parts.
- Effort:
  `medium`

### A21. Add a limitations subsection

- Reviewer concern:
  Important current limitations are pushed too far into Future Work.
- Sections to update:
  `journal_paper/conclusion.tex`
- Action:
  Add a short standalone limitations paragraph or subsection covering:
  small number of datasets;
  synthetic query generation;
  automated qrels;
  inferential limits;
  hardware-dependent timing.
- Why:
  This makes the paper more defensible even before all stronger experiments are completed.
- Effort:
  `easy`

### A22. Reduce repetition and tighten evidence-to-claim alignment

- Reviewer concern:
  The manuscript repeats its framing too often and leans heavily on conceptual figures.
- Sections to update:
  `journal_paper/intro.tex`, `journal_paper/method.tex`, `journal_paper/results.tex`, `journal_paper/conclusion.tex`
- Action:
  Trim repeated phrasing such as `local benchmarking`, `fit-for-purpose`, `fixed protocol`, and `not a universal ranking`.
  If space is tight, consider replacing a conceptual figure with a validation/evidence figure.
- Why:
  The revision should feel more rigorous and less repetitive.
- Effort:
  `medium`

### A23. Fix terminology and presentation details

- Reviewer concern:
  Several smaller issues reduce polish and precision.
- Sections to update:
  `journal_paper/manuscript.tex`, `journal_paper/method.tex`, `journal_paper/experiments.tex`, `journal_paper/results.tex`
- Action:
  Define `qrels` at first use.
  Replace `query-construction judge` with clearer wording.
  Clarify whether negative labels are stored or only positive qrels are retained.
  Justify candidate-pool size 20.
  Add an appendix or repository pointer to the exact curated document list.
  Remove the hidden encoding artifact before Results if present.
- Why:
  These are low-effort credibility fixes.
- Effort:
  `easy`

### A24. Audit citations and source matching

- Reviewer concern:
  The paper relies heavily on recent sources and should be checked carefully.
- Sections to update:
  `journal_paper/related.tex`, `journal_paper/refs.bib`
- Action:
  Verify that each citation is real, correctly attributed, and matched to the sentence it supports.
  Replace weak or overloaded citations with stronger benchmark-methodology sources where needed.
- Why:
  A methods paper is vulnerable if the citation layer looks unstable.
- Effort:
  `medium`

## Recommended Working Sequence

### Phase 1: Fix what can be fixed by writing, disclosure, and structure

- [ ] `A1`
- [ ] `A2`
- [ ] `A3`
- [ ] `A4`
- [ ] `A5`
- [ ] `A9`
- [ ] `A10`
- [ ] `A13`
- [ ] `A15`
- [ ] `A18`
- [ ] `A21`
- [ ] `A22`
- [ ] `A23`
- [ ] `A24`

### Phase 2: Decide whether the paper stays a bounded demonstration or becomes a stronger resubmission

- If not doing new experiments:
  soften claims heavily and make the paper explicitly a bounded demonstration of the pipeline.
- If doing new experiments:
  prioritize `A6`, `A7`, `A11`, `A12`, `A14`, `A16`, `A17`, `A19`, `A20`.

## Most Important Decision Point

If `A6`, `A7`, and `A12` cannot be addressed with stronger evidence, the paper should be revised as a more modest demonstration paper rather than presented as a strong journal-level comparative evaluation paper.
