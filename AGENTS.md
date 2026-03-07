# Codex Project Rules (Non-Negotiable)

These rules apply to all Codex sessions in this repository.

## Primary Manuscript Workflow
- Always follow Elsevier CAS template conventions from `journal_paper/template/`.
- Use TeX-first sources only:
  - `journal_paper/manuscript.tex`
  - `journal_paper/*.tex` section files
  - `journal_paper/refs.bib`
- Do not reintroduce markdown-to-latex manuscript assembly.

## Flat Folder Policy
- Keep manuscript `.tex` files and image files in `journal_paper/` (flat source folder).
- Do not use nested source paths in `\input{...}` or `\includegraphics{...}`.

## Table/Figure Rules
- Every `table`, `longtable`, and `figure` environment must include:
  - `\caption{...}`
  - `\label{...}`
- Keep labels unique and citation keys resolvable in `refs.bib`.

## Required Checks Before Claiming Completion
- Run:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1`
- If `-CompilePdf` is requested, run full compile.
- Do not report success if lint/build gates fail.

## Secondary Guidance Skill
- For complex formatting tasks, follow:
  - `codex_skills/latex-template-compliance/SKILL.md`
- Treat skill guidance as helper rules; build/lint gates remain final authority.
