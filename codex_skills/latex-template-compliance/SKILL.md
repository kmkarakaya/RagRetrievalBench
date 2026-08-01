---
name: latex-template-compliance
description: Enforce Springer Nature sn-jnl template rules for the journal_paper TeX-first workflow (target journal: Machine Learning, Springer 10994). Use when editing manuscript.tex, section .tex files, declarations.tex, refs.bib, tables, figures, front matter, citations, and build.ps1 lint/build checks.
---

# Springer Nature (sn-jnl) Compliance Workflow

Use this workflow whenever a task touches manuscript content or formatting.

For template-grounded details and canonical command patterns, load:
- `references/template_rules.md`

## Source Editing Rules
- Edit only TeX-first manuscript sources:
  - `journal_paper/manuscript.tex`
  - `journal_paper/*.tex` section files
  - `journal_paper/refs.bib`
- Keep source files flat in `journal_paper/` (no nested manuscript folders).

## Structural Rules
- Declare the class directly: `\documentclass[pdflatex,sn-basic,lineno]{sn-jnl}`. There is no
  placeholder token to substitute (the retired CAS build used `__CAS_CLASS__`; that is gone).
- Keep section includes via `\input{...}` with flat filenames only.
- Keep figure assets in the same flat folder and reference with flat names.
- Keep Springer front matter blocks present in `manuscript.tex`:
  - `\title[Running Head]{Full Title}`
  - at least one `\author*[1]{\fnm{First} \sur{Last}}\email{...}`
  - matching `\affil*[1]{\orgdiv{...}, \orgname{...}, \orgaddress{\city{...}, \country{...}}}`
  - `\abstract{...}` — a command taking the prose as its argument
  - `\keywords{comma, separated, list}`
  - `\maketitle`
- Keep the bibliography contract: `\bibliography{refs}` alone.
- Never add these to `manuscript.tex`; the class provides all three and the lint gates reject them:
  - `\usepackage{natbib}` — `sn-jnl` already loads it, so a second load is an option clash
  - `\bibliographystyle{...}` — set by the `sn-basic` documentclass option
  - `\begin{highlights}` — Elsevier-only, no Springer equivalent
- Keep `amsmath` loaded: the class calls `\allowdisplaybreaks` at `\begin{document}` and fails
  with `Undefined control sequence` without it.
- `sn-jnl` is single-column. Do not use `table*` or `figure*`; size floats with `\linewidth`.

## Declarations Rules
`journal_paper/declarations.tex` carries the Springer back matter and must keep:
- `\backmatter` before any declaration content
- `\section*{Declarations}`
- `\bmhead{}` subheadings for Funding, Competing interests, Ethics approval and consent to
  participate, Consent for publication, Data availability, Materials availability, Code
  availability, Author contributions
- `Not applicable` as the body wherever a heading does not apply
- Author contributions replaces the CAS `\printcredits`; `\credit{}` is not available in `sn-jnl`.

## Table/Figure Rules
- Require both `\caption{...}` and `\label{...}` for:
  - `table`, `table*`
  - `longtable`
  - `figure`, `figure*`
- Keep labels unique and meaningful.
- Prefer template-aligned formatting:
  - tables: `booktabs` style (`\toprule`, `\midrule`, `\bottomrule`)
  - figures: `\centering` + explicit width option in `\includegraphics[...]`
- Keep table/figure labels cross-referenceable from text (`\ref{...}` where relevant).
- Keep captions, headings, row labels, and surrounding prose semantically aligned. If the artifact and prose drift apart, revise one or both sides until they describe the same workflow or evidence.
- If a figure presents a finer-grained workflow than the prose, revise the prose so it follows the figure sequence explicitly rather than leaving the figure to carry unsupported detail.
- Prefer regular `table` environments for short manuscript tables. Use `longtable` only when genuine multi-page behavior is needed; small `longtable` blocks in this repo have triggered split-box failures after unrelated layout changes.

## Citation Rules
- Use natbib citation commands (`\citep`, `\citet`, etc.).
- Ensure every cited key exists in `journal_paper/refs.bib`.
- Do not use unresolved placeholder citation styles.
- Keep key names stable once introduced; avoid silent key renames.
- The reference style is Springer Basic author-year, selected by the `sn-basic` documentclass
  option without `Numbered`. To switch to numbered references, change the documentclass option;
  never add a `\bibliographystyle` line.
- For website-style resources, follow the pattern already in `journal_paper/refs.bib`:
  - use `@misc`
  - use `howpublished = {\url{...}}`
  - add `note = {Accessed: YYYY-MM-DD}`
  - avoid report-style over-specification unless the extra metadata is methodologically necessary
- For organizational or corporate authors, wrap the full author string in double braces, for example `author = {{RagRetrievalBench}}`, so BibTeX does not render inverted pseudo-person names such as `Project, R.`.

## Section-Boundary Guidance
- Keep `journal_paper/method.tex` focused on:
  - proposed pipeline/workflow design
  - artifact construction
  - indexing/evaluation logic
  - reporting/reproducibility
- Keep `journal_paper/experiments.tex` focused on:
  - manuscript-specific setup
  - dataset context and provenance
  - evaluated model roster
  - controlled variables and limitations
- Keep `journal_paper/results.tex` focused on:
  - metric presentation
  - comparative evidence
  - tradeoffs and findings
- Do not let Method absorb result interpretation or manuscript-snapshot setup details that belong in Experiments or Results.

## Wording Guidance For Reusable Methods
- When describing a reusable pipeline in `method.tex`, prefer generalized wording such as `document collection` unless a specific source format is methodologically important.
- If the current manuscript snapshot uses a concrete source format (for example PDFs), mention that as a factual implementation detail in the relevant subsection rather than making the whole method unnecessarily format-specific.

## Terminology Guidance
- In reader-facing scholarly prose, prefer `paper` over `manuscript` for statements such as `this paper`, `the paper presents`, or `the paper reports`.
- Reserve `manuscript` for workflow and source-management contexts, such as `manuscript.tex`, build steps, or submission-package instructions.
- Avoid report-oriented internal traceability language in the paper body unless it is required for methodological clarity.
- In reader-facing scholarly prose, prefer `practitioner` for the person applying the pipeline to local corpora.
- Avoid mixing `user`, `developer`, and `practitioner` in the paper body unless the distinction is genuinely necessary.
- Reserve `developer` for implementation/repository contexts and `user` for interface/product contexts.

## Required Validation
- Always run:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1`
- If PDF compile is part of request:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1 -CompilePdf`
- For layout-sensitive edits involving tables, figures, captions, or section reflow, prefer running `-CompilePdf` even if the user did not explicitly ask for it, because lint-only checks may miss pagination and float-placement failures.
- Treat build lint failures as blocking defects.
- The build uses **pdflatex**. All source is ASCII with escaped accents (`T\"urkiye`); keep it
  that way rather than pasting UTF-8 literals.
- If a compile hangs with no log growth, MiKTeX is blocking on an on-the-fly package install.
  Run `pdflatex -disable-installer` to surface the missing `.sty`, then `mpm --install=<pkg>`.
  Packages already added for `sn-jnl`: `threeparttable`, `appendix`, `amscls` (for `amsthm.sty`).
- The submission artifact is `build/<timestamp>/manuscript_sn_full.tex` — the single-file wrapper
  with every `\input` inlined, because Springer requires one `.tex` document.
- After manuscript number edits also run `python rag_benchmark.py --verify-paper` (33 values).

## Quick Checklist
For a concise task checklist, see:
- `references/checklist.md`
