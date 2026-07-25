# Cold-Start Prompts for Completing `todo.md`

## How to Use This File

Run the prompts **in order**, using one fresh agent session per prompt. Copy the complete prompt block into the cold-start session. Do not combine prompts: each is deliberately limited to a small manuscript scope.

The prompts assume the repository is:

`C:\Codes\RagRetrievalBench`

The pipeline and experiment are complete. These prompts revise only the paper. No prompt authorizes changes to pipeline code, configuration, datasets, qrels, models, raw results, generated figures, or experimental execution.

Intermediate agents must not edit `todo.md`; Prompt 10 performs the final evidence-based checkbox audit.

## Sequence and Coverage

| Prompt | Primary task | Main TODO/reviewer coverage |
|---|---|---|
| 1 | Reposition Method | Method, central per-corpus workflow, R3, M8, M10 |
| 2 | Clarify Experiments | Experiments, R1–R2, M1–M2, M6–M10, MIN3–MIN5, MIN9–MIN10 |
| 3 | Restructure Results | Results, R1–R3, M2–M9, MIN4, MIN6–MIN8, MIN12 |
| 4 | Add Discussion | Discussion, R1–R3, M1, M3, M5–M11, MIN8, MIN12–MIN13 |
| 5 | Strengthen Related Work | Related Work, R3, M6, M10–M11, MIN11, MIN13 |
| 6 | Revise Introduction and RQs | Introduction, R1, R3, M4–M5, M11, MIN2, MIN12–MIN13 |
| 7 | Revise Abstract and front matter | Front matter, R1–R3, M3, MIN1–MIN2, MIN12–MIN14 |
| 8 | Revise Conclusion and limitations | Conclusion, R1–R3, M1, M3–M11, MIN12–MIN13 |
| 9 | Global consistency and presentation audit | All claim rules and minor comments |
| 10 | Final verification, PDF, and TODO closure | All final acceptance gates and checkbox status |

Explicit reviewer-ID coverage:

- Reject: `R1`, `R2`, `R3`.
- Major: `M1`, `M2`, `M3`, `M4`, `M5`, `M6`, `M7`, `M8`, `M9`, `M10`, `M11`.
- Minor: `MIN1`, `MIN2`, `MIN3`, `MIN4`, `MIN5`, `MIN6`, `MIN7`, `MIN8`, `MIN9`, `MIN10`, `MIN11`, `MIN12`, `MIN13`, `MIN14`.

---

## Prompt 1 — Reposition the Method

```text
You are a cold-start manuscript-editing agent working in:

C:\Codes\RagRetrievalBench

Your capability is intentionally limited. Complete only the Method revision
described below.

AUTHORIZED FILE:
- journal_paper/method.tex

READ-ONLY CONTEXT:
- AGENTS.md
- todo.md
- reviewer.md
- journal_paper/manuscript.tex
- journal_paper/intro.tex
- journal_paper/experiments.tex
- journal_paper/results.tex
- journal_paper/conclusion.tex

Do not edit todo.md. Do not edit any pipeline, configuration, script, dataset,
qrels, raw result, image, generated build file, or bibliography file. Preserve
all unrelated working-tree changes.

Before editing:
1. Read AGENTS.md completely and obey the TeX-first, flat-folder, section-
   boundary, terminology, citation, table, and figure rules.
2. Read todo.md completely, especially Central Research Position, Role of
   Language and Domain, Claim and Terminology Rules, Method, R3, M8, M10, and
   the Final Acceptance Gates.
3. Inspect git status and the current Method. Do not overwrite user changes.

CENTRAL POSITION TO EXPRESS

A practitioner should not assume one embedding model will be optimal for every
corpus under their control. The completed pipeline evaluates the same candidate
roster separately on each corpus and produces a separate dataset-level report.
The practitioner may therefore select different models for different corpora.
The aggregate report is secondary comparative context, not a command to deploy
one global model.

IMPLEMENTATION TASKS

1. Preserve the implemented stage sequence and all methodologically accurate
   details. Do not invent a new stage.
2. Strengthen the opening and Pipeline Overview so that:
   - every corpus is routed, processed, indexed, evaluated, and reported in
     isolation;
   - the same roster and fixed protocol make the corpus reports comparable;
   - one practitioner can repeat the workflow for several controlled corpora;
   - the dataset-level report is the primary model-selection artifact.
3. Revise Automated Reporting and Reproducibility so that:
   - one dataset report supports one corpus-specific shortlist;
   - the aggregate report is optional secondary context;
   - heterogeneous language/domain subsets may be evaluated separately;
   - implementation availability is not described as immutable archival
     reproducibility.
4. Preserve the distinction between query generator and relevance judge.
5. Keep pooled-qrels wording bounded: pooling reduces single-model privilege,
   but does not guarantee complete ground truth.
6. Limit operational outputs to what exists: retrieval metrics, combined corpus
   embedding/index-insertion timing, and combined query-embedding/vector-search
   latency.
7. Do not add runtime memory, model-size decision logic, Pareto analysis, hard
   constraints, eligibility filtering, new baselines, human auditing, or other
   unimplemented capabilities.
8. Use “practitioner,” “paper,” “document collection,” “corpus-specific,” and
   “English-oriented” consistently where relevant.
9. Keep Method free of manuscript-specific numerical result interpretation;
   leave frozen setup values in Experiments and empirical findings in Results.
10. Keep all current labels stable unless a duplicate or broken label requires
    correction.

QUALITY CHECKS

- Search the edited Method for “universal,” “best model,” “memory,” “Pareto,”
  “hard constraint,” and “actionable.” Ensure any occurrence is accurate and
  bounded.
- Confirm every retained table and figure has caption, label, and surrounding
  prose reference.
- Confirm no result value or experimental outcome was added to Method.
- Run:

  powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1

If the build fails, fix only Method-caused errors. Do not change other sections
to conceal a Method problem.

FINAL RESPONSE

Report:
- the Method subsections changed;
- how per-corpus selection and secondary aggregation were clarified;
- todo/reviewer concerns addressed in this batch;
- any residual issue requiring a later prompt;
- the exact build result.

Do not claim the entire paper or todo.md is complete.
```

