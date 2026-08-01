# LaTeX Compliance Checklist

Target: Springer Nature `sn-jnl` for **Machine Learning** (Springer 10994).

1. Edited only TeX-first manuscript files (`manuscript.tex`, section `.tex`, `declarations.tex`, `refs.bib`).
2. Kept flat source policy (no nested `\input` or image paths).
3. Verified Springer front matter exists: `\documentclass[pdflatex,sn-basic,lineno]{sn-jnl}`, `\title`, `\author*`, `\affil*`, `\abstract{...}`, `\keywords{...}`, `\maketitle`, `\bibliography{refs}`.
4. Verified the preamble does **not** contain `\usepackage{natbib}`, `\bibliographystyle{...}`, or a `highlights` environment — the class supplies all three.
5. Verified `amsmath` is still loaded (the class calls `\allowdisplaybreaks` at `\begin{document}`).
6. Verified `declarations.tex` keeps `\backmatter`, `\section*{Declarations}`, and a `\bmhead{}` for each required declaration, using `Not applicable` where a heading does not apply.
7. Verified every table/longtable/figure has both `\caption` and `\label`, plus `\centering`, and that no `table*`/`figure*` was introduced (the class is single-column).
8. Verified table style is template-aligned (`booktabs` rules where possible).
9. Verified all citation keys resolve in `refs.bib`.
10. Ran `build.ps1` and confirmed lint gates pass (0 errors, 0 warnings).
11. Ran `-CompilePdf` when requested; confirmed 0 undefined citations/references and a converged `.aux` (no "Rerun to get").
12. Ran `python rag_benchmark.py --verify-paper` if any manuscript number was touched.
13. Confirmed `git status --porcelain -- datasets/` is empty — the frozen run must not move.
14. Reported the build folder path and the submission file `build/<timestamp>/manuscript_sn_full.tex`.
