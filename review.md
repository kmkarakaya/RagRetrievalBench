# Pre-submission review — `journal_paper/manuscript.tex`

**Date:** 2026-07-31
**Read against:** the paper's own stated goal, not any prior review.

> A pipeline to evaluate the performance of candidate embedding models on local datasets **easily**,
> **repeatably**, in a **countable and statistically explainable** way, generating **detailed reports per
> dataset or aggregated**.

**Reading posture:** a referee at a new journal, opening this cold, with no knowledge of earlier versions.

---

## Verdict

**Revise before submission — but the work is sound.** Nothing here questions the science. The pooling
design, the marginal-versus-paired interval distinction, and the measured pool-incompleteness numbers in
§5.10 are genuine strengths that most benchmark papers lack.

What needs fixing is the distance between what the paper *claims* and what it *shows*. Three of the goal's
four clauses are asserted more strongly than they are demonstrated:

| Goal clause | Status |
|---|---|
| *easily* | **Not demonstrated.** No command, no invocation, no usage surface anywhere in 31 pages. |
| *repeatably* | Demonstrated, but the strongest evidence sits in a table cell. |
| *countable and statistically explainable* | **Demonstrated well** — the best part of the paper. |
| *detailed reports per dataset or aggregated* | Described twice, never concretely; no report contents given. |

### Measured shape

| Metric | Value |
|---|---|
| Body words | ~12,980 |
| Tables / figures | 20 / 11 (≈1 exhibit per page) |
| Pages | 31 |
| Hedge words: *secondary* / *bounded* / *descriptive* / *conditional* | 18 / 14 / 13 / 11 = **56** |
| Restatements of the M1/M5/M3 headline | **9** |
| Occurrences of `raw-L2` / definitions of it | 7 / **0** |
| Usage or command content | **0** |

---

## Chapter by chapter

### Abstract

**Works.** Accurate, quantified, no overclaiming. The "purpose of the demonstration is not to make these
particular model rankings the main contribution" sentence is exactly right for a tool paper and pre-empts
the most likely misreading.

**Challenge.** It closes on five stacked caveats in a single sentence — synthetic queries, unvalidated
qrels, non-normalized retrieval, five-model roster, single-machine timing. A referee's last impression of
the abstract becomes a list of what the paper cannot do. The pipeline's actual deliverable — the per-dataset
and aggregate reports — is mentioned only in passing, though it is the goal's final clause.

**Alignment:** partial. → *item 10*

### §1 Introduction

**Works.** The problem is stated cleanly in the first paragraph and the "do not transfer a model between
corpora" thesis is defended rather than assumed. The four contributions are concrete. The RQ preamble that
defines *pipeline utility* and *operational cost* before use is good practice.

**Challenge.** RQ2 and RQ3 are titled "Language sensitivity" and "Domain sensitivity" — names that promise
causal identification. §5.5 and §5.6 then state plainly that language and domain are confounded with corpus
identity, source selection and qrels composition. A referee will read the RQ, reach the Results, and record
a mismatch between question and design.

**Alignment:** good, with a naming defect. → *item 7*

### §2 Related Work

**Works.** §2.5 ("Relation to General-Purpose Evaluation Tooling") is the strongest subsection in the
chapter and does the real work: it explains what BEIR/MTEB, `ir_datasets`, `ir_measures`, Pyserini, UMBRELA,
RAGAS/ARES and the application frameworks each supply, and why none of them takes an *unlabeled* local
collection as input. That is the contribution's actual defence. §2.6 converts it into five gaps tied to the
RQs. The candidate-pool discussion at the end of §2.2 correctly grounds the pooling design in Zobel and
Buckley & Voorhees.

**Challenge.** 1,656 words across five subsections, with very long citation-dense paragraphs — §2.3 runs
~250 words with 17 citations. It reads as a survey rather than as positioning. Per the author's decision
this pass does **not** compress it; noting it because a referee may raise it independently.

**Alignment:** good. No action this pass.

### §3 Method

**Works.** §3.6 (Query-Level Uncertainty Estimation) is the best-argued section in the paper. The
marginal-versus-paired distinction — and the explicit statement that overlapping marginal intervals are
*not* evidence two models perform alike — is a point most benchmark papers get wrong. The per-cell seeding
rationale (intervals reproducible from a partial re-execution) is a real engineering contribution stated
without inflation. §3.2's separation of the *query generator* and *relevance judge* roles, on the grounds
that their validity concerns differ, is careful.

**Challenge, and the chapter's biggest gap.** For a paper whose first goal word is *easily*, §3 never says
how the pipeline is run. Searching every `.tex` file for `command`, `CLI`, `invoke`, `python rag_benchmark`
and `--build` returns nothing; the only hits are the English word "command" in prose and `\providecommand`
in the preamble. The referee question — *how do I run this on my corpus?* — has no answer in the manuscript.

Second: §3.7 describes the two-layer reporting design, and §4.7 cross-references §3.7 and then re-describes
it. Neither states what a generated report actually contains beyond Table 2's one-line summaries. The
reports are the pipeline's product and the goal's final clause, yet they are the least concretely specified
artifact in the paper.

Third: two paragraphs of §3.6 reappear near-verbatim in §5.9 — the pooled-versus-macro mean and the
unstratified-resampling properties, in the same order, and the marginal/paired explanation likewise.