---

## Prompt 2 — Clarify the Frozen Experiments

```text
You are a cold-start manuscript-editing agent working in:

C:\Codes\RagRetrievalBench

Complete only the Experiments revision. The pipeline and frozen experiment must
remain unchanged.

AUTHORIZED FILE:
- journal_paper/experiments.tex

READ-ONLY CONTEXT:
- AGENTS.md
- todo.md
- reviewer.md
- journal_paper/manuscript.tex
- journal_paper/method.tex
- journal_paper/results.tex
- journal_paper/conclusion.tex

Do not edit todo.md, code, configuration, datasets, qrels, raw results, figures,
or generated build files. Do not run the benchmark or regenerate evidence.
Preserve unrelated working-tree changes.

Before editing:
1. Read AGENTS.md and todo.md completely.
2. Verify that Prompt 1's Method revision is present. If it is clearly absent,
   stop and report the missing prerequisite instead of compensating in
   Experiments.
3. Inspect git status and all current Experiments tables/captions.

CENTRAL POSITION

The three corpora are worked demonstrations of separate corpus-specific model
selection under one completed protocol. They create meaningful language,
domain, structure, and scale variation, but they do not isolate causal language
or domain effects.

IMPLEMENTATION TASKS

1. Reframe Experimental Snapshot and Datasets:
   - explain that the same five-model roster is evaluated independently on each
     corpus;
   - state that separate dataset reports demonstrate how a practitioner may
     make different choices;
   - avoid saying the design isolates language or domain.
2. Preserve the three observed cases and all frozen workload values.
3. Correct query accounting:
   - keep 150 as the number of generated queries;
   - disclose 148 statistically scored positive-bearing queries;
   - report 48 for education_eng and 50 for each Turkish dataset;
   - explain that zero-positive queries are excluded by the evaluator;
   - do not silently replace all 150-query workload statements with 148.
4. Relabel the dataset table's “Qrels” column as “Positive qrels.”
5. Clarify that explicit negative judgments are also stored and distinguish
   positive qrels from all judged pairs without inventing counts.
6. State the exact completed retrieval geometry prominently:
   - default non-normalized embeddings;
   - ChromaDB squared-Euclidean/L2 space;
   - results are conditional on this configuration;
   - remove any suggestion that cosine necessarily preserves the same ordering.
7. Describe fixed parameters as demonstration settings, not optima:
   chunk size 1000, overlap 200, 50 generated queries, top-20 pool, and k=10.
8. Clarify roster scope:
   - five accessible Sentence-Transformers candidates;
   - selected partly through popularity/accessibility;
   - not comprehensive of lexical, hybrid, reranking, domain-adapted, newer
     multilingual, or commercial alternatives.
9. Standardize model-family language to “English-oriented” and “multilingual.”
10. Clarify operational measurements:
    - embedding throughput combines corpus embedding and index insertion;
    - query latency combines query embedding and vector search;
    - timing is single-run, single-machine, CPU-only, and descriptive;
    - runtime memory was not measured;
    - do not invent CPU/RAM/thread details that are not already recorded.
11. Define or clearly point to definitions for MAP@10, Recall@10, Precision@10,
    NDCG@10, MRR@10, and Success@10, including zero-positive handling. Keep
    equations concise and within Experiments/Method boundaries.
12. Define aggregate concepts used later: dataset macro means, average rank,
    and weighted latency. Use only the existing calculations.
13. Change the provenance date from 01/01/2026 to 2026-01-01.
14. State only verified source ownership, provenance, and redistribution
    limitations. Do not invent licenses or permissions.
15. Reframe reproducibility:
    - describe available artifacts accurately;
    - distinguish a live repository from an immutable archive;
    - do not claim DOI/tagged archival durability unless it exists.

REVIEWER COVERAGE

This batch contributes to R1, R2, M1, M2, M6, M7, M8, M9, M10, MIN3, MIN4,
MIN5, MIN9, and MIN10. It handles them through clarification and scope
restriction only; it does not create missing experiments.

QUALITY CHECKS

- Search Experiments for: “monolingual,” “effect,” “dominates,” “optimal,”
  “sufficient,” “memory,” “150,” “148,” and “01/01/2026.”
- Verify every occurrence is correct and bounded.
- Verify all table/figure captions and labels remain present and unique.
- Run:

  powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1

Fix only errors caused by this batch.

FINAL RESPONSE

Report:
- exact Experiments subsections and tables changed;
- final generated/scored query wording;
- final geometry/timing/roster limitations;
- reviewer items advanced;
- unresolved residual risks;
- build result.

Do not edit todo.md or claim the full revision is complete.
```

