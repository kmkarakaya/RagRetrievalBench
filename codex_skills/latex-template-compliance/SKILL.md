---
name: latex-template-compliance
description: Enforce CAS LaTeX manuscript formatting rules for journal_paper TeX-first workflow. Use when editing manuscript.tex, section .tex files, refs.bib, tables, figures, citations, and build.ps1 lint/build checks.
---

# CAS Compliance Workflow

Use this workflow whenever a task touches manuscript content or formatting.

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

## Table/Figure Rules
- Require both `\caption{...}` and `\label{...}` for:
  - `table`, `table*`
  - `longtable`
  - `figure`, `figure*`
- Keep labels unique and meaningful.

## Citation Rules
- Use natbib citation commands (`\citep`, `\citet`, etc.).
- Ensure every cited key exists in `journal_paper/refs.bib`.
- Do not use unresolved placeholder citation styles.

## Required Validation
- Always run:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1`
- If PDF compile is part of request:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1 -CompilePdf`
- Treat build lint failures as blocking defects.

## Quick Checklist
For a concise task checklist, see:
- `references/checklist.md`
