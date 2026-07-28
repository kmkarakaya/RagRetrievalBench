# Consolidated Editorial and Reviewer Report

**Manuscript:** *A Local RAG Retrieval Benchmarking Pipeline for Corpus-Specific Embedding-Model Selection*
**Author:** Murat Karakaya (TED University)
**Files reviewed:** [manuscript.tex](journal_paper/manuscript.tex), [intro.tex](journal_paper/intro.tex), [related.tex](journal_paper/related.tex), [method.tex](journal_paper/method.tex), [experiments.tex](journal_paper/experiments.tex), [results.tex](journal_paper/results.tex), [discussion.tex](journal_paper/discussion.tex), [conclusion.tex](journal_paper/conclusion.tex), [refs.bib](journal_paper/refs.bib)
**Supporting material inspected:** the public implementation and all frozen run artifacts in the submitting repository.

---

## 0. Editor's decision

**MAJOR REVISION.**

This is a benchmark-*method* paper. I have reviewed it on those terms: the contribution is the reusable,
configuration-driven per-corpus workflow and the artifacts it produces, and the three-corpus snapshot is a
demonstration that the manuscript explicitly and correctly declines to advance as a finding. I have therefore **not**
evaluated the manuscript as if "M5 is the best embedding model" were its claim, and reviewers are asked not to do so
either.

Judged as a tool paper, the submission has a real and useful core. The workflow is coherent, the dataset-isolation
design is sound, model-independent pooling is the right call and is well motivated, and the manuscript is unusually
disciplined about the boundaries of its own evidence — I recorded far fewer overclaims than is typical for this kind of
submission. I also independently recomputed the entire numerical layer against the frozen artifacts and found it clean
(details in §2).

What blocks acceptance is that the paper does not yet demonstrate the three things a tool paper must demonstrate.
**(i) Availability:** the artifacts the paper says are in the public repository are excluded from it by
`.gitignore`, so contributions C1 and C4 cannot currently be inspected by a reader. **(ii) Novelty:** the paper never
states, in any comparable form, what this pipeline does that BEIR/MTEB harnesses, RAGAS, ARES, RAGBench, UMBRELA or the
LangChain/LlamaIndex evaluators do not. **(iii) Internal consistency:** in several places the shipped tool does not
behave the way the Method section describes it, the tool's generated report contradicts the paper, and the tool's own
inline documentation contradicts the paper on retrieval geometry. Separately, the one method-level novelty the paper
does claim — model-independent pooling — is supported by a comparison that changes three variables at once and is
presented as if it changed one.

None of this is fatal. Every item below is fixable, and a substantial fraction is fixable in text alone. The revision I
am asking for is: make the artifact real, say what the tool adds, make the paper and the code agree, and replace the
one uncontrolled comparison with the controlled one that the repository is already half-way to producing.

---

## 1. How this report is organised

Three severity sections, in the order you requested.

| Section                      | Meaning                                                                                                                                                         | Count |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- |
| **§3 Reject-risk**    | Not a rejection in this round. These are the points on which a second reviewer could reasonably vote reject if they are not fully resolved. Treat as mandatory. | 3     |
| **§4 Major revision** | Required for acceptance. Each changes what the paper is entitled to claim, or what the tool actually does.                                                      | 11    |
| **§5 Minor revision** | Correctness, presentation, and bibliography hygiene. Required, but none affects the contribution.                                                               | 22    |

Every point has the same four parts:

- **Problem** — what is wrong, in reviewer voice.
- **Where** — the manuscript location (file, section, table/figure, line).
- **Evidence** — the repository path and the exact numbers or code lines, so you can check the claim rather than take
  it on trust.
- **Fix** — concrete remedy, with ready-to-paste **Proposed replacement text** where the fix is textual.

§6 is a point-to-section index table. §7 lists the short set of changes that would convert this to accept-with-minor.

---

## 2. What I verified, and what the paper gets right

I want this on record, because it is unusual and it should count in the author's favour at the next round.

**The numerical layer is clean.** I recomputed every reported value from `datasets/*/reports/raw_results_*.json`:

- All 30 per-model retrieval values in Tables 10, 12 and 14 (`tbl:education_eng_metrics`, `tbl:education_tr_metrics`,
  `tbl:law_tr_metrics`) match the stored metrics exactly.
- All 15 timing values in Tables 11, 13 and 15 (`tbl:*_timing`) match.
- The macro means in Table 9 (`tbl:cross_dataset_consistency_summary`: 0.2536 / 0.2408 / 0.3051 / 0.2799 / 0.3810)
  recompute correctly, as do the per-dataset means in Table 8 (`tbl:dataset_result_summary`: 0.4534 / 0.2121 / 0.2107).
- Average ranks (3.33 / 3.67 / 3.00 / 3.00 / 2.00) are internally consistent — they sum to 15.00 as they must for five
  models over three datasets.
- Weighted latencies (16.28 / 51.66 / 25.05 / 26.91 / 42.94) reproduce under the stated 48/50/50 scored-query weights.
- Both difference tables (Tables 16 and 17, `tbl:language_effect_comparison` and `tbl:turkish_domain_comparison`) are
  arithmetically correct to four decimals.