---

## Prompt 3 — Restructure Results Around Per-Corpus Decisions

```text
You are a cold-start manuscript-editing agent working in:

C:\Codes\RagRetrievalBench

Complete only the Results restructuring using the existing frozen evidence.

AUTHORIZED FILE:
- journal_paper/results.tex

READ-ONLY CONTEXT:
- AGENTS.md
- todo.md
- reviewer.md
- journal_paper/manuscript.tex
- journal_paper/method.tex
- journal_paper/experiments.tex
- journal_paper/conclusion.tex

Do not edit todo.md, code, configuration, data, qrels, raw results, image files,
or generated build files. Do not rerun analyses or invent numerical results.
Preserve unrelated changes.

Before editing:
1. Read AGENTS.md and todo.md completely.
2. Verify Prompt 1 and Prompt 2 changes are present. If a prerequisite is
   missing, stop and report it.
3. Read Results completely before changing any subsection.

CENTRAL RESULTS STORY

Dataset-level decisions are primary:
- education_eng: M1 is both highest MAP@10 and lowest latency.
- education_tr: M5 is quality-first; M3 is a lower-latency compromise.
- law_tr: M5 is quality-first; M3 is a lower-latency compromise.

The different English/Turkish selections show why one model should not be
assumed for all corpora. The similar Turkish selections show that local
evaluation can also confirm stability. Aggregate M5 performance is secondary
cross-corpus context, not a universal deployment recommendation.

IMPLEMENTATION TASKS

1. Rename “Cross-Dataset Headline Findings” to “Corpus-Specific Selection
   Outcomes.”
2. Open Results with the three corpus-to-recommendation outcomes above.
3. Move aggregate ranking interpretation after the corpus-specific outcomes and
   label it secondary.
4. Keep all frozen metric and timing values unchanged unless correcting a
   demonstrable transcription inconsistency.
5. Replace unqualified “best model” with a conditional description naming the
   corpus, roster, protocol, metric, or priority.
6. Rename:
   - “Language Effect” to “Language-Associated Comparison of the Education
     Corpora”
   - “Domain Effect Within Turkish” to “Domain-Associated Comparison of the
     Turkish Corpora”
7. Preserve language and domain importance while removing causal explanations:
   - report different English/Turkish family rankings;
   - report similar Turkish leading rankings;
   - remove “language dominates domain/difficulty.”
8. Revise the cross-dataset consistency table:
   - remove all-metric CV;
   - remove worst drop;
   - remove score range;
   - remove “consistency penalty” prose;
   - retain interpretable existing columns such as average rank, mean MAP@10,
     and wins;
   - adjust caption, column specification, and surrounding prose consistently.
9. Revise Statistical Decision Support:
   - distinguish 150 generated from 148 scored queries;
   - use 148 in statistical captions/prose;
   - remove bootstrap p-values and the p-value column;
   - remove “significant,” “separated,” and formal inferential language;
   - retain confidence intervals as descriptive, snapshot-conditional
     uncertainty;
   - acknowledge dependence and lack of population generalization.
10. Narrow pool-robustness claims:
    - retain positive-yield differences and observed ordering stability;
    - say the ranking was stable across the two tested constructions;
    - remove “decisively,” “not an artifact,” complete/unbiased, and arbitrary
      future-system reuse claims.
11. Keep timing interpretations conditional on compound, single-machine values.
12. Add a prose-only worked practitioner interpretation using existing results:
    one organization could use M1 for its English education corpus, M5 where
    Turkish retrieval quality is prioritized, or M3 where Turkish latency is
    more important.
13. Do not add Pareto analysis, memory claims, new tables requiring calculation,
    new models, baselines, sensitivity results, or human validation.
14. Calibrate qualitative examples:
    - present existing examples as illustrations;
    - do not claim unreported model-specific failure frequencies;
    - do not imply human confirmation or judge-agreement evidence.
15. Improve model readability by pairing M1–M5 with short names in key
    standalone captions/tables where space permits.
16. Remove or relocate redundant per-dataset figures only when the adjacent
    table already communicates the same point. Do not delete image files.

REVIEWER COVERAGE

This batch contributes to R1–R3, M2–M9, MIN4, MIN6–MIN8, and MIN12.

QUALITY CHECKS

- Search Results for: “150 queries,” “p<,” “p=,” “significant,” “separated,”
  “CV,” “worst drop,” “score range,” “consistency penalty,” “language effect,”
  “domain effect,” “dominates,” “decisively,” “artifact,” “monolingual,” and
  “best model.”
- Confirm prohibited claims are removed or properly bounded.
- Verify changed tables still have matching tabular column counts.
- Verify all figure/table labels and prose references remain valid.
- Run:

  powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1

Fix only Results-caused errors.

FINAL RESPONSE

Report:
- new Results structure;
- retained corpus-specific recommendations;
- removed invalid/inferential claims;
- tables/figures changed or relocated;
- residual methodological risks;
- build result.

Do not edit todo.md or claim the full paper is finalized.
```

---

## Prompt 4 — Add the Discussion Section

