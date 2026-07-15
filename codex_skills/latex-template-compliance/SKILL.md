---
name: latex-template-compliance
description: Enforce Elsevier CAS template rules for journal_paper TeX-first workflow. Use when editing manuscript.tex, section .tex files, refs.bib, tables, figures, front matter, citations, and build.ps1 lint/build checks.
---

# CAS Compliance Workflow

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
- Use CAS class via `__CAS_CLASS__` token in `manuscript.tex`.
- Keep section includes via `\input{...}` with flat filenames only.
- Keep figure assets in the same flat folder and reference with flat names.
- Keep CAS front matter blocks present in `manuscript.tex`:
  - `\shorttitle{...}`
  - `\shortauthors{...}`
  - `\title[mode=title]{...}`
  - at least one `\author[...]` and matching `\affiliation[...]`
  - `\begin{abstract}...\end{abstract}`
  - `\begin{highlights}...\end{highlights}`
  - `\begin{keywords}...\end{keywords}`
  - `\maketitle`
- Keep bibliography contract:
  - `\bibliographystyle{cas-model2-names}`
  - `\bibliography{refs}`
- Abstract handling rule (critical for CAS `sc` and `dc` layouts):
  - In this template family, the `abstract` environment is written to `\jobname.abs` via `verbatimwrite` (`cas-common.sty`).
  - Keep final abstract prose as literal text inside `\begin{abstract}...\end{abstract}` in `manuscript.tex`.
  - Do not place `\input{abstract.tex}` or custom macro calls inside the abstract block; these can render as literal tokens (for example `abstract.tex`) in the PDF.
  - If `journal_paper/abstract.tex` is used as a drafting helper, manually synchronize its final text into the abstract block in `manuscript.tex` before running builds.
  - After compile, verify `journal_paper/build/<timestamp>/manuscript_cas_<layout>.abs` contains prose content, not filename or macro artifacts.

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
- Prefer regular `table` environments for short manuscript tables. Use `longtable` only when genuine multi-page behavior is needed; small `longtable` blocks in this repo have triggered XeLaTeX split-box failures after unrelated layout changes.

## Citation Rules
- Use natbib citation commands (`\citep`, `\citet`, etc.).
- Ensure every cited key exists in `journal_paper/refs.bib`.
- Do not use unresolved placeholder citation styles.
- Keep key names stable once introduced; avoid silent key renames.
- For website-style resources, follow the local CAS template example in `journal_paper/template/cas-refs.bib`:
  - use `@misc`
  - use `howpublished = {\url{...}}`
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
- For layout-sensitive edits involving tables, figures, captions, or section reflow, prefer running `-CompilePdf` even if the user did not explicitly ask for it, because lint-only checks may miss XeLaTeX pagination and float-placement failures.
- Treat build lint failures as blocking defects.

## Quick Checklist
For a concise task checklist, see:
- `references/checklist.md`