- Qrels counts reproduce exactly: 312/1805, 354/3024, 286/3515, i.e. the 9,296 judged pairs stated at
  [results.tex:297](journal_paper/results.tex#L297).

**The seed policy is bit-reproducible.** Re-running `random.seed(42); random.sample(...)` against each frozen
`corpus.jsonl` reproduces all 50 recorded seed-chunk IDs, positionally, for all three corpora, with no duplicates.

**The metric semantics are as documented.** The chain from ChromaDB rankings through
`InformationRetrievalEvaluator.compute_metrics()` into the report tables was traced end to end with no index error, and
the MAP@10 denominator really is `min(|R_q|, 10)` as stated at [experiments.tex:85](journal_paper/experiments.tex#L85).
Zero-positive exclusion is enforced independently in two places, giving the stated 48/50/50 = 148.

**Design choices that are correct and worth keeping.** Per-dataset isolation of corpora, queries, qrels, collections
and reports; model-independent pooling; storing explicit negative judgments rather than discarding them; not
force-labelling the seed chunk relevant; separating the *query generator* and *relevance judge* roles terminologically
and conceptually ([method.tex:47](journal_paper/method.tex#L47)); and the consistently conditional framing of every
ranking claim.

**Two corrections to things a reviewer might wrongly flag.** The `__CAS_CLASS__` token in `\documentclass` is not an
error — the build script substitutes it. And the `1/(1+d)` similarity transform genuinely is rank-preserving, so
reporting similarities rather than distances introduces no distortion by itself.

### Scoring the stated contributions

|     | Contribution / RQ                                                                  | Verdict                                                                                                                                                                                                                                            |
| --- | ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C1  | Repeatable per-corpus benchmark-construction workflow producing reusable artifacts | **Partially met.** The workflow exists and runs; the artifacts are not published (RR1) and the pipeline diverges from the Method description in three places (MJ3, MJ4, MJ9).                                                                |
| C2  | Shared-protocol candidate comparison across one roster                             | **Met.** Verified: same corpus, same queries, same qrels, per-model isolated collections.                                                                                                                                                    |
| C3  | Dataset-level + secondary aggregate reports combining quality and operational cost | **Partially met.** The reports exist, but the generated report misstates the configuration and mislabels its own conclusions (MJ9), and the decision-support layer the paper promises (uncertainty) is absent from the dataset report (MJ1). |
| C4  | Preserved artifacts for inspection and report regeneration                         | **Not met as submitted.** See RR1.                                                                                                                                                                                                           |
| RQ1 | Pipeline utility                                                                   | **Partially answered.** The tool produces the evidence; utility relative to existing tooling is never established (RR2).                                                                                                                     |
| RQ2 | Language sensitivity                                                               | **Answerable only as an illustration.** The two education corpora share no documents and no subject matter (MJ8).                                                                                                                            |
| RQ3 | Domain sensitivity                                                                 | Same limitation; the paper's own hedging is correct but insufficiently specific (MJ8).                                                                                                                                                             |
| RQ4 | Operational decision support                                                       | **Weakly answered.** Latency is a stated decision criterion but is measured without warm-up, once, at the wrong cutoff (MJ7).                                                                                                                |

---

## 3. Reject-risk issues

Three items. My recommendation is major revision, not reject — but each of these is a point on which a second reviewer
could reasonably vote to reject, and I expect all three to be closed in the revision.

### RR1 — The contributed artifacts are not in the public repository

**Problem.** The paper's contributions C1 and C4 are, in the author's own words, to "turn a local document collection
into reusable corpus, query, qrels, ranking, timing, and report artifacts" and to "preserve benchmark artifacts for
inspection and report regeneration". For a tool paper this is the deliverable. As the repository stands, none of those
artifacts is published, so a reader cannot inspect, verify, or reuse the contribution at all.

**Where.** [experiments.tex:137](journal_paper/experiments.tex#L137), the *Available artifacts* row of Table 7
(`tbl:reproducibility`), which
states: "Corpus-derived benchmark artifacts, queries, qrels, raw-result JSON, and reports in the public repository".
Repeated at [method.tex:115](journal_paper/method.tex#L115) and [experiments.tex:114](journal_paper/experiments.tex#L114).

**Evidence.** `.gitignore` line 96 contains `datasets/`. `git ls-files datasets/` returns **zero** tracked files.
Nothing under `datasets/*/corpus.jsonl`, `queries.jsonl`, `qrels.tsv`, `reports/raw_results_*.json` or
`reports/*_benchmark_report_*.md` is in version control. Only `aggregated_reports/`, `results_reanalysis/` and the
`analysis/` scripts are tracked.

A second, compounding finding. The frozen raw-result JSONs were **edited after the run**. The reported run executed
under dataset names `education_eng_rerun`, `education_tr_rerun`, `law_tr_rerun` — this survives in the persisted
ChromaDB collection names inside `chroma.sqlite3` (`education_eng_rerun_coll_v1` …), in the report filenames
(`education_eng_rerun_benchmark_report_2026-07-23_17-51-50.md`), and in
`aggregated_reports/2026-07-23_18-05-12/aggregate_report.md`. The directories were subsequently renamed and the JSONs
hand-edited to `"dataset": "education_eng"` / `"collection_name": "education_eng_coll_v1"`. File modification times
confirm the sequence: the report `.md` is 17:52:34, the co-located `raw_results_...17-51-50.json` is 20:16:38, roughly
two and a half hours later. **I checked whether the edit touched the numbers: it did not** — every metric in the JSON
still reconciles with the report and with the paper. So this is a cosmetic rename, not data alteration. But
[experiments.tex:144](journal_paper/experiments.tex#L144) presents the raw-result JSON as the artifact that "preserves
the essential benchmark record" for "later verification", and that record has in fact been modified post hoc into
disagreement with the index and report filenames sitting beside it.

**Fix.**

1. Publish the artifacts. Either track `datasets/*/corpus.jsonl`, `queries.jsonl`, `qrels.tsv`,
   `reports/raw_results_*.json` and `reports/*_benchmark_report_*.md` (removing the blanket `datasets/` ignore and
   replacing it with targeted ignores for `pdfs/` and `chromadb_collections/`), or ship them as a release asset. Do not
   publish the source PDFs if redistribution is unclear — the derived chunk text, queries and qrels are what a reader
   needs, and [experiments.tex:41](journal_paper/experiments.tex#L41) already handles the licensing caveat correctly.
2. Regenerate the frozen run cleanly under the final dataset names so that the JSON, the ChromaDB collection names and
   the report filenames agree. If a regeneration is not possible, disclose the rename explicitly.
3. Mint an immutable archive. A Zenodo deposit of the artifact bundle with a DOI, plus a matching git tag, converts
   this from a claim into a fact and simultaneously closes the paper's own "no DOI-backed archival record" caveat at
   [experiments.tex:114](journal_paper/experiments.tex#L114).

**Proposed replacement text** — Table 7 (`tbl:reproducibility`), *Available artifacts* row:

```latex
Available artifacts & Chunked corpora, generated queries, LLM-judged qrels (positive and negative labels),
per-model ranking files, raw-result JSON, and generated dataset and aggregate reports, archived at
\texttt{<DOI>} and mirrored in the public repository \citep{GitHub_RagRetrievalBench}. Source PDFs are not
redistributed; see Section~\ref{dataset-provenance}. Persisted vector indexes are excluded for size and can be
rebuilt from the chunked corpora. \\
```

---

### RR2 — The novelty of the workflow is asserted but never demonstrated

**Problem.** The paper's identity is "an integrated local benchmark workflow rather than a new embedding algorithm,
retrieval metric, or general-purpose leaderboard" ([discussion.tex:19](journal_paper/discussion.tex#L19)). I accept
that framing. But it makes one question decisive, and the manuscript never answers it: *what does this pipeline do that
a practitioner could not already do with existing tooling?* Section 2 surveys prior work at length and ends in a gap
statement, yet the gap is argued entirely from what prior *studies* did, never from what prior *tools* can and cannot
do. A reader who already uses `ir_measures` + `ir_datasets`, or RAGAS, or the BEIR evaluation harness, finishes the
paper without knowing whether they should adopt this.

**Where.** [related.tex:25-29](journal_paper/related.tex#L25) (§2.5 Gap Statement and Positioning);
[intro.tex:12](journal_paper/intro.tex#L12) (Contributions); [discussion.tex:19-21](journal_paper/discussion.tex#L19).

**Evidence.** There is no comparison table anywhere in the manuscript — I searched all seven section files. The named
comparators in §2 (BEIR, MTEB, RAGBench, ReproRAG, RAGOps) are discussed as *studies*. RAGAS, ARES, UMBRELA,
`ir_measures`/`ir_datasets`, and the LangChain/LlamaIndex retrieval evaluators — the tools a practitioner would
actually reach for — are not mentioned at all.

**Fix — RESOLVED IN REVISION (prose, not a table).** A capability-comparison table was considered and rejected in
favour of prose: a table in which the new tool wins every row is not credible, and the distinction here is about what
each tool *presupposes*, which is an argument rather than a checklist. Implemented as a new
`\subsection{Relation to General-Purpose Evaluation Tooling}\label{rw-tooling}` in
[related.tex](journal_paper/related.tex), placed after §2.4 and before the Gap Statement, in two paragraphs:

- **Paragraph 1** groups the landscape into four families and states what each presupposes. Shared testbeds (BEIR,
  MTEB, MMTEB) supply corpus, queries and judgments together, and their harnesses accept a local collection only once
  it is already accompanied by a query file and a qrels file — with unjudged pairs then treated as non-relevant by
  convention, which ties back to the paper's own pooling argument in §2.2. Evaluation and dataset libraries
  (`ir_datasets`, `ir_measures`, the Sentence-Transformers `InformationRetrievalEvaluator`) and reproducible retrieval
  toolkits (Pyserini) *consume* a labeled benchmark rather than producing one. UMBRELA supplies a judge component but
  not the corpus-to-report workflow. RAG frameworks (RAGAS, ARES, RAGBench) score an assembled generation pipeline on
  context relevance, faithfulness and answer relevance.
- **Paragraph 2** states the contribution as a composition, says plainly that no individual stage is new and that the
  metric layer is delegated to an existing implementation, then names the four choices the pipeline fixes which the
  generic tools leave open (model-independent pooling across the roster; negatives retained; one frozen protocol over
  isolated per-model indexes; quality reported together with measured operational cost). It closes by positioning the
  pipeline *upstream of* the answer-quality frameworks rather than in competition with them.

Two accuracy constraints were enforced while drafting, because the argument fails if either is overstated. **RAGAS does
generate evaluation data from supplied documents** (`TestsetGenerator`), so the revision does not claim otherwise; the
stated difference is that its items pair a question with the contexts that produced it — a seed-as-positive convention
serving answer-quality measurement — rather than pooled, judged relevance over the full chunk set. And the revision
notes that the pipeline's artifacts are written in a BEIR-style corpus/queries/qrels layout, so a benchmark built here
can be re-scored with external tooling; that is a checkable interoperability claim rather than a competitive one.

Supporting edits made in the same pass: the §2 opening sentence now announces the tooling discussion; the Gap Statement
goes from four gaps to five with the tooling gap added; [discussion.tex](journal_paper/discussion.tex) §6.3 gains one
sentence pointing to `rw-tooling`; and the first contribution in [intro.tex](journal_paper/intro.tex) now says the
workflow takes an unlabeled collection as input rather than presupposing a labeled benchmark. Ten verified bibliography
entries were added (`es2024ragas`, `saadfalcon2024ares`, `reimers2019sentencebert`, `macavaney2021irdatasets`,
`macavaney2022irmeasures`, `lin2021pyserini`, `upadhyay2024umbrela`, `enevoldsen2025mmteb`, `langchain2026`,
`llamaindex2026`), and `Thakur_BEIR_2021` was corrected to the NeurIPS Datasets and Benchmarks Track form.

---

### RR3 — The pooling robustness check is not a controlled comparison

**Problem.** Model-independent pooling is the paper's one method-level novelty claim, and §5.8 is the evidence offered
for it. But the comparison it reports changes at least three variables simultaneously and attributes the entire result
to one of them. This is, precisely, the failure mode the Introduction criticises in ad hoc trials: "ad hoc trials can
change multiple protocol variables at once" ([intro.tex:5](journal_paper/intro.tex#L5)). It is the most serious
methodological overstatement in the manuscript, and it sits on the paper's own novelty claim.

**Where.** [results.tex:295-313](journal_paper/results.tex#L295), §5.8 "Robustness to Candidate-Pool Construction" and
Table 20 (`tbl:pooled_survival`). Also referenced at [experiments.tex:133](journal_paper/experiments.tex#L133)
(Table 7, *Candidate pool* row)
and [related.tex:15](journal_paper/related.tex#L15).

**Evidence.** The "single-model (M5-only) pool" row of Table 20 (0.486 / 0.428 / 0.330 / 0.279 / 0.263) is the
2026-03-05 run preserved in `backup_frozen_2026-07-23/`. I recomputed its macro means from
`backup_frozen_2026-07-23/datasets/*/reports/raw_results_2026-03-05_*.json` as 0.4857 / 0.4281 / 0.3299 / 0.2789 /
0.2631 — an exact match to the paper's row. So the provenance is confirmed. That run differs from the frozen July run
in three ways at once:

1. **Pool source** — M5-only vs. five-model union. This is the variable the paper intends to isolate.
2. **Seed-forcing policy** — the March qrels force the seed chunk positive. In all three
   `backup_frozen_2026-07-23/datasets/*/qrels.tsv` the seed chunk is a positive for **50/50** queries and there are
   **zero** zero-positive queries; `analysis/qrels_reconstruction_summary.json` records
   `"forced_source_positives": 50` for each corpus. The July run judges the seed like any other candidate.
3. **A completely different query set.** Comparing `queries.jsonl` between the backup and the current snapshot:

   | dataset       | old n | new n | shared`query_id` | identical query text |
   | ------------- | ----- | ----- | ------------------ | -------------------- |
   | education_eng | 50    | 50    | **0**        | 3                    |
   | education_tr  | 50    | 50    | **0**        | 4                    |
   | law_tr        | 50    | 50    | **0**        | 2                    |

   The `corpus.jsonl` doc-id sets are identical across both runs (572 / 619 / 723), so it is the same corpus with an
   entirely disjoint seed sample. The cause is visible in the configs: the March run has no `random_seed` key at all
   (the key was introduced later), so its sampling was unseeded.

Given this, [results.tex:299](journal_paper/results.tex#L299) — "the model-independent pool surfaces substantially more
relevant chunks than the single-model pool — 312 versus 215 positives on `education_eng` … so restricting candidate
generation to one model under-covers relevance" — is not identified. Part of the 312-vs-215 gap is pooling; part is the
forced-vs-judged seed change; part is 50 different queries. Likewise the ranking-stability finding compares two
different experiments rather than two pool constructions.

**Fix.** Run the controlled version. It is cheap and the repository is already most of the way there:
`analysis/pooled_qrels.py` builds the union from the persisted per-model ranking files
(`datasets/*/analysis/rankings_M*.jsonl`). Restricting that construction to `rankings_M5.jsonl` alone yields an M5-only
candidate set over the **same queries** with the **same LLM judgments** already stored in `qrels.tsv` — every pair in
the M5-only pool is a subset of pairs already judged, so no new LLM calls are needed. Rescore the frozen rankings
against that subset. That isolates variable (1) exactly.

While you are there, add the leave-one-model-out version, which is the diagnostic a TREC-trained reviewer will ask for:
for each model *X*, rebuild the pool from the other four, rescore *X*, and report how much *X* loses. That directly
bounds the roster-conditionality the paper concedes at [discussion.tex:25](journal_paper/discussion.tex#L25).

If you prefer not to run anything, the *minimum* acceptable revision is to stop calling this a pool-construction
comparison and to disclose all three differences. But I would push hard for the controlled run: it is a subset
operation on data you already have, it costs no API budget, and it converts your weakest section into direct support
for your novelty claim.

**Proposed replacement text** — §5.8, replacing the current second paragraph and the Table 20 caption, assuming the
controlled ablation is run:

```latex
To isolate the effect of pool construction, we hold the frozen query set, the frozen LLM judgments, and the frozen
per-model rankings fixed, and restrict the candidate pool to the top-20 retrieved by \texttt{M5} alone. Because
every pair in the restricted pool was already judged during the model-independent construction, this is a strict
subset of the same relevance resource and requires no additional judging; the only variable that changes is which
retriever generated the candidates. Under this controlled comparison, the model-independent pool yields
<X> versus <Y> positives on \texttt{education\_eng}, <X> versus <Y> on \texttt{education\_tr}, and <X> versus <Y>
on \texttt{law\_tr}, and the aggregate ordering is <stable / changes as follows>. Table~\ref{tbl:pooled_survival}
reports both constructions.

An earlier snapshot of this study used a single-model pool together with a forced-relevant seed chunk and a
different generated query set. We do not use it as a pool-construction comparison, because those three factors
vary together and the pooling effect is not separately identified; it is reported in
Appendix~\ref{app:earlier-snapshot} only as a record of how the protocol evolved.
```

And Table 20's caption must lose the phrase "The tested ordering is unchanged; only absolute scores differ" unless the
controlled run supports it.

---

## 4. Major revision

### MJ1 — The decision-support layer is computed at the wrong level

**Problem.** RQ1 promises "query-level uncertainty estimates" as part of the per-corpus evidence, RQ4 promises to
"combine retrieval effectiveness, operational cost, and query-level uncertainty" into guidance, and
[discussion.tex:5](journal_paper/discussion.tex#L5) states that the practitioner "should read the benchmark output at
the corpus level before considering any aggregate summary". But §5.7 reports confidence intervals **only for the
aggregate** — the layer the paper itself repeatedly labels *secondary*. The uncertainty layer is therefore absent from
the artifact the paper designates as primary. This is a gap in the *pipeline*, not a complaint about the rankings: the
dataset-level report does not carry the uncertainty the paper says it carries.

It matters concretely, because the per-corpus intervals already exist in the repository and they change how the
per-corpus reports should be read.

**Where.** [results.tex:266-293](journal_paper/results.tex#L266) (§5.7); RQ1 and RQ4 at
[intro.tex:21,27](journal_paper/intro.tex#L21); [conclusion.tex:5,9](journal_paper/conclusion.tex#L5).

**Evidence.** `results_reanalysis/bootstrap_frozen.json` already contains per-dataset percentile bootstrap intervals
for every model and metric, at *B* = 10,000. For MAP@10, the top two candidates on each corpus:

| corpus        | leader                  | runner-up               |
| ------------- | ----------------------- | ----------------------- |
| education_eng | M1 0.526 [0.458, 0.592] | M2 0.502 [0.431, 0.573] |
| education_tr  | M5 0.361 [0.294, 0.430] | M3 0.297 [0.232, 0.364] |
| law_tr        | M5 0.358 [0.278, 0.445] | M3 0.262 [0.198, 0.331] |

On all three corpora the leader's interval overlaps the runner-up's. That is not a defect in the result — it is exactly
the kind of information a decision-support tool exists to surface, and withholding it from the per-corpus report while
publishing it for the aggregate is the wrong way round.

Three further statistical points in the same section:

- **The bootstrap is not stratified by dataset.** `analysis/bootstrap_ci.py` concatenates per-query MAP values across
  the three corpora into one flat length-148 vector and resamples uniformly from it. A single resample can therefore
  contain, say, 60 `law_tr` and 40 `education_eng` queries. Given the very large between-corpus heterogeneity (M1:
  0.526 / 0.123 / 0.112), dataset-composition variation is folded into the interval width.
  [results.tex:268](journal_paper/results.tex#L268) correctly flags that queries are "nested within only three
  datasets", but does not say that the resampling ignores the nesting.
- **Two different estimators are labelled identically one page apart.** Table 19 (`tbl:bootstrap_ci`) reports the
  *pooled-over-148* mean (M1 0.250, M2 0.237); Table 20 (`tbl:pooled_survival`) reports the *macro mean over three
  corpora* (M1 0.254, M2 0.241). Both are correct and
  [experiments.tex:87](journal_paper/experiments.tex#L87) does define the macro mean, but neither table says which one
  it uses and both are called "aggregate MAP@10".
- **Four paired comparisons against M5 with no multiplicity statement.** Given that the section is explicitly
  descriptive, one sentence acknowledging this is enough; no correction is required.

**Fix.**

1. Add a per-corpus interval table (or interval columns on the existing Tables 10, 12, 14) and make the dataset-level
   report emit it. This is a small change to `analysis/bootstrap_ci.py` / `plot_bootstrap_forest.py`, both of which
   already compute per-dataset intervals.
2. Add a per-corpus *paired* interval for the leader minus the runner-up. Paired at the query level is the right test
   and `bootstrap_ci.py` already does the pairing correctly for the aggregate.
3. Rewrite the corpus readings so the tie is broken on the operational axis rather than on quality. This is a
   *stronger* version of the paper's own argument, not a retreat from it: the point of RQ4 is that operational cost
   matters, and the honest reading is that on `education_eng` quality does not separate the top candidates but latency
   does, by a factor of three.
4. Stratify the aggregate bootstrap by dataset, or state explicitly that it is unstratified and what that does to the
   intervals.
5. Label the two estimators distinctly.

**Proposed replacement text** — [results.tex:53](journal_paper/results.tex#L53), the `education_eng` reading:

```latex
Table~\ref{tbl:education_eng_timing} completes the practical reading. On retrieval quality, \texttt{M1} and
\texttt{M2} are not separated by this benchmark: their \texttt{MAP@10} values are 0.5260 and 0.5022, and their
per-corpus bootstrap intervals over the 48 scored queries overlap substantially
(Table~\ref{tbl:education_eng_ci}). What does separate them is operational cost: \texttt{M1} answers a query in
13.10~ms against 42.62~ms for \texttt{M2}, and indexes the corpus at 51.3 against 7.7 chunks/s. For this corpus
and this priority set the report therefore points to \texttt{M1}---not because it is measurably more effective,
but because it is statistically indistinguishable in effectiveness at roughly one third of the latency.
\texttt{M4} is a further low-latency alternative at slightly lower measured quality (0.4587 at 24.31~ms/query).
This is the pattern the pipeline is designed to expose: when the quality evidence does not discriminate, the
operational evidence decides.
```

Mirror the same correction in [discussion.tex:5](journal_paper/discussion.tex#L5) and
[conclusion.tex:9](journal_paper/conclusion.tex#L9), both of which currently say "highest-`MAP@10` and lowest-latency
candidate" as though the quality claim were established.

**Proposed new table** — insert after Table 10 (`tbl:education_eng_metrics`):

```latex
\begin{table}[t]
\caption{Per-corpus descriptive bootstrap intervals for \texttt{MAP@10} on \texttt{education\_eng}
($n=48$ scored queries, $B=10{,}000$ percentile bootstrap), with paired differences against the
\texttt{MAP@10}-leading candidate. Intervals are descriptive and snapshot-conditional.}\label{tbl:education_eng_ci}
\centering
\small
\begin{tabular}{@{}lcc@{}}
\toprule
Model & \texttt{MAP@10} [95\% CI] & \texttt{M1}$-$model $\Delta$ [95\% CI] \\
\midrule
M1 & 0.526 [0.458, 0.592] & --- \\
M2 & 0.502 [0.431, 0.573] & \textit{(paired interval)} \\
M4 & 0.459 [0.398, 0.521] & \textit{(paired interval)} \\
M5 & 0.425 [0.344, 0.508] & \textit{(paired interval)} \\
M3 & 0.356 [0.286, 0.431] & \textit{(paired interval)} \\
\bottomrule
\end{tabular}
\end{table}
```

The point-estimate and interval columns are taken directly from `results_reanalysis/bootstrap_frozen.json`; only the
paired column needs to be computed. Add the equivalent tables for the two Turkish corpora.

---

### MJ2 — Retrieval geometry is a tool-default defect, and the code contradicts the paper about it

**Problem.** The paper handles the raw-L2 configuration honestly as a limitation. My concern is different and is about
the tool, not the snapshot: the pipeline **ships** a default geometry that contradicts the model cards of every model in
its own default roster, and the code's inline documentation asserts something about that geometry which the paper
correctly refuses to assert. A practitioner who adopts this tool inherits the misconfiguration silently.

**Where.** [experiments.tex:59](journal_paper/experiments.tex#L59) and the *Vector store* / *Embeddings* rows of
Table 7 (`tbl:reproducibility`); [discussion.tex:27](journal_paper/discussion.tex#L27).

**Evidence.**

- `config.py:121` sets `hnsw_space = "l2"`.
- `normalize_embeddings` is never set anywhere in the repository. Chroma's sentence-transformer embedding function
  defaults it to `False`, and this is confirmed in the persisted collection configuration of **all 15** collections:
  `{"vector_index":{"hnsw":{"space":"l2"}}, "embedding_function":{"config":{..., "normalize_embeddings": false}}}`.
- All five rostered models are `sentence-transformers/*` models documented for cosine similarity.
- `config.py:117-119` carries this comment: *"Ranking-based metrics are invariant to the monotonic similarity=1/(1+d)
  transform, so 'l2' and 'cosine' typically produce the same ordering."* The first clause is true; the second does not
  follow from it and is false for non-normalized vectors, where squared-L2 ordering depends on embedding norm and
  cosine ordering does not. The paper says the opposite and says it correctly:
  [experiments.tex:59](journal_paper/experiments.tex#L59) — "the paper does not assume that cosine retrieval would
  preserve the same ordering for non-normalized vectors." Paper and code disagree, and the code is wrong.

**Fix.**

1. Correct or delete the `config.py:117-119` comment — it is the kind of thing a reviewer who opens the repository will
   find in ninety seconds, and it undermines the manuscript's careful handling of the same issue.
2. Change the shipped default to `hnsw_space = "cosine"` (or set `normalize_embeddings=True`), and add a startup
   validation warning when a roster of cosine-trained models is combined with a non-cosine space. A decision-support
   tool should not silently default to a geometry its own default roster was not trained for.
3. Rerun the demonstration under cosine and report both geometries. From the frozen timings, corpus embedding costs
   11–207 s per model-corpus, so a full five-model three-corpus re-index is well under an hour of CPU and needs no LLM
   calls — the queries and qrels are frozen and reusable. Reporting L2 and cosine side by side would simultaneously
   close this point and give the paper the sensitivity evidence it currently lacks (MJ6). Presented as "the pipeline's
   first worked sensitivity study", it becomes a contribution rather than a concession.

If the rerun is genuinely out of scope, the minimum is items 1 and 2 plus a sentence in
[discussion.tex:27](journal_paper/discussion.tex#L27) stating that the shipped default has been corrected for future
users even though the reported snapshot predates the correction.

---

### MJ3 — The two execution modes do not run the same benchmark logic

**Problem.** The paper offers dual execution (interactive and batch) as a design feature and states that the two are
equivalent. They are not: the query-generation prompt differs between them, and the reported snapshot was produced by
the mode with the weaker prompt. Since the generated queries define the entire benchmark, this is a substantive
inconsistency between the described method and the shipped tool.

**Where.** [experiments.tex:83](journal_paper/experiments.tex#L83): "This dual execution design preserves the same
benchmark logic while allowing the execution mode to be adapted to dataset size, budget, or turnaround constraints."

**Evidence.** Both modes share the same system instruction (`config.py:192-199`), but the user message differs:

- interactive — `rag_benchmark.py:270`:
  `f"Generate a search query for the following document:\n\n{corpus[seed_id]}\n\nQuery:"`
- batch — `rag_benchmark.py:259`: the seed chunk is passed as the request body with **no instruction wrapper**.

The frozen batch-request files (`datasets/*/reports/batches/batch_req_query_gen_*.jsonl`) confirm the snapshot was
generated in batch mode, i.e. from the bare chunk.

**Fix.** Unify the two user prompts in the code, and correct the sentence. If the snapshot is not regenerated, say
which mode produced it.

**Proposed replacement text** — [experiments.tex:83](journal_paper/experiments.tex#L83), final sentence:

```latex
The two modes share the same system instruction, seed sample, candidate-pool construction, and judging protocol;
the reported snapshot was produced in batch mode. Because the execution mode determines only how requests are
submitted and collected, it is recorded in the run configuration so that any benchmark can be traced to the mode
that produced it \citep{GitHub_RagRetrievalBench}.
```

---

### MJ4 — The prompts define the ground truth, are absent from the paper, and the judge instruction contradicts itself

**Problem.** Every relevance label in this benchmark is produced by one prompt, and every query by another. They are
the most load-bearing methodological detail in the paper and they appear nowhere in it. Worse, the judging instruction
gives the model two incompatible criteria in adjacent sentences, and the judging pipeline silently converts failures
into negative labels.

**Where.** [method.tex:53,55](journal_paper/method.tex#L53) (steps 2 and 4);
[experiments.tex:83](journal_paper/experiments.tex#L83); [results.tex:319](journal_paper/results.tex#L319).

**Evidence.**

- The judge system instruction (`config.py:201-215`, byte-identical to the frozen batch-request files) says: *"Your
  task is to determine if the excerpt **fully answers** the question"* and then, three lines later, *"1 means it does
  have the **complete or partial** information."* These are different thresholds. With 952 positives out of 9,296
  pairs the model evidently applied the looser reading, but the instruction is ambiguous and there is no agreement
  study to bound the consequence.
- The judge sees **one candidate at a time**, with no other candidates for calibration and **without the seed chunk**
  as a reference. User message: `f"Question: {query_text}\n{i+1}. [{doc_id}] \"{text}\"\n\n"`.
- The `{i+1}.` enumeration is vestigial from a list-style prompt. Each request contains one item, so the index is a
  meaningless integer varying from 1 to 69 across otherwise identical judging tasks — uncontrolled prompt noise.
- **Parse failures become negatives.** `parse_relevance_score` (`rag_benchmark.py:98-114`) returns 0 on any parse
  failure, `utils/llm.py:43-66` has no retry logic, and no artifact records a failure count. "Judged non-relevant" and
  "never successfully judged" are therefore indistinguishable in the released qrels.

**Fix.**

1. Add an appendix with both prompts verbatim, the model ID, the temperature, and the request structure. This is
   non-negotiable for a paper whose ground truth is LLM-produced.
2. Repair the judge instruction to state one criterion. Given the observed behaviour, "partial information counts as
   relevant" is the criterion actually applied, so say that and drop "fully answers".
3. Remove the vestigial `{i+1}.` index.
4. Log parse failures and API failures per run, emit the count into the raw-result JSON, add retry, and record
   unjudged pairs as a distinct third state rather than as negatives.
5. Add the human-validation study the paper repeatedly identifies as its own biggest gap
   ([discussion.tex:25](journal_paper/discussion.tex#L25), [conclusion.tex:11](journal_paper/conclusion.tex#L11)). A
   stratified sample of ~200 judged pairs across the three corpora, balanced positive/negative, two independent
   annotators, reporting Cohen's κ and the judge's per-class precision and recall, plus ~50 queries rated for realism,
   is roughly a day of work and would convert the paper's weakest point into a genuine result. Since generator and
   judge are the same model family, also run a second judge from a different family on the same sample and report
   agreement — that bounds the self-preference concern directly.

**Proposed replacement text** — new appendix stub:

```latex
\appendix
\section{Query-Generation and Relevance-Judging Prompts}\label{app:prompts}

All queries and relevance labels in the reported snapshot were produced by \texttt{gemini-2.5-flash-lite} at
temperature 0.1. The query generator receives one seed chunk and returns one query; the relevance judge receives
one query--candidate pair and returns a binary label. The judge does not see the seed chunk, the other candidates,
or any model identity. Both prompts are reproduced verbatim below and are also stored with the released
configuration \citep{GitHub_RagRetrievalBench}.

\subsection*{Query generator (system instruction)}
\begin{verbatim}
<paste config.py QUERY_GENERATION_SYSTEM_INSTRUCTION verbatim>
\end{verbatim}

\subsection*{Relevance judge (system instruction)}
\begin{verbatim}
<paste the corrected single-criterion judging instruction verbatim>
\end{verbatim}
```

---

### MJ5 — Pool incompleteness is undisclosed where it is measurable

**Problem.** The paper concedes pool incompleteness in general terms three times. It does not report the one number it
has that makes the concession concrete and checkable: how often the pool missed the chunk that is known *a priori* to
be on-point, namely the chunk that generated the query.

**Where.** [method.tex:59](journal_paper/method.tex#L59): "relevant chunks missed by all pooled retrievers can remain
unjudged"; [discussion.tex:25](journal_paper/discussion.tex#L25); [related.tex:15](journal_paper/related.tex#L15).

**Evidence.** Measured against the frozen `qrels.tsv` and `queries.jsonl`:

| corpus          | seed chunk never entered the pool | seed judged non-relevant | zero-positive queries |
| --------------- | --------------------------------- | ------------------------ | --------------------- |
| education_eng   | 0                                 | 3                        | 2                     |
| education_tr    | 4                                 | 2                        | 0                     |
| law_tr          | 5                                 | 1                        | 0                     |
| **total** | **9 / 150**                 | **6 / 150**        | **2 / 150**     |

For 9 of 150 queries, no model retrieved the query's own source chunk in its top-20, so that chunk was never presented
to the judge at all. This is a much sharper statement about pool coverage than the current prose, and it is favourable
to the paper's argument — it is direct evidence that a single-retriever pool would be worse still.

Also worth stating: the seed chunk is judged relevant for 47/50, 44/50 and 44/50 queries respectively. So although
`force_source_chunk_relevant` is correctly `false`, the seed is *de facto* a positive about 90% of the time. That is
fine, but a reader should be told, because [results.tex:319](journal_paper/results.tex#L319) currently emphasises only
that the forced-seed bias was removed.

**Fix.** Report both numbers in §5.9 and add standard pool diagnostics as pipeline outputs: per-model unique
contribution to the pool, pool-depth sensitivity (rescore at depth 5, 10, 20 from the already-judged pairs — no new
judging needed), and leave-one-model-out coverage (see RR3). Consider adding **bpref**, which is designed for exactly
this situation; all six reported measures are among those shown to be non-robust under incomplete judgments.

**Proposed replacement text** — [results.tex:319](journal_paper/results.tex#L319), first observation:

```latex
First, each query's seed chunk is judged like any other candidate rather than force-labeled relevant. This removes
the guaranteed-positive bias of a forced-seed protocol, and is reflected in a high but no-longer-saturated
\texttt{Success@10} on \texttt{education\_eng} (about 0.96 across models rather than 1.00). Two consequences are
worth reporting explicitly. The seed chunk is nevertheless judged relevant for 47, 44, and 44 of the 50 queries in
\texttt{education\_eng}, \texttt{education\_tr}, and \texttt{law\_tr} respectively, so it usually is a positive
even without forcing. Conversely, for 9 of the 150 queries (0, 4, and 5 respectively) no evaluated model retrieved
the seed chunk within its top-20, so the chunk that generated the query never entered the candidate pool and was
never judged. This is a direct, if bounded, measurement of pool incompleteness within the evaluated roster
\citep{zobel1998reliable,buckley2004retrieval}.
```

---

### MJ6 — No sensitivity run, although configurability is the first contribution

**Problem.** The paper's selling point is a configurable pipeline. [intro.tex:32](journal_paper/intro.tex#L32) lists
thirteen configurable dimensions and Table 5 (`tbl:experiment_workflow_parameters`) fixes eight parameters. Not one of
them is varied. The manuscript is
honest about this ([experiments.tex:61](journal_paper/experiments.tex#L61),
[discussion.tex:27](journal_paper/discussion.tex#L27): "functional configurability is not evidence that the reported
rankings are robust to those alternatives"), but honesty does not substitute for the evidence. A configurable tool
whose configurability is never exercised has not been shown to be useful *as* a configurable tool — which is RQ1.

**Where.** [intro.tex:32](journal_paper/intro.tex#L32); [experiments.tex:61](journal_paper/experiments.tex#L61) and
Table 5; [discussion.tex:7,27](journal_paper/discussion.tex#L7).

**Fix.** One minimal sweep on one corpus is enough to demonstrate the capability. Suggested: `education_eng`, a
2 × 2 × 2 over chunk size (500 / 1000) × retrieval cutoff (5 / 10) × pool depth (10 / 20), reported as a rank-stability
table using Kendall's τ against the frozen ordering. Note that the cutoff and pool-depth arms need no re-embedding and
no new judging — they are rescoring operations over the existing rankings and qrels. Only the chunk-size arm requires
re-indexing and re-judging.

Combining this with the cosine arm from MJ2 gives a single new subsection, "Worked sensitivity example", that closes
two major points at once and directly evidences RQ1.

---

### MJ7 — Timing is a headline tool output and is not measured soundly

**Problem.** Latency and throughput are decision criteria in every corpus-level reading and in RQ4. The measurement
procedure behind them has no warm-up, runs once, is taken at a retrieval depth different from the evaluation cutoff,
and produces numbers that do not scale coherently across corpora for one of the five models. The manuscript discloses
the single-run limitation, which is good, but disclosure does not make an unreplicated measurement adequate for a
criterion the paper uses to break ties.

**Where.** [method.tex:81](journal_paper/method.tex#L81); [experiments.tex:116](journal_paper/experiments.tex#L116) and
the *Timing scope* row of Table 7 (`tbl:reproducibility`); Tables 11, 13, 15, 18 and Figure 10
(`fig:results_quality_speed_tradeoff`).

**Evidence.**

- **No warm-up exists anywhere in the repository.** The first timed query therefore absorbs Torch/BLAS first-forward
  initialisation and HNSW segment load, and it does so differently per model. With only 48–50 queries averaged, the
  warm-up share is unquantified and is proportionally largest for the fastest model — precisely the one the paper
  recommends on `education_eng`.
- **The timers are correctly scoped otherwise.** I verified that model loading is *outside* both timers and that the
  query timer genuinely includes query embedding plus search, matching the paper. But the code's own comments say the
  opposite: `utils/chromadb_utils.py:191` reads "DB retrieval only: collection.query call" and `:268` prints
  "Avg Retrieval Latency@query (DB only)". The paper is right and the code comments are wrong; a reader who opens the
  repository will hit the contradiction.
- **Latency is measured at `n_results=100`**, not at the evaluation cutoff `k=10` (`utils/chromadb_utils.py:208`). The
  reported per-query latency is therefore not the latency of the configuration being evaluated.
- **`document_batch_size = 32` does not set the encode batch size.** It sets the `collection.add` chunk count; the
  sentence-transformer `encode` call receives no `batch_size` argument and falls back to its own default, which happens
  also to be 32. So [experiments.tex:128](journal_paper/experiments.tex#L128) is true only by coincidence.
- **The frozen numbers do not scale coherently for M2.** Throughput across corpora of 572 / 619 / 723 chunks:

  | model | education_eng | education_tr  | law_tr        | change          |
  | ----- | ------------- | ------------- | ------------- | --------------- |
  | M1    | 51.3          | 43.5          | 42.3          | −18%           |
  | M2    | **7.7** | **3.6** | **3.5** | **−55%** |
  | M3    | 44.1          | 41.3          | 41.4          | −6%            |
  | M4    | 43.2          | 41.9          | 42.1          | −3%            |
  | M5    | 13.9          | 13.3          | 13.5          | −3%            |

  Query latency shows the same signature: M2 goes 42.62 → 49.86 → 62.14 ms while M5, the other 768-dimensional model,
  goes 41.07 → 42.72 → 44.95 ms. Two explanations are plausible and the paper distinguishes neither. Either the M2 runs
  were contaminated by machine load — which single-run timing cannot rule out — or Turkish text tokenises into far more
  subwords under `all-mpnet`'s English vocabulary, pushing sequences toward its 384-token limit while the MiniLM models
  truncate at 256 and the multilingual XLM-R tokeniser handles Turkish efficiently. **If it is the second, it is a
  genuinely valuable practitioner finding that your tool is uniquely positioned to surface**, and it belongs in the
  paper rather than being left as an unexplained anomaly in Table 18 (`tbl:quality_speed_summary`).

**Fix.**

1. Add a warm-up pass (discard the first *n* queries and one embedding batch) and repeat the timing ≥5 times; report
   median and interquartile range rather than a single mean.
2. Measure query latency at the evaluation cutoff `k=10`.
3. Split the compound timers into embed / insert and embed / search components — the paper already flags the
   compounding as a limitation, and separating them removes the limitation rather than restating it.
4. Fix the misleading code comments at `utils/chromadb_utils.py:191,268`, and either wire `document_batch_size` into
   the `encode` call or rename it to `insert_batch_size` and correct Table 7.
5. Add mean subword-token count per chunk, per model, per corpus to the emitted statistics, and use it to test the
   tokenisation hypothesis for M2. This is cheap — it is one tokeniser pass over each corpus.
6. Put the CPU model, RAM, thread count and OS in the paper body. Table 7 currently defers entirely to the JSON
   environment snapshot; the reader should not have to open an artifact to learn the hardware behind a decision
   criterion.

---

### MJ8 — RQ2 and RQ3 rest on corpora that are not comparable, and the paper under-discloses how

**Problem.** The manuscript already states that language and domain are confounded with corpus identity. That
disclosure is correct but too weak, because it leaves the reader believing the two education corpora are the same kind
of material in two languages. They are not: they share no documents and, more importantly, no subject matter. And RQ2
and RQ3 as phrased ("can the pipeline expose …") are trivially answerable yes, so they do not carry the weight the
Results sections put on them.

**Where.** [results.tex:187-210](journal_paper/results.tex#L187) (§5.5) and
[results.tex:212-233](journal_paper/results.tex#L212) (§5.6); RQ2/RQ3 at
[intro.tex:23,25](journal_paper/intro.tex#L23); [conclusion.tex:7](journal_paper/conclusion.tex#L7);
Table 4 (Dataset Provenance).

**Evidence.** The document sets:

- `education_eng`: Admission, Barriers, Certificates, Council, Directive, DoubleMajor, English, Exams, Graduate,
  Integrity, Internship, Leave, Medical, Minor, mobility, Online, PartTime, Ranking, Rules, Scholarship, Social,
  Societies, Staff, Studies, Traineeship, Transfer, Undergraduate, Violation, Hind — i.e. **student-facing academic
  regulation**.
- `education_tr`: Atama (appointments), Bütçe (budget), İhale (tenders), Demirbaş (fixed assets), Etik, Fikri
  (intellectual property), Bilişim (IT), Kalite (quality), İmza (signature authority), YapayZeka (AI), Teşvik
  (incentives), Misafir, Harita, STAM, Bap … — i.e. **administrative, financial, HR and procurement directive**.

Zero document correspondence. The "language-associated comparison" in §5.5 therefore varies language *and* topic *and*
document genre *and* intended audience simultaneously. Table 4 obscures this by labelling both rows "TED University
regulations and guidelines".

**Fix.**

1. Say plainly what the two corpora contain. This costs the paper nothing — the comparison remains a legitimate worked
   illustration of the pipeline — and it forecloses a reviewer discovering it independently.
2. Split Table 4's *Source* column so the two education rows are distinguishable, or add a *Document type* column.
3. Rephrase RQ2 and RQ3 away from yes/no capability questions. "To what extent do corpus-specific reports diverge when
   language differs under one fixed protocol, and what does the divergence look like?" is answerable and non-trivial;
   "can the pipeline expose language-conditioned ranking changes" is not.
4. **Strongly recommended:** TED University publishes a number of regulations in both Turkish and English. Building
   even a ten-document genuinely parallel subset and rerunning the language comparison would turn §5.5 from a confounded
   illustration into a controlled one, at the cost of one extra corpus run. That is the single highest-value new
   experiment available to this paper, because it is the only one that would let RQ2 be answered rather than
   illustrated.

**Proposed replacement text** — [results.tex:189](journal_paper/results.tex#L189):

```latex
Under the shared evaluation setup in Section~\ref{shared-evaluation-setup}, the English and Turkish education
corpora provide a within-snapshot comparison of whether model behavior differs between the two language-associated
cases. The comparison is bounded in a way that must be stated precisely. The two corpora are drawn from the same
institutional source but are not parallel and do not overlap in content: \texttt{education\_eng} consists of
student-facing academic regulations (admission, examinations, transfer, internship, scholarships), whereas
\texttt{education\_tr} consists of administrative, financial and human-resources directives (appointments, budget,
procurement, fixed assets, intellectual property). Language therefore varies together with topic, document genre,
intended audience, and qrels composition. What follows is a case observation about two corpus reports produced
under one protocol, not an isolated estimate of a language effect.
```

---

### MJ9 — The generated report, which the paper designates as the primary deliverable, contains errors the paper does not

**Problem.** [experiments.tex:146](journal_paper/experiments.tex#L146) states that "each dataset report is the primary
decision-support artifact for its own corpus". A reader who follows that instruction and opens the generated reports
finds a misstated configuration, a mislabelled conclusion, and statistical tests the manuscript has deliberately
removed. For a tool paper the generated report *is* the product, so defects in it are defects in the contribution.

**Where.** [experiments.tex:142-148](journal_paper/experiments.tex#L142) (§4.6);
[method.tex:89-107](journal_paper/method.tex#L89) (§3.5 and Table 2).

**Evidence.** In `aggregated_reports/2026-07-23_20-23-04/aggregate_report.md`:

- *"Chunking: 1000 **tokens** with 200-token overlap."* Both the paper and the code use **characters** (LangChain
  recursive character splitter). The report misdescribes the configuration it was generated from.
- *"paraphrase-multilingual-mpnet-base-v2 … Best on: education_eng (MAP=0.42), education_tr (MAP=0.36)."* M5 is not
  best on `education_eng` — M1 is, at 0.526. The "Best on" label is being emitted for datasets where the model is not
  best. The same mislabelling appears for all five models.
- The report still emits a Friedman test (**χ² = 1.87, p = 0.760**), paired t-tests, Cohen's *d*, and coefficient-of-
  variation consistency scores. The manuscript removed all of these. The reader is therefore never told that the
  dataset-level omnibus test over three corpora is non-significant — which is not embarrassing (three dataset means
  cannot support such a test, which is exactly why the paper moved to query-level bootstrap), but it should be stated
  rather than left to be discovered in the artifact.

Two further tool-level issues in the same area:

- `qrels_embedding_model_index: 4` is **dead** under `qrels_pooling: true` — it is read only inside the `else` branch
  at `rag_benchmark.py:186` — yet it is serialised unconditionally into every raw-result JSON. A reader inspecting the
  frozen artifact sees a field that appears to say the qrels came from M5 alone, directly contradicting the paper.
- `build_qrels_candidate_pool` calls `initialize_collection` (`rag_benchmark.py:191`), which **deletes and rebuilds
  every collection** because `reinitialize_collections = True`. Regenerating qrels therefore destroys the frozen
  indexes. This is documented in `analysis/README.md` but not in the paper, and it is a trap for anyone reusing the
  pipeline.

**Fix.**

1. Fix the report generator: characters not tokens; "Best on" only where the model actually leads; either remove the
   three-dataset Friedman/t-test/CV block or gate it behind an explicit flag with a caveat about *n* = 3.
2. Regenerate the frozen reports so the published artifacts match the paper.
3. Suppress `qrels_embedding_model_index` from the serialised config when pooling is enabled, or rename it to make its
   conditional role obvious.
4. Document the destructive re-initialisation in §3.5 and guard it with a confirmation or a `--no-reinit` default.
5. Add one sentence to §5.7 acknowledging the dataset-level omnibus result and why query-level bootstrap replaces it.

**Proposed replacement text** — insert in §5.7 after the first paragraph:

```latex
We do not report dataset-level significance tests. With three corpora, an omnibus test over dataset means has
almost no power---on this snapshot the Friedman statistic is $\chi^2 = 1.87$ ($p = 0.76$), which is uninformative
rather than evidence of equivalence---and the pipeline's automatically generated aggregate report is configured
accordingly. The query-level bootstrap below is reported instead because it uses the 148 scored queries as the
unit of variation rather than three dataset means.
```

---

### MJ10 — No lexical baseline, while the synthetic queries are strongly lexically anchored

**Problem.** The tool evaluates dense sentence-transformer models only. A practitioner-facing *selection* tool that
cannot return the answer "BM25 already beats every dense candidate on your corpus" is missing one of the most common
and most consequential real outcomes — and BEIR, which the paper already cites, is the standard evidence that this
happens. This is a capability gap in the contribution, not a roster-size quibble.

It is sharpened by a property of the generated queries that the paper does not report: they overlap their seed chunk
lexically to a very high degree, so a substantial part of what the benchmark measures is near-duplicate surface
matching, for which a lexical baseline is the natural reference point.

**Where.** [experiments.tex:89](journal_paper/experiments.tex#L89) (roster rationale);
[discussion.tex:27](journal_paper/discussion.tex#L27); [method.tex:71](journal_paper/method.tex#L71).

**Evidence.** Mean fraction of a query's content words (length > 3) that appear verbatim in its own seed chunk, against
the same fraction for a randomly chosen chunk from the same corpus:

| corpus        | overlap with seed chunk | overlap with random chunk | mean content words per query |
| ------------- | ----------------------- | ------------------------- | ---------------------------- |
| education_eng | 0.593 (median 0.613)    | 0.171                     | 8.4                          |
| education_tr  | 0.506 (median 0.500)    | 0.100                     | 8.1                          |
| law_tr        | 0.446 (median 0.500)    | 0.065                     | 8.4                          |

On `education_eng`, 22% of queries have ≥ 80% of their content words present verbatim in the seed chunk. Combined with
MJ5 (the seed is a positive ~90% of the time), the task has a strong lexical-matching component.

**Fix.**

1. Add BM25 as a rostered candidate. It requires no embedding model, no GPU, and no new judging — it retrieves from the
   same chunked corpus, is scored against the same frozen qrels, and gives readers an absolute reference for whether
   MAP@10 = 0.36 on Turkish is good or poor. It also strengthens the pooling design, since a lexical retriever
   contributes candidates that no dense model surfaces.
2. Report the overlap statistics above in §4.3 or §5.9 as a query-realism diagnostic, and make the pipeline emit them
   per run. They are a legitimate quality-control output for a synthetic-query pipeline.
3. Optionally, add a paraphrase pass to the generator so a second, lower-overlap query variant can be produced, and
   report both. The existing system instruction already asks for a query "that is not just a replicate of the
   document" — measuring how well that instruction is followed is a natural pipeline feature.

---

### MJ11 — Citation defects that affect substance

**Problem.** Three citations do not support the claims they are attached to, and the paper's central method-level
argument — pooling incompleteness — is stated three separate times with no citation to the literature that established
it. There are also several canonical omissions that a reviewer in this area will notice immediately.

**Where.** [related.tex:13,15,19,23](journal_paper/related.tex#L13); [method.tex:59](journal_paper/method.tex#L59);
[discussion.tex:25](journal_paper/discussion.tex#L25).

**Evidence — support mismatches.**

- **`Song_2024` (MLKE)** at [related.tex:19](journal_paper/related.tex#L19) occupies the slot for "multilingual …
  benchmarks show ranking behavior conditioned on similarity formulation and corpus composition". MLKE is a benchmark
  for **multilingual knowledge editing** of LLM parametric knowledge. It contains no retrieval, no embedding ranking,
  and no corpus-composition analysis. **Does not support.** Also an SSRN preprint with a likely journal successor.
- **`huang-etal-2025-targa`** at [related.tex:13](journal_paper/related.tex#L13) is cited as a "concrete quality
  control relevant to qrels design". TARGA is targeted synthetic data generation for KBQA in-context learning; it has
  no judging component at all. **Does not support.** `caferouglu2025sing` in the same sentence is **weak**: its
  "LLM-as-a-judge with executability checks" validates *SQL executability*, a mechanically checkable property with a
  ground-truth oracle, which is categorically unlike binary topical relevance. Only `Bassani_2021` is apt. This
  sentence carries the paper's justification that its LLM-judged qrels rest on established practice, so it is exactly
  where the argument should be strongest and it is currently weakest.
- **`ali2024establishing`** at [related.tex:23](journal_paper/related.tex#L23) is placed under "Reproducibility and
  Benchmark Governance". It is about recovering trace links between requirements and code. **Does not support** —
  relocate to §2.1 as another domain-pipeline example, or drop.

**Evidence — missing canonical references.** Three statements of pool incompleteness
([related.tex:15](journal_paper/related.tex#L15), [method.tex:59](journal_paper/method.tex#L59),
[discussion.tex:25](journal_paper/discussion.tex#L25)) cite nothing, and `Voorhees_Evaluation_2002` alone is
under-powered as the sole support for the pooling contribution. Required additions:

```bibtex
@inproceedings{zobel1998reliable,
  author = {Zobel, Justin},
  title = {How Reliable Are the Results of Large-Scale Information Retrieval Experiments?},
  booktitle = {Proceedings of the 21st Annual International ACM SIGIR Conference on Research and
               Development in Information Retrieval (SIGIR '98)},
  pages = {307--314}, year = {1998}, publisher = {ACM}, doi = {10.1145/290941.291014}
}

@inproceedings{buckley2004retrieval,
  author = {Buckley, Chris and Voorhees, Ellen M.},
  title = {Retrieval Evaluation with Incomplete Information},
  booktitle = {Proceedings of the 27th Annual International ACM SIGIR Conference on Research and
               Development in Information Retrieval (SIGIR '04)},
  pages = {25--32}, year = {2004}, publisher = {ACM}, doi = {10.1145/1008992.1009000}
}
```

Also expected and currently absent:

- **Reimers & Gurevych (2019)**, Sentence-BERT, EMNLP-IJCNLP, pp. 3982–3992 — the origin paper of the entire roster and
  of the `InformationRetrievalEvaluator` the pipeline uses. Currently cited only as three URLs.
- **Upadhyay et al. (2024)**, UMBRELA (arXiv:2406.06519) — the toolkit that produced the LLM qrels for the TREC 2024
  RAG Track, i.e. the closest precedent to what this pipeline does. Its absence beside `thakur2025support` is
  conspicuous.
- **Faggioli et al. (2023)**, *Perspectives on LLMs for Relevance Judgment*, ICTIR '23, pp. 39–50,
  doi:10.1145/3578337.3605136; and **Thomas et al. (2024)**, SIGIR '24, pp. 1930–1940, doi:10.1145/3626772.3657707.
- **Es et al. (2024)** RAGAS (EACL demos, pp. 150–158) and **Saad-Falcon et al. (2024)** ARES (NAACL, pp. 338–354) —
  needed for RR2 in any case.
- **Enevoldsen et al. (2025)**, MMTEB (ICLR) — §2.1 currently stops at MTEB 2023, which reads three years stale on the
  multilingual axis that two of three corpora sit on.
- **Robertson & Zaragoza (2009)**, BM25 (FnTIR 3(4):333–389, doi:10.1561/1500000019) — needed for MJ10.
- Optionally **Voorhees (2000)**, *Variations in relevance judgments*, IP&M 36(5):697–716, which directly supports the
  single-judge caveat at [discussion.tex:25](journal_paper/discussion.tex#L25).

**Evidence — metadata errors affecting substance.**

- `Lewis_RAG_2021` is entered as `@article` with `journal = {arXiv}`, year 2021. It is **NeurIPS 2020**, vol. 33,
  pp. 9459–9474. This is the paper's opening citation.
- `thakur2025support` is cited three times as the anchor for LLM-judge reliability and pooling design, but a
  peer-reviewed version exists: Thakur, Pradeep, Upadhyay, Campos, Craswell, Soboroff, Dang, Lin, *Assessing Support
  for the TREC 2024 RAG Track*, SIGIR '25, doi:10.1145/3726302.3730165.
- `Thakur_BEIR_2021` gives `volume = {34}, pages = {7984--7996}` for the NeurIPS main proceedings. BEIR appeared in the
  **NeurIPS 2021 Datasets and Benchmarks Track**; the volume and page range do not correspond to it.

**Fix.** Remove or relocate the three mismatched citations, add the canonical set above, and correct the three metadata
errors. The remaining bibliography issues are collected in §5.

---

## 5. Minor revision

**m1 — Stale duplicate abstract.** `journal_paper/abstract.tex` is not `\input` by
[manuscript.tex](journal_paper/manuscript.tex) (the abstract is inline at lines 19–23) and still contains claims the
current version has removed: "language rather than domain dominates difficulty here", "English favors monolingual
models", "confirming that the ranking is stable under an alternative single-model pool". If it ships in the submission
package it will be read as a contradiction. Delete it or synchronise it.

**m2 — "Mean MAP@10" means two different things.** In Table 8 (`tbl:dataset_result_summary`) it is the mean over the
five models for one corpus; in Table 9 (`tbl:cross_dataset_consistency_summary`) it is the mean over the three corpora
for one model. Rename to "Mean MAP@10 (across models)" and "Mean MAP@10
(across corpora)".

**m3 — Citations placed after sentence-final periods.** Throughout: [intro.tex:3](journal_paper/intro.tex#L3), :7, :9;
[related.tex:7](journal_paper/related.tex#L7), :9, :13, :19, :23, :27, :29. Move each `\citep{}` inside the sentence it
supports.

**m4 — Identical `Success@10` across all five models needs a footnote.** All five report 0.9583 on `education_eng`
(46/48 scored queries) — identical to four decimal places. I verified this is genuine, not a bug: the same two queries
fail for every model. But a reader will suspect an error. Add a footnote saying the same two queries fail for all five
candidates.

**m5 — Table 2 should carry total judged pairs.** It reports positive qrels only (312 / 354 / 286). The totals
(2,117 / 3,378 / 3,801 = 9,296) appear only in §5.8 and §5.9 prose. Add a "Judged pairs" column so the labelling effort
is visible where the workload is described.

**m6 — Figure 1 shows three models for a five-model study.** `conceptual_overview.jpg` depicts "Model 1 / Model 2 /
Model 3". Regenerate with five, or relabel generically as "Model 1 … Model *n*". Also: the figure's internal title ends
with a period, and there is an empty dashed rectangle beneath the ingestion/chunking boxes.

**m7 — Five workflow figures largely restate two tables.** Figures 1–4 plus `experimental_design.png` cover material
already in Table 1 (stage sequence) and Table 2 (reporting outputs). Merge to at most two: one end-to-end pipeline
figure and one reporting-layer figure.

**m8 — Figure 8 (quality–speed) is weak.** Truncated *y*-axis starting near 0.23, no error bars despite per-model
intervals being available, no Pareto frontier marked, and it encodes ten numbers already in Table 16. Either add the
intervals and mark the Pareto set, or drop the figure and keep the table.

**m9 — Figures 5–7 duplicate Tables 7, 9, 11.** The auto-generated per-dataset bar panels add no information beyond
their adjacent tables. Move to supplementary material, or keep one as an example of the pipeline's visual output and
say so in the caption.

**m10 — RQ1–RQ3 are phrased as yes/no capability questions.** "Can the pipeline produce…", "can the pipeline
expose…" are trivially answerable. Rephrase as "To what extent…" or "Under what conditions…". See also MJ8.

**m11 — The repository is cited eight times inline.** Consolidate into a Code Availability statement and cite it once
or twice in the body.

**m12 — Missing declarations.** No Data Availability, Code Availability, Funding, Conflict of Interest, Ethics, or
declaration of generative-AI use in manuscript preparation. Most target journals require several of these; the CAS
template expects them before the bibliography.

**m13 — `\texttt` markup inside the abstract.** [manuscript.tex:20-22](journal_paper/manuscript.tex#L20) uses `\texttt`
for dataset and model names. Many publishers strip formatting from abstracts for indexing. Use plain text.

**m14 — The abstract understates the judging effort.** It reports "952 positive relevance judgments" without the 9,296
total judged pairs, which makes the labelling work look an order of magnitude smaller than it was. State both.

**m15 — "raw-L2" is used in the abstract before it is defined.** Define once on first use or avoid the shorthand in the
abstract.

**m16 — Highlight 4 overstates.** "Shared-protocol artifacts make corpus-specific screening **auditable**" — auditable
by whom, given no human audit was performed and (per RR1) the artifacts are not published? Soften to "inspectable and
repeatable", and revisit once RR1 is closed.

**m17 — §5.9 examples should give chunk IDs.** The worked `education_eng` example and its near-miss are described but
not identified. Give the query ID and both chunk IDs so a reader can locate them in the released qrels.

**m18 — Five uncited bibliography entries.** `Gao_KG_RAG_Power_2025`, `Saha_QuIMRAG_2024`, `Hu_ICCARAG_2025`,
`Ghasemi_Metadata_QR_2024` and `SentenceTransformers_Website` are defined but never cited. The first four are IEEE
Access papers with no thematic connection to the argument (power-grid cybersecurity KG-RAG, customs clearance, community
QA metadata); leaving them in reads as citation padding. Delete them. `SentenceTransformers_Website` is redundant with
two cited sentence-transformers entries.

**m19 — Mangled author names.** `dvovravckova2025analyzing` → **Dvořáčková, Lucie** (the bib string is a flattened
de-accenting, and the citation key inherits the corruption); `caferouglu2025sing` → **Caferoğlu, Çelik, Ulusoy** (and
the key's `caferouglu` disagrees with the field's `Caferoglu`); `Iana_2026` → **Glavaš**; `Margit_2025` parses as
family = Margit, given = Antal, which is almost certainly reversed — please confirm it should be `{Antal, Margit}`.

**m20 — Incomplete self-citation.** `Karakaya_Conference_2025` has no pages, DOI, publisher, ISBN or month, and the
`booktitle` string "TheIIER International Conference" is missing a space. It is the load-bearing reference for the
paper's novelty delta at [related.tex:29](journal_paper/related.tex#L29), so a reviewer will try to locate it and
currently cannot. Add the full proceedings record or an arXiv mirror.

**m21 — Other bibliography metadata.** `luo2025domain` is internally inconsistent (published December 2025, which is
*Processes* vol. 13, but the entry says vol. 14 / 2025). Missing DOIs on `Sajja_2025` (10.2166/wst.2025.156),
`dvovravckova2025analyzing` (10.1007/s00521-025-11231-4), `ali2024establishing` (10.1007/978-3-031-75872-0_16),
`Voorhees_Evaluation_2002` (10.1007/3-540-45691-0_34), `Muennighoff_MTEB_2023` (10.18653/v1/2023.eacl-main.148), and
several ACL/ACM entries. The eight `@misc` web entries are all dated 2026 with no access date — add
`note = {Accessed: 2026-01-01}` to match the provenance date already given at
[experiments.tex:41](journal_paper/experiments.tex#L41). Verify that `Abimbola_2026` and `Iana_2026` are published in
issue rather than "just accepted" before citing volume and page numbers.

**m22 — Preprint reliance on load-bearing claims.** Twelve of fifty cited works are preprints, workshop papers or
theses, and they concentrate in the two subsections carrying the methodological justification rather than in the
background. Two need attention specifically. `Mikkelsen_2026` is a **JMIR preprint** whose title still ends with
"(Preprint)", and it carries the paper's core empirical premise that rankings shift across corpora — this is the
manuscript's largest venue-quality exposure. `Wen_2026` is a preprints.org deposit supporting a claim about multilingual
judge calibration. Also `Steve_2023`: an identically-titled paper with the same headline findings was published as
*Domain-Specific Contextualized Embedding: A Systematic Literature Review*, 2020 12th ICITEE, IEEE, pp. 162–167, under
different authorship. Please resolve the provenance before submission — cite the 2020 IEEE version, or drop it.

---

## 6. Point-to-section index

| ID      | Sev.        | Manuscript location                                                         | Repository evidence                                                                          | Ask                                                                                                             | Effort                                | New compute              |
| ------- | ----------- | --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------- | ------------------------ |
| RR1     | Reject-risk | `experiments.tex` §4.5 Table 10, :137; `method.tex` :115               | `.gitignore:96`; `git ls-files datasets/` = 0; JSON mtime 20:16 vs report 17:52          | Publish artifacts; regenerate under final names; Zenodo DOI                                                     | 1 day                                 | No                       |
| RR2     | Reject-risk | `related.tex` §2.5; `intro.tex` :12; `discussion.tex` §6.3          | No positioning against evaluation tooling in any section file                                | **Resolved:** new prose subsection `rw-tooling` + 10 verified bib entries + gap/intro/discussion echoes | Done                                  | No                       |
| RR3     | Reject-risk | `results.tex` §5.8 Table 15, :295–313                                   | `backup_frozen_2026-07-23/`; 0/50 shared query IDs; `forced_source_positives: 50`        | Controlled M5-only subset ablation; add leave-one-out                                                           | 0.5 day                               | Rescore only             |
| MJ1     | Major       | `results.tex` §5.7; RQ1/RQ4; `conclusion.tex` :5,:9                    | `results_reanalysis/bootstrap_frozen.json`; `analysis/bootstrap_ci.py:43-49`             | Per-corpus CIs in the dataset report; rewrite corpus readings; stratify or disclose                             | 1 day                                 | Rescore only             |
| MJ2     | Major       | `experiments.tex` :59, Table 10; `discussion.tex` :27                   | `config.py:117-121`; `normalize_embeddings:false` in all 15 collections                  | Fix comment; change default; rerun under cosine                                                                 | 0.5 day                               | **Yes** (~1 h CPU) |
| MJ3     | Major       | `experiments.tex` :83                                                     | `rag_benchmark.py:259` vs `:270`; frozen batch files                                     | Unify prompts; correct the equivalence claim                                                                    | 1 hour                                | No                       |
| MJ4     | Major       | `method.tex` :53,:55; `results.tex` :319                                | `config.py:192-215`; `rag_benchmark.py:98-114`; `utils/llm.py:43-66`                   | Prompts appendix; fix contradictory criterion; log parse failures; human audit + κ                             | 1–2 days                             | Judge sample             |
| MJ5     | Major       | `method.tex` :59; `results.tex` §5.9; `discussion.tex` :25           | qrels vs queries: 9/150 seeds never pooled; seed positive 47/44/44                           | Report both numbers; add pool diagnostics; consider bpref                                                       | 0.5 day                               | Rescore only             |
| MJ6     | Major       | `intro.tex` :32; `experiments.tex` :61 Table 3                          | No varied parameter in any frozen run                                                        | One 2×2×2 sweep on one corpus; Kendall's τ stability table                                                   | 0.5 day                               | Partial                  |
| MJ7     | Major       | `method.tex` :81; `experiments.tex` :116 Table 10; Tables 8/10/12/16    | No warm-up in repo;`chromadb_utils.py:191,208,268`; M2 7.7→3.6→3.5 chunks/s              | Warm-up + ≥5 repeats; measure at k=10; split timers; token stats; hardware in body                             | 0.5 day                               | **Yes** (~1 h CPU) |
| MJ8     | Major       | `results.tex` §5.5, §5.6; RQ2/RQ3; Table 4                              | Document lists: zero overlap in subject matter                                               | Disclose corpus content; split Table 4; rephrase RQs; optionally build a parallel subset                        | 0.5 day (2 days with parallel corpus) | Optional                 |
| MJ9     | Major       | `experiments.tex` §4.6; `method.tex` §3.5                             | `aggregated_reports/2026-07-23_20-23-04/aggregate_report.md`; `rag_benchmark.py:186,191` | Fix generator; regenerate reports; hide dead config key; document destructive re-init                           | 0.5 day                               | Regenerate               |
| MJ10    | Major       | `experiments.tex` :89; `discussion.tex` :27                             | Overlap 0.593/0.506/0.446 vs 0.171/0.100/0.065                                               | Add BM25 to the roster; report overlap diagnostics                                                              | 0.5 day                               | Rescore only             |
| MJ11    | Major       | `related.tex` :13,:15,:19,:23; `method.tex` :59; `discussion.tex` :25 | `refs.bib` entries as listed                                                               | Remove 3 mismatched citations; add Zobel/Buckley & Voorhees + 6 canonical works; fix 3 metadata errors          | 0.5 day                               | No                       |
| m1–m22 | Minor       | see each item                                                               | see each item                                                                                | presentation, tables, figures, declarations, bibliography hygiene                                               | 1–2 days total                       | No                       |

Rough total: **8–11 working days**, of which roughly two hours are CPU time and one optional day is the human-audit
sample. Nothing here requires a GPU or new API budget beyond the judge-agreement sample.

---

## 7. What would convert this to accept-with-minor

In priority order. The first four are the ones I would treat as non-negotiable at the next round.

1. **Publish the artifacts and mint a DOI** (RR1). Without this the tool contribution cannot be assessed at all.
2. ~~**Position the pipeline against existing evaluation tooling** (RR2).~~ **Done** — implemented as the prose
   subsection `rw-tooling` in `related.tex` rather than as a table. This was the difference between "here is a pipeline
   I built" and "here is what this pipeline adds".
3. **Replace §5.8 with the controlled pool ablation** (RR3). A subset operation over data you already hold, with no new
   LLM calls, that turns the paper's weakest section into direct support for its novelty claim.
4. **Move the uncertainty layer into the per-corpus report and rewrite the corpus readings accordingly** (MJ1). The
   numbers already exist; the rewrite makes the paper's own argument about operational cost stronger, not weaker.
5. **Rerun under cosine and report both geometries as the pipeline's first worked sensitivity example** (MJ2 + MJ6).
   Under an hour of CPU, and it closes two major points with one subsection.
6. **Fix the timing methodology** (MJ7): warm-up, five repeats, median and IQR, measured at *k* = 10, hardware in the
   body. If the M2 anomaly turns out to be tokenisation rather than machine load, report it — it is a real finding.
7. **Put the prompts in an appendix and repair the judge criterion** (MJ4).
8. **Add BM25 to the roster** (MJ10). Cheap, and it gives every number in the paper an absolute reference point.
9. **The ~200-pair human-judge audit with Cohen's κ** (MJ4, item 5). Optional for acceptance, but it is the single
   change that would most raise the paper's standing, because it converts the limitation the manuscript names most
   often into a measured quantity.

A closing editorial note. The candour of this manuscript is genuinely above average, and I want to be clear that the
severity of this report is not a judgement on the honesty of the write-up. It is a consequence of the paper being a
tool paper: for that genre, availability, positioning and paper–code agreement carry the weight that empirical novelty
carries elsewhere, and those are the three places where the submission is currently short. The underlying work looks
sound, and most of the distance to acceptance is a week of careful engineering rather than a new research programme.