```text
You are a cold-start manuscript-editing agent working in:

C:\Codes\RagRetrievalBench

Add and integrate a dedicated Discussion section using only existing paper
evidence.

AUTHORIZED FILES:
- journal_paper/discussion.tex (new flat source file)
- journal_paper/manuscript.tex (only to add the Discussion input)

READ-ONLY CONTEXT:
- AGENTS.md
- todo.md
- reviewer.md
- journal_paper/intro.tex
- journal_paper/related.tex
- journal_paper/method.tex
- journal_paper/experiments.tex
- journal_paper/results.tex
- journal_paper/conclusion.tex
- journal_paper/refs.bib

Do not edit todo.md or any other file. Do not change front-matter content in
manuscript.tex. Preserve unrelated changes.

Before editing:
1. Read AGENTS.md and todo.md completely.
2. Verify Prompts 1–3 revisions are present. Stop if they are not.
3. Read Results and Conclusion completely so Discussion interprets rather than
   duplicates them.

IMPLEMENTATION TASKS

1. Create journal_paper/discussion.tex as a flat TeX source.
2. Add:

   \input{discussion.tex}

   in manuscript.tex immediately after results.tex and before conclusion.tex.
3. Use:

   \section{Discussion}\label{discussion}

4. Create four coherent subsections, each with a stable unique label:
   - Practitioner implications
   - Language- and domain-aware corpus partitioning
   - Relation to prior benchmark workflows
   - Validity and transfer limits
5. Practitioner implications:
   - explain that one organization may select different models for different
     corpora;
   - use M1/M5/M3 only as snapshot examples;
   - make dataset-level reports primary and aggregate M5 secondary.
6. Language/domain:
   - retain both as important corpus characteristics;
   - explain that observed difference and stability should be measured;
   - do not attribute causality or claim language generally dominates domain.
7. Prior workflows:
   - frame contribution as integrated automation of local corpus preparation,
     query/qrels construction, shared-roster comparison, timing summaries,
     artifact preservation, and dataset-level reporting;
   - do not claim a new embedding algorithm, metric, or universal benchmark;
   - use only citation keys already verified in refs.bib.
8. Validity and transfer limits must explicitly cover:
   - synthetic queries and same-family LLM judging;
   - no human validation;
   - raw non-normalized L2;
   - five-model bounded roster and no lexical/hybrid baseline;
   - fixed chunk/query/pool/k protocol and no sensitivity study;
   - roster-conditional pooled qrels;
   - compound single-run, single-machine timing;
   - live-repository versus immutable-archive limitation;
   - no runtime-memory measurement.
9. Explain that these limits make the output preliminary corpus-specific
   decision support, not a deployment guarantee.
10. Do not introduce new data, calculations, citations, tables, figures,
    algorithms, or pipeline features.

REVIEWER COVERAGE

This batch contributes to R1–R3, M1, M3, M5–M11, MIN8, MIN12, and MIN13.

QUALITY CHECKS

- Confirm discussion.tex is flat under journal_paper/.
- Confirm manuscript.tex contains exactly one discussion input in the correct
  position.
- Search Discussion for “proves,” “universal,” “dominates,” “validated,”
  “significant,” “memory-aware,” “Pareto,” and unqualified “best.”
- Run:

  powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1

Fix only Discussion integration errors.

FINAL RESPONSE

Report:
- new Discussion structure;
- manuscript input placement;
- major practitioner and limitation arguments;
- residual reviewer risks;
- build result.

Do not edit todo.md or revise another section.
```

---

## Prompt 5 — Strengthen Related Work and Bibliography Positioning

```text
You are a cold-start manuscript-editing agent working in:

C:\Codes\RagRetrievalBench

Complete only the Related Work and bibliography-positioning batch.

AUTHORIZED FILES:
- journal_paper/related.tex
- journal_paper/refs.bib

READ-ONLY CONTEXT:
- AGENTS.md
- todo.md
- reviewer.md
- journal_paper/intro.tex
- journal_paper/method.tex
- journal_paper/experiments.tex
- journal_paper/results.tex
- journal_paper/discussion.tex
- journal_paper/conclusion.tex
- journal_paper/template/cas-refs.bib

Do not edit todo.md, manuscript.tex, other TeX sections, code, data, figures, or
generated files. Preserve unrelated changes.

Before editing:
1. Read AGENTS.md and todo.md completely.
2. Verify Discussion exists and is included. Stop if Prompt 4 is incomplete.
3. Audit every existing Related Work citation against its nearby claim.
4. If the crossref-citation-check skill is available, use it for bibliographic
   validation. If web lookup is needed, use primary/official sources only.
5. Never invent DOI, venue, author, year, URL, or access metadata.

IMPLEMENTATION TASKS

1. Reorganize Related Work around the paper's actual contribution:
   - local/practitioner retrieval evaluation;
   - synthetic query and qrels construction;
   - language/domain-sensitive embedding selection;
   - reproducibility and benchmark governance;
   - gap and positioning.
2. Reduce long lists of unrelated RAG applications. Retain only work that
   supports the local selection, evaluation, pooling, multilingual/domain, or
   reproducibility argument.
3. Add or strengthen primary positioning for:
   - BEIR-style heterogeneous retrieval evaluation;
   - original MTEB embedding evaluation;
   - classical/TREC pooling;
   - relevant RAG evaluation frameworks.
4. Add a concise capability-comparison table only if it can be supported
   accurately from cited sources. If added:
   - give it a caption and unique label;
   - use booktabs;
   - compare documented capabilities, not empirical superiority;
   - include local-corpus construction, pooled judgments, per-corpus model
     comparison, operational timing, artifact preservation, and reporting.
5. State the gap narrowly:
   integrated automation for turning a practitioner's own corpus into a
   repeatable dataset-level embedding-model comparison.
6. State explicitly that individual components are established practices and
   integration/automation is the contribution.
7. Present the five-model experiment as a demonstration of the workflow, not a
   comprehensive benchmark.
8. Preserve the distinction from the earlier conference paper without
   overstating journal novelty.
9. Audit refs.bib:
   - correct foundational RAG metadata;
   - verify author, title, year, venue, DOI/URL, and publication status;
   - use CAS-compatible @misc website formatting;
   - wrap organizational authors in double braces;
   - remove unused or unsupported entries only when safe;
   - preserve all keys cited elsewhere.
10. Use natbib citation commands and keep the bibliography contract unchanged.

REVIEWER COVERAGE

This batch contributes to R3, M6, M10, M11, MIN11, and MIN13.

QUALITY CHECKS

- Verify every citation key in related.tex exists in refs.bib.
- Verify no existing citation key used by another section was removed.
- Search for unsupported phrases such as “first,” “unique,” “comprehensive,”
  and “outperforms.”
- Run:

  powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1

Fix only Related Work/bibliography errors introduced by this batch.

FINAL RESPONSE

Report:
- Related Work structure changed;
- primary benchmark/pooling sources added or corrected;
- any capability table added;
- citation metadata corrections;
- sources that could not be verified;
- build result.

Do not edit todo.md or claim all bibliography work is complete beyond the
verified scope.
```