**Alignment:** strong on statistics, weak on usability and on the deliverable. → *items 1, 2, 3*

### §4 Experiments

**Works.** Genuinely well documented. Table 5 (parameters), Table 6 (model roster) and Table 7
(reproducibility conditions) are more complete than is typical — pinned library versions, the seed policy,
the compound-timing definition, the explicit statement that timing does not isolate model inference from
vector-store behaviour. §4.3's provenance disclosure, including that the two education corpora share four
documents in translation but differ in emphasis, is honest in a way referees notice favourably. §4.4's
explicit metric definitions (including that MAP@10's denominator penalises unretrieved positives) remove a
common source of ambiguity.

**Challenge.** "raw-L2" is used seven times across three files and defined nowhere; the reader must infer
that *raw* means non-normalized. And the Table 7 "Available artifacts" cell contains a sentence about how
*this paper's own* tables and figures were produced — meta-commentary about the manuscript's production
rather than about the pipeline, which does not belong in the paper.

**Alignment:** strong. → *items 2, 8*

### §5 Results

**Works.** The per-corpus structure genuinely demonstrates per-dataset reporting rather than merely
claiming it. §5.2's `education_eng` reading is the paper's best paragraph: it shows the paired interval for
M1−M2 including zero, concludes that the corpus *cannot* resolve the two leading candidates on quality, and
falls through to latency — which is precisely what a decision-support tool should do, and it is stated
without spin. §5.10's pool-incompleteness numbers (9 of 150 queries whose seed chunk no model retrieved;
seed judged relevant 47/44/44 of 50) convert a standard caveat into a measurement.

**Challenge — structural.** `tbl:per_corpus_ci` is cited in §5.2, §5.3 and §5.4 — the three sections whose
decisions depend on it — but printed in §5.9, roughly six pages later. Since the paper's own position is
that the dataset-level report is the primary selection artifact, the per-corpus statistics belong beside
the per-corpus results. This is the clearest structural contradiction of the stated goal in the paper.

**Challenge — rhetorical.** The M1/M5/M3 headline appears nine times across the manuscript, four of them
inside this chapter. Combined with the hedge-word density, the chapter reads as more repetitive than its
content warrants.

**Alignment:** the content serves the goal; the layout works against it. → *items 3, 4, 5, 6, 7, 8*

### §6 Discussion

**Works.** §6.1 correctly separates "what this snapshot showed" from "what a practitioner should do", and
says outright that the examples are *not* permanent prescriptions. §6.4 is a model limitations section —
it concedes no human validation, no judge-agreement analysis, roster-conditional qrels, untested retrieval
geometry, no sensitivity study, and single-run timing, without hedging any of them into vagueness.

**Challenge.** §6.3 re-derives the positioning already established in §2.5 and then cross-references §2.5
for it. And because §6.4 already carries every caveat in full, the caveats repeated throughout §§1–5 are
redundant with it — that is what makes the 56 hedge-word count a presentation problem rather than an
honesty problem.

**Alignment:** good. → *items 4, 9*

### §7 Conclusion

**Works.** Answers each RQ in turn, and the RQ2/RQ3 answers explicitly decline the causal reading ("does
not establish a causal language effect because each language condition is represented by one corpus"). The
future-work paragraph maps each limitation to a specific next step rather than gesturing.

**Challenge.** It is the fourth or fifth restatement of the headline result. Standard for a conclusion, but
here it compounds.

**Alignment:** good. → *items 5, 7*

---

## What must not change

Recorded so that the revision pass does not damage the paper's strengths:

1. **§3.6 and §5.9's uncertainty argument.** The marginal/paired distinction is the paper's sharpest
   methodological point. De-duplicate the prose; do not weaken the argument.
2. **§5.2's "the corpus cannot resolve M1 vs M2" reading.** The most credible paragraph in the paper.
3. **§5.10's pool-incompleteness measurement.** A measurement where most papers offer a caveat.
4. **§4.3's provenance and comparability disclosure.** Honest about a genuine confound.
5. **§6.4 Limitations.** Every caveat removed elsewhere must still be found here.
6. **Every number.** All data tables are pipeline-generated fragments; no figure in the manuscript is
   hand-authored. The revision changes no value.

---

## Out of scope for this pass

Author decisions, recorded so the reasoning is not lost:

- **No length compression.** Related Work stays at 1,656 words; §5.2–5.4 stay separate.
- **No figure changes.** The three near-identical per-dataset bar charts stay; no report-excerpt figure.
- **RQ2/RQ3 stay separate** — renamed only.
- **The `--verify-paper` gate stays out of the manuscript.** It is a development control, not a
  contribution, and the paper should not discuss its own production.

## Known open items not addressed here

- The GitHub repository is **private**; it returns 404 anonymously. The Code and Data Availability
  statement and the two remaining inline citations point at it. Must be public before submission.
- The interactive and batch query-generation paths build the seed prompt differently
  (`rag_benchmark.py`); the frozen snapshot came from the batch path. A repeatability defect in the code,
  not in the paper.
- A failed judge-response parse is recorded as a non-relevant label, so "judged non-relevant" and "never
  successfully judged" are indistinguishable in the released qrels. Affects the *countable* claim.
