# Pre-submission TODO

> **Status 2026-07-31:** all ten manuscript items applied and verified.
> Build lint 0/0, 0 undefined references, `.aux` converged, 31 pages, gate 33/33, frozen datasets
> untouched, `pytest` 81 passed / 7 failed (unchanged baseline).

Companion to [review.md](review.md). Ten items, ordered by what a fresh referee hits first.
Scope: consistency and goal-alignment only — no length compression, no figure changes, **no number changes**.

## Items

- [x] **1. Add a usage subsection to §3 Method** — ~40 min
  The paper claims the pipeline is *easy to use* and shows no invocation anywhere. Add a subsection at the
  end of `journal_paper/method.tex`: what the practitioner supplies, what is configured in `config.py`, the
  command that runs the pipeline end to end, and what lands on disk. Source the flags from `README.md`
  ("The Full Stage Sequence") and verify each against `rag_benchmark.py:780-820`.
  *Show proposed text before applying.*

- [x] **2. Make report generation single-sourced and concrete** — ~1 h
  - `journal_paper/method.tex` §3.7 owns the mechanism: how a dataset report is built from the stored
    raw-result JSON, how the aggregate report is built from completed dataset reports, and what each one
    contains. Take contents from `utils/report_utils.py` and `utils/aggregate_report_utils.py`.
  - `journal_paper/experiments.tex` §4.7 keeps only what *this snapshot* produced; drop the ~350 words
    that re-describe the two-layer design after cross-referencing §3.7.
  - Remove the sentence in the Table 7 "Available artifacts" cell (`experiments.tex:129`) about the
    paper's own tables and figures being pipeline-emitted. The manuscript does not discuss its own
    production.
  *Show proposed text before applying.*

- [x] **3. De-duplicate Method §3.6 against Results §5.9** — ~30 min
  `method.tex:94,98` and `results.tex:184,186` carry the same two arguments near-verbatim
  (pooled-vs-macro mean + unstratified resampling; marginal-vs-paired intervals). Method defines, Results
  reports and cross-references `Section~\ref{query-level-uncertainty}`.

- [x] **4. Halve the hedging density** — ~1 h
  56 instances of four words: *secondary* ×18, *bounded* ×14, *descriptive* ×13, *conditional* ×11. State
  each caveat once where first load-bearing, and once in §6.4. §6.4 must still carry every one.

- [x] **5. Reduce the headline restatement from 9 to 3** — ~30 min
  Keep: abstract, §5.1 (full), §6.1 (interpretive). §5.2–5.4 keep their own per-corpus readings. §5.7 and
  §7 become cross-references. Sites: `results.tex:3,7,43,70,96,152`; `discussion.tex:5,9`;
  `conclusion.tex:9`.
  *Show proposed text before applying.*

- [x] **6. Move `tbl:per_corpus_ci` into §5.1** — ~20 min
  Cited at `results.tex:43,70,96`, printed at `results.tex:188`. Move the float and a one-sentence
  introduction to §5.1, after `tbl:dataset_result_summary`. §5.9 then covers the aggregate layer only.
  Pure relocation.
  *Show proposed text before applying.*

- [x] **7. Rename RQ2 and RQ3** — ~15 min
  "Language sensitivity" → **"Cross-language shortlist stability"**; "Domain sensitivity" →
  **"Cross-domain shortlist stability"**. Sites: `intro.tex:23,25`; `related.tex:33`; `conclusion.tex:7`;
  subsection titles at `results.tex:118,133`.

- [x] **8. Define "raw-L2" at first use** — ~10 min
  Used 7×, defined 0×. One parenthetical at `experiments.tex:50` where the geometry is already described.

- [x] **9. Trim Discussion §6.3** — ~15 min
  `discussion.tex:19` re-derives the §2.5 positioning and then cross-references §2.5 for it. Keep the
  cross-reference and what §6.3 adds.

- [x] **10. Rebalance the abstract** — ~20 min
  `manuscript.tex:22` ends on five stacked caveats. Compress to one clause; use the space to name the
  per-dataset and aggregate reports. Caveats remain in full in §6.4.

## Verification after each item

- [x] `cd journal_paper && ./build.ps1 -CompilePdf` → `Lint summary: 0 errors, 0 warnings`, then one extra
      `pdflatex` pass; expect 0 undefined citations and 0 undefined references
- [x] `python rag_benchmark.py --verify-paper` → exit 0, 33 values checked
- [x] `git status --porcelain -- datasets/` → empty
- [x] `pytest tests/ -q` → matches the 6-failure `HEAD` baseline, 81 passing
- [x] After items 4 and 5, re-count hedge words and headline restatements to confirm the reduction landed

## Reformatted for Machine Learning (Springer) — 2026-08-01

Target journal changed from Elsevier to **Machine Learning** (Springer, journal 10994).

- [x] `manuscript.tex` → `sn-jnl` with `[pdflatex,sn-basic,lineno]`; Springer Basic author–year
      references, `\author*`/`\affil*`/`\abstract{}`/`\keywords{}`, `lineno` margin numbers for referees.
      Elsevier `highlights` removed (no Springer equivalent); `\bibliographystyle` and the manual
      `natbib` load removed because the class supplies both.
- [x] `declarations.tex` → `\backmatter` + `\section*{Declarations}` with `\bmhead{}` subheadings:
      Funding, Competing interests, Ethics approval, Consent for publication, Data availability,
      Materials availability, Code availability, Author contributions (replaces `\printcredits`).
- [x] `build.ps1` → sn-jnl assets from `ML_Template/`, `pdflatex` instead of `xelatex`, SN001–SN014 lint
      rules replacing CAS001–CAS016. Structural rules (caption/label/centering, flat-source, image and
      citation-key resolution) are unchanged.
- [x] Elsevier front matter archived under `journal_paper/archive_cas/` (invisible to every glob).
- [x] Verified: lint 0/0, 0 undefined citations/references, `.aux` converged, 47 pages,
      `--verify-paper` 33/33, `datasets/` untouched. `manuscript_sn_full.tex` compiles standalone.

**Submit `build/<timestamp>/manuscript_sn_full.tex`** — Springer asks for a single `.tex` document, and
that wrapper has every `\input` inlined.

## Blocking before submission — author action

- [ ] **Make the GitHub repository public.** It currently 404s anonymously. The Data and Code Availability
      statements and two inline citations point at it. This is the single largest gap between what the paper
      claims and what a referee can verify.
- [ ] **Write the 1–2 page information sheet** that Machine Learning requires alongside each submission.
- [ ] Confirm on the live submission-guidelines page that Machine Learning wants Springer Basic
      **author–year** (current setting). Switching to numbered is a one-word change: add `Numbered` to the
      `\documentclass` options in `manuscript.tex`.
- [ ] Enter the ORCID (0000-0002-9542-6965) in the submission portal — `sn-jnl`'s `\orcid` macro needs an
      `Orcidlogo.eps` that ships separately, so it is not set in the LaTeX source.
- [ ] Confirm whether the journal requires a generative-AI declaration in the manuscript body
      (currently omitted by author decision) or only in the submission portal.

## Not in this pass

Code-level defects that affect the paper's claims but need no manuscript edit:

- [ ] Unify the interactive and batch query-generation prompts (`rag_benchmark.py`); the frozen snapshot
      came from the batch path. Affects *repeatable*.
- [ ] Stop recording judge parse failures as non-relevant labels; add retry and a distinct unjudged state.
      Affects *countable*. Does not change the frozen qrels.