---

## Prompt 6 — Revise the Introduction, Contributions, and RQs

```text
You are a cold-start manuscript-editing agent working in:

C:\Codes\RagRetrievalBench

Complete only the Introduction and research-question revision.

AUTHORIZED FILE:
- journal_paper/intro.tex

READ-ONLY CONTEXT:
- AGENTS.md
- todo.md
- reviewer.md
- journal_paper/manuscript.tex
- journal_paper/related.tex
- journal_paper/method.tex
- journal_paper/experiments.tex
- journal_paper/results.tex
- journal_paper/discussion.tex
- journal_paper/conclusion.tex
- journal_paper/refs.bib

Do not edit todo.md or any other file. Preserve unrelated changes.

Before editing:
1. Read AGENTS.md and todo.md completely.
2. Verify Prompts 1–5 are reflected in the current paper. Stop if a prerequisite
   is absent.
3. Read the revised Method, Results, Discussion, and Related Work before
   rewriting Introduction.

CENTRAL MOTIVATION

One practitioner or organization may control several heterogeneous corpora.
The suitable embedding model can differ by corpus and operational priority.
Generic rankings or one previous local result should not be transferred
automatically. The completed pipeline automates comparable per-corpus
evaluation and reporting.

IMPLEMENTATION TASKS

1. Reorder the motivation:
   - practitioners manage local corpora with different language, domain,
     structure, and information needs;
   - generic leaderboards and ad hoc trials cannot determine every local
     choice;
   - manual comparison is costly and may change multiple protocol variables;
   - the pipeline applies one controlled workflow separately to each corpus.
2. State the defensible thesis:
   “No universally best embedding model should be assumed.”
   Do not claim the study proves no universal best model exists.
3. Make dataset-level selection primary and aggregate comparison secondary.
4. Revise contributions to exactly these themes:
   - repeatable per-corpus benchmark construction;
   - shared-protocol candidate comparison;
   - dataset-level and secondary aggregate quality/operational reporting;
   - preserved artifacts for inspection and report regeneration.
5. Do not claim a new embedding model, retrieval algorithm, IR metric, causal
   language/domain study, comprehensive benchmark, or deployment guarantee.
6. Preserve all four RQ numbers and themes. Make only these edits:
   - RQ1: change “on a local document collection” to
     “on each local document collection.”
   - RQ2: keep its wording; add immediate clarification that it is a bounded
     two-corpus education comparison, not a causal language experiment.
   - RQ3: minimally replace “domain-conditioned ranking changes” with
     “domain-associated ranking differences or stability.”
   - RQ4: keep its wording; define operational cost only as reported
     embedding/insertion throughput and query latency.
7. Redefine decision-support evidence:
   - supports preliminary corpus-specific screening/shortlisting;
   - is not “sufficient” or independently validated;
   - is conditional on the fixed protocol and synthetic evidence.
8. Remove the invalid all-metric consistency-diagnostic definition.
9. Keep language and domain important as corpus-partitioning and interpretation
   dimensions without causal wording.
10. Use “English-oriented,” “practitioner,” and “paper” consistently.
11. Ensure the section roadmap includes the new Discussion.

REVIEWER COVERAGE

This batch contributes to R1, R3, M4, M5, M11, MIN2, MIN12, and MIN13.

QUALITY CHECKS

- Confirm exactly four RQs remain and are numbered RQ1–RQ4.
- Compare RQ text against todo.md; do not broaden the allowed edits.
- Search for “universal,” “best,” “actionable,” “sufficient,” “reliable,”
  “dominates,” “effect,” “consistency diagnostics,” “monolingual,” and
  “memory.”
- Verify all citations resolve.
- Run:

  powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1

Fix only Introduction-caused errors.

FINAL RESPONSE

Report:
- revised motivation and contributions;
- exact RQ changes;
- removed definitions/overclaims;
- reviewer items advanced;
- build result.

Do not edit todo.md or another section.
```

