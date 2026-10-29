# Codex Project Rules (Non-Negotiable)

These rules apply to all Codex sessions in this repository.

## Primary Manuscript Workflow

- Target journal: **PeerJ Computer Science**. Always follow the `wlpeerj` template conventions
  from `journal_paper/Peerj_template/` (`wlpeerj.cls`, `main.tex`).
- The rejected Springer *Machine Learning* front matter is archived in `journal_paper/archive_sn/`
  and the Elsevier CAS front matter in `journal_paper/archive_cas/`, for reference only. Do not
  treat either as the active contract and do not build from them.
- Use TeX-first sources only:
  - `journal_paper/manuscript.tex`
  - `journal_paper/*.tex` section files
  - `journal_paper/refs.bib`
- Do not reintroduce markdown-to-latex manuscript assembly.
- Do not edit generated files under `journal_paper/build/` or the exported package in
  `journal_paper/Peerj Submision/` (except the hand-written `portal_statements.txt`) as source
  content.

## Flat Folder Policy

- Keep manuscript `.tex` files and image files in `journal_paper/` (flat source folder).
- Do not use nested source paths in `\input{...}` or `\includegraphics{...}`.

## Mandatory PeerJ Front Matter

`journal_paper/manuscript.tex` must keep all of the following (lint rules PJ001–PJ008):

- `\documentclass[fleqn,10pt,lineno]{wlpeerj}` — `lineno` is required for peer review
- `\title{Full Title}` — no running-head optional argument
- at least one authblk `\author[1]{First Last}` with a matching `\affil[1]{Dept, University, City, Country}`
- `\corrauthor[1]{First Last}{email}`
- `\begin{abstract}...\end{abstract}` **before** `\begin{document}`, with no nested `\begin`/`\end`
- `\maketitle`
- `\bibliography{refs}`

Must **not** appear (lint rules PJ010–PJ016):

- `\usepackage{natbib}` or `\bibliographystyle{...}` — `wlpeerj` loads natbib and sets `apalike`
- an uncommented `\keywords{...}` — PeerJ collects keywords in the submission form
- `\begin{highlights}` or sn-jnl-only commands (`\fnm`, `\sur`, `\orgdiv`, `\bmhead`, `\backmatter`)
- `table*` / `figure*`
- Funding, Competing interests, Author contributions, or Declarations headings in any `.tex` file

## PeerJ Declarations

- Funding, competing interests, ethics/consent, author contributions, and keywords are entered
  in the PeerJ submission form; their text lives in `journal_paper/Peerj Submision/portal_statements.txt`.
- `journal_paper/declarations.tex` keeps only `\section*{Data availability}` and
  `\section*{Code availability}` (warning PJ901).

## Table/Figure Rules

- Every `table`, `longtable`, and `figure` environment must include:
  - `\caption{...}`
  - `\label{...}`
- Keep labels unique and citation keys resolvable in `refs.bib`.
- For template alignment, prefer `booktabs` table style (`\toprule`, `\midrule`, `\bottomrule`).
- Keep figure blocks template-like: `\begin{figure} ... \centering ... \includegraphics[...] ... \caption...\label...`.
- Reference tables and figures explicitly in the surrounding prose where they are methodologically relevant.
- Keep figure captions, table captions, and row/column wording aligned with the section text; revise one or both sides if the artifact and prose drift apart.
- Prefer regular `table` environments for short manuscript tables. Use `longtable` only when multi-page behavior is actually necessary; small `longtable` blocks have caused split-box failures in this repo.
- `wlpeerj` is single-column with a wide left margin. Do not introduce `table*` or `figure*`; size floats with `\linewidth`.

## Citation and Bibliography Rules

- Use natbib citation commands (`\citep`, `\citet`, etc.).
- Every cited key must exist in `journal_paper/refs.bib`.
- For website-style resources, follow the pattern already in `journal_paper/refs.bib`:
  - use `@misc`
  - use `howpublished = {\url{...}}` for the website address
  - add `note = {Accessed: YYYY-MM-DD}`
  - prefer concise fields instead of report-style metadata
- For organizational or corporate authors in BibTeX, wrap the full name in double braces, for example `author = {{Sentence Transformers}}`, so BibTeX does not invert it into forms such as `Project, R.`.
- Keep bibliography contract exactly:
  - `\bibliography{refs}` and nothing else — `wlpeerj` sets `\bibliographystyle{apalike}`
    (author-year) itself.
  - `refs.bib` needs `\usepackage{url}` in `manuscript.tex` for its `\url{...}` fields.

## Section and Label Rules

- Keep top-level sections as `\section{...}\label{...}`.
- Keep cross-reference labels stable and unique across the manuscript.

## Manuscript Section Boundaries

- Keep `journal_paper/method.tex` focused on the proposed pipeline and workflow design:
  - staged process
  - artifact construction
  - indexing/evaluation logic
  - reporting/reproducibility
- Keep `journal_paper/experiments.tex` focused on the manuscript-specific experimental setup:
  - frozen run scope
  - dataset context and provenance
  - evaluated model roster
  - controlled setup details and limitations
- Keep `journal_paper/results.tex` focused on evidence and interpretation:
  - metric presentation
  - comparative findings
  - tradeoff discussion
  - dataset-specific outcomes
- Do not let `method.tex` absorb result interpretation, metric-equation exposition reserved for Results, or manuscript-snapshot setup details that belong in Experiments.

## Terminology Rule

- In reader-facing paper prose, prefer `paper` over `manuscript` for statements such as `this paper`, `the paper reports`, or `the paper demonstrates`.
- Reserve `manuscript` for repo workflow, source-file instructions, build guidance, and references to the submission artifact as a file/package.
- Avoid report-style traceability language in the main paper body unless it is methodologically necessary.
- In reader-facing paper prose, prefer `practitioner` for the person applying the pipeline to local corpora.
- Avoid mixing `user`, `developer`, and `practitioner` in the paper body unless the distinction is genuinely necessary.
- Reserve `developer` for implementation/repository contexts and `user` for interface/product contexts.

## Method Writing Guidance

- For reusable pipeline descriptions in `method.tex`, prefer generalized wording such as `document collection` unless the file format itself is methodologically important.
- If the manuscript snapshot uses a concrete source format (for example PDFs), mention that as a factual implementation detail in the relevant subsection instead of making the whole method unnecessarily format-specific.
- When a figure presents a finer-grained workflow than the prose, revise the prose to follow the figure sequence explicitly.

## Required Checks Before Claiming Completion

- Run:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1`
- always use `-CompilePdf` flag to run full compile.
- Do not report success if lint/build gates fail.
- The build compiles with **pdflatex** (`wlpeerj` loads inputenc/times/mathptmx). All source is
  ASCII with escaped accents, e.g. `T\"urkiye`; keep it that way rather than pasting UTF-8
  literals.
- `-CompilePdf` exports the submission package to `journal_paper/Peerj Submision/`:
  `latex_source/` (single-file `manuscript.tex` with every `\input` inlined, `refs.bib`, `.bbl`,
  `wlpeerj.cls`, and `Figure1..N.png` numbered in order of appearance and padded to PeerJ's
  900 x 900 px minimum), `latex_source.zip`, and `manuscript.pdf` compiled from `latex_source/`
  itself. The same `FigureN.png` files are referenced by the TEX and uploaded to PeerJ; there is
  no second figure copy.

## Secondary Guidance Skill

- For complex formatting tasks, follow:
  - `codex_skills/latex-template-compliance/SKILL.md`
- Treat skill guidance as helper rules; build/lint gates remain final authority.