---

## Prompt 7 — Revise Abstract, Highlights, Keywords, and Front Matter

```text
You are a cold-start manuscript-editing agent working in:

C:\Codes\RagRetrievalBench

Complete only the front-matter content revision.

AUTHORIZED FILE:
- journal_paper/manuscript.tex

READ-ONLY CONTEXT:
- AGENTS.md
- todo.md
- reviewer.md
- journal_paper/intro.tex
- journal_paper/related.tex
- journal_paper/method.tex
- journal_paper/experiments.tex
- journal_paper/results.tex
- journal_paper/discussion.tex
- journal_paper/conclusion.tex

Do not edit todo.md or any other file. Do not remove or alter mandatory CAS
front-matter commands, authorship, affiliation, bibliography contract, or
section-input order. Preserve unrelated changes, including the Discussion input
added by Prompt 4.

Before editing:
1. Read AGENTS.md and todo.md completely.
2. Verify Prompts 1–6 are complete. Stop if the paper body still carries the old
   central argument.
3. Read the revised Introduction, Results, and Discussion before editing the
   Abstract.

IMPLEMENTATION TASKS

1. Preserve the current title unless it conflicts with revised paper identity;
   it already emphasizes corpus-specific selection.
2. Rewrite the Abstract around:
   - the practitioner may control several heterogeneous corpora;
   - one model should not be assumed optimal for all;
   - the completed pipeline evaluates the same roster separately and generates
     dataset-level reports;
   - aggregate reporting is secondary.
3. Report only existing evidence:
   - M1 is highest-MAP@10 and lowest-latency for education_eng;
   - M5 is quality-first for both Turkish corpora;
   - M3 is a lower-latency Turkish compromise;
   - the education comparison differs by model family;
   - the Turkish-domain comparison preserves leading rankings.
4. Do not write “language dominates domain/difficulty.”
5. Keep 150 as generated queries; if statistical sample size is mentioned,
   distinguish 148 scored.
6. Remove bootstrap p-values/significance language and invalid consistency
   claims.
7. State limitations compactly: synthetic queries/LLM qrels without human
   validation, raw-L2 fixed protocol, bounded roster, and descriptive timing.
8. Describe output as preliminary corpus-specific decision support, not
   actionable/validated/deployment-grade selection.
9. Rewrite highlights so they cover:
   - per-corpus evaluation;
   - possible different selections for different corpora;
   - quality and measured operational trade-offs;
   - auditable shared-protocol reports.
10. Use “English-oriented,” not “monolingual.”
11. Keep keywords concise and aligned with the method/tool identity.
12. Do not claim runtime memory, Pareto analysis, new baselines, sensitivity,
    human validation, or immutable archival reproduction.
13. Preserve all required CAS front-matter elements listed in AGENTS.md.
14. The target journal is not specified. Check generic CAS compliance now; do
    not claim target-journal-specific limits are satisfied. Leave that as a
    conditional submission task.

REVIEWER COVERAGE

This batch contributes to R1–R3, M3, MIN1, MIN2, MIN12, MIN13, and MIN14.

QUALITY CHECKS

- Verify all mandatory CAS front matter remains.
- Search manuscript.tex for “monolingual,” “dominates,” “significant,”
  “actionable,” “validated,” “memory,” “Pareto,” and unqualified “best.”
- Confirm discussion.tex remains included after results.tex and before
  conclusion.tex.
- Run:

  powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1

Fix only front-matter-caused errors.

FINAL RESPONSE

Report:
- title decision;
- Abstract/highlight/keyword changes;
- preserved CAS elements;
- remaining journal-specific front-matter dependency;
- build result.

Do not edit todo.md or another section.
```

---

## Prompt 8 — Revise Conclusion, Limitations, and Future Work

```text
You are a cold-start manuscript-editing agent working in:

C:\Codes\RagRetrievalBench

Complete only the Conclusion, Limitations, and Future Work revision.

AUTHORIZED FILE:
- journal_paper/conclusion.tex

READ-ONLY CONTEXT:
- AGENTS.md
- todo.md
- reviewer.md
- journal_paper/manuscript.tex
- journal_paper/intro.tex
- journal_paper/related.tex
- journal_paper/method.tex
- journal_paper/experiments.tex
- journal_paper/results.tex
- journal_paper/discussion.tex

Do not edit todo.md or any other file. Preserve unrelated changes.

Before editing:
1. Read AGENTS.md and todo.md completely.
2. Verify Prompts 1–7 are present. Stop if the Abstract/RQs/Results still express
   incompatible claims.
3. Read the revised RQs, Results, and Discussion before editing.

IMPLEMENTATION TASKS

1. Lead with the completed pipeline's per-corpus selection purpose, not M5's
   aggregate ranking.
2. State the defensible conclusion:
   a practitioner should benchmark each materially distinct corpus rather than
   assume one generic or aggregate winner.
3. Answer every RQ directly and in order:
   - RQ1: separate dataset reports provide comparable per-corpus evidence;
   - RQ2: the two education cases show different family rankings, without a
     causal language claim;
   - RQ3: the two Turkish cases show ranking stability, without claiming domain
     irrelevance;
   - RQ4: quality, embedding/insertion throughput, query latency, and
     descriptive uncertainty support different corpus/priority choices.
4. Use existing outcomes only:
   - education_eng → M1;
   - Turkish quality-first → M5;
   - Turkish lower-latency compromise → M3.
5. Make aggregate M5 secondary context.
6. Remove:
   - bootstrap p-values and significance claims;
   - “language dominates” wording;
   - universal superiority;
   - “actionable,” “reliable,” “sufficient,” and deployment guarantees;
   - invalid consistency-diagnostic conclusions;
   - any runtime-memory/Pareto implication.
7. Consolidate limitations without duplicating Discussion. Explicitly retain:
   - synthetic query/LLM qrels and no human validation;
   - one corpus per language/domain condition;
   - raw non-normalized L2;
   - fixed parameters and no sensitivity analysis;
   - bounded five-model roster and missing alternative baselines;
   - roster-conditional pool;
   - 148 scored versus 150 generated queries;
   - compound single-machine timing;
   - mutable-repository/archival limits;
   - no runtime-memory measurement.
8. Future Work may mention the missing evidence above, but must not imply it was
   completed in this paper.
9. Use “paper,” “practitioner,” and “English-oriented” consistently.

REVIEWER COVERAGE

This batch contributes to R1–R3, M1, M3–M11, MIN12, and MIN13.

QUALITY CHECKS

- Confirm RQ1–RQ4 are answered once each and match intro.tex.
- Search for “p<,” “p=,” “significant,” “dominates,” “universal,” “actionable,”
  “reliable,” “sufficient,” “memory-aware,” “Pareto,” and “monolingual.”
- Confirm Conclusion does not introduce a new result.
- Run:

  powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1

Fix only Conclusion-caused errors.

FINAL RESPONSE

Report:
- exact RQ answers;
- final per-corpus conclusion;
- limitations/future-work changes;
- residual reviewer risks;
- build result.

Do not edit todo.md or another section.
```

---

## Prompt 9 — Global Consistency, Terminology, Tables, Figures, and Citations

```text
You are a cold-start manuscript-audit agent working in:

C:\Codes\RagRetrievalBench

Perform a constrained global consistency and presentation pass. Structural
section rewrites should already be complete.

AUTHORIZED FILES:
- journal_paper/manuscript.tex
- journal_paper/intro.tex
- journal_paper/related.tex
- journal_paper/method.tex
- journal_paper/experiments.tex
- journal_paper/results.tex
- journal_paper/discussion.tex
- journal_paper/conclusion.tex
- journal_paper/refs.bib

Do not edit todo.md, prompts.md, code, configuration, datasets, qrels, raw
results, image files, or generated build files. Do not introduce new substantive
arguments or evidence. Preserve unrelated changes.

Before editing:
1. Read AGENTS.md, todo.md, reviewer.md, and every authorized manuscript source.
2. Verify Prompts 1–8 are complete. If a structural batch is missing, stop and
   report it rather than attempting a broad rewrite.
3. Inspect git diff so the audit preserves prior intentional changes.

AUDIT TASKS

1. Claim consistency:
   - dataset-level reports primary;
   - aggregate report secondary;
   - no universally best model assumed;
   - language/domain important but non-causal;
   - all recommendations bounded to corpus, roster, protocol, metric, priority,
     qrels, and hardware.
2. RQ consistency:
   - exactly RQ1–RQ4;
   - only allowed RQ1/RQ3 wording changes;
   - Results, Discussion, and Conclusion answers match.
3. Numerical consistency:
   - 150 generated queries;
   - 148 scored queries for statistics;
   - 48/50/50 scored distribution;
   - no accidental changes to frozen model scores/timings.
4. Statistical consistency:
   - no bootstrap p-values or significance claims;
   - CIs described as descriptive and snapshot-conditional;
   - no invalid all-metric CV/worst-drop/range claims.
5. Terminology:
   - “English-oriented,” not “monolingual”;
   - “practitioner,” not mixed user/developer terminology;
   - “paper,” not manuscript, in reader-facing prose;
   - remove promotional words listed in MIN12.
6. Metric/aggregation definitions:
   - all six retrieval metrics defined;
   - zero-positive policy disclosed;
   - macro means, average rank, and weighted latency explained;
   - “Positive qrels” label used accurately.
7. Operational boundaries:
   - timing described as compound, single-machine, descriptive;
   - no runtime-memory, Pareto, hard-constraint, or new-output claim.
8. Dataset/provenance:
   - ISO date 2026-01-01;
   - ownership and redistribution wording verified and non-invented.
9. Models:
   - M1–M5 identities visible in central standalone artifacts;
   - five-model roster described as bounded.
10. Tables and figures:
    - every environment has caption and label;
    - labels are unique;
    - every retained artifact is referenced in prose;
    - captions agree with revised text;
    - tabular column specifications match rows;
    - redundant figures are removed/relocated only if already authorized by
      todo.md; do not delete image files.
11. Citations:
    - every cited key exists;
    - every reference supports its nearby claim;
    - bibliography contract remains exact.
12. CAS/source rules:
    - flat journal_paper sources;
    - no nested inputs;
    - mandatory front matter preserved;
    - Discussion included once in the correct position.

LIMITED-AGENT RULE

Make only small consistency, terminology, caption, citation, and formatting
fixes. If a problem requires new evidence, a new experiment, or a major
structural rewrite, do not improvise. Report it as a residual blocker.

QUALITY CHECKS

Run targeted rg searches for:
- monolingual
- language dominates
- domain effect
- language effect
- p<
- p=
- significant
- all-metric
- worst drop
- score range
- consistency penalty
- actionable
- sufficient
- reliable
- memory-aware
- Pareto
- 150 queries
- 148
- 01/01/2026

Interpret results carefully; do not blindly replace text.

Run:

  powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1

Fix all manuscript-source errors within the authorized scope.

FINAL RESPONSE

Report:
- files changed;
- consistency defects fixed;
- remaining blockers requiring evidence or journal selection;
- lint/build result.

Do not edit todo.md or claim final PDF acceptance; Prompt 10 performs that gate.
```

---

## Prompt 10 — Final PDF Verification and `todo.md` Closure

```text
You are the final cold-start verification agent working in:

C:\Codes\RagRetrievalBench

Your role is verification and minimal repair, not another broad rewrite.

AUTHORIZED FILES:
- todo.md
- journal_paper/manuscript.tex
- journal_paper/intro.tex
- journal_paper/related.tex
- journal_paper/method.tex
- journal_paper/experiments.tex
- journal_paper/results.tex
- journal_paper/discussion.tex
- journal_paper/conclusion.tex
- journal_paper/refs.bib

Do not edit prompts.md, pipeline code, configuration, datasets, qrels, raw
results, image files, or generated build files as source. Preserve unrelated
changes.

Before editing:
1. Read AGENTS.md, todo.md, reviewer.md, prompts.md, and every manuscript source
   completely.
2. Inspect git status and diff.
3. Confirm Prompts 1–9 were implemented. If a major stage is missing, do not
   mark its TODO items complete; report the missing stage.

FINAL CONTENT GATES

Verify all of the following:

1. The central thesis is unmistakable:
   a practitioner should not assume one model for every corpus and may make
   different corpus-specific selections.
2. Dataset-level reports are primary; aggregate ranking is secondary.
3. Existing worked outcomes are correct:
   - education_eng → M1 for highest MAP@10 and lowest latency;
   - education_tr/law_tr → M5 quality-first;
   - M3 is the lower-latency Turkish compromise.
4. Language and domain remain important but non-causal.
5. Exactly four RQs remain; only the allowed RQ1/RQ3 edits were made.
6. 150 generated and 148 scored queries are distinguished consistently.
7. No bootstrap p-value/significance claims remain.
8. No invalid all-metric consistency statistic remains.
9. Raw-L2, synthetic-qrels, bounded-roster, fixed-protocol, pool, timing,
   reproducibility, and no-memory limits are explicit.
10. No current-capability claim mentions runtime memory, Pareto analysis, hard
    constraints, human validation, new baselines, or unimplemented outputs.
11. Discussion exists, is included once, and covers practitioner implications,
    language/domain partitioning, prior-work relation, and validity limits.
12. All tables/figures/citations/labels are valid and aligned with prose.
13. All 3 reject, 11 major, and 14 minor reviewer items in todo.md have been
    addressed through manuscript revision or explicitly retained as residual
    risks.

TODO CHECKBOX RULES

Update todo.md only after inspecting direct manuscript evidence:

- Mark a section-level or reviewer checkbox complete when its required writing
  action and evidence-boundary disclosure are present.
- A reviewer item may be marked complete as a manuscript-response task even
  when its “Residual risk” remains high; do not delete or weaken that residual
  risk.
- Do not mark MIN14 complete if no target journal has been specified and its
  journal-specific limits cannot be verified. Leave it unchecked and state the
  blocker.
- Do not mark a final acceptance gate complete unless it was directly verified.
- Do not rewrite the substance of todo.md during closure.

FINAL BUILD

Run:

  powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1 -CompilePdf

Do not report success if lint or compilation fails. Apply only minimal
manuscript-source fixes required to pass the gate.

PDF INSPECTION

Locate the compiled PDF and inspect it for:
- clipped/overflowing tables;
- unreadable figures;
- broken characters;
- unresolved citations or references;
- bad section ordering;
- orphaned captions/headings;
- excessive blank space caused by floats;
- front-matter formatting problems.

Use PDF rendering/inspection tools if available. Do not edit generated build
files directly; fix the TeX source.

FINAL RESPONSE

Report:
- all source files changed in this final pass;
- final checkbox counts and any intentionally unchecked item;
- the status of all 3 reject, 11 major, and 14 minor mappings;
- CAS lint result;
- PDF compilation result and output path;
- visual inspection result;
- residual scientific risks that paper wording cannot eliminate.

Do not claim that residual methodological risks were scientifically resolved.
```

## Expected End State

After Prompt 10:

- the paper consistently presents per-corpus embedding-model selection as its main contribution;
- all four RQs remain;
- language and domain remain important without causal overreach;
- all completed claims match the frozen experiment;
- each reviewer comment has a manuscript response or explicit residual-risk disclosure;
- `todo.md` truthfully reflects completion status; and
- the CAS PDF passes lint, compilation, and visual inspection.
