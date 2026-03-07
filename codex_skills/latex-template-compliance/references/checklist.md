# LaTeX Compliance Checklist

1. Edited only TeX-first manuscript files (`manuscript.tex`, section `.tex`, `refs.bib`).
2. Kept flat source policy (no nested `\input` or image paths).
3. Verified every table/longtable/figure has both `\caption` and `\label`.
4. Verified all citation keys resolve in `refs.bib`.
5. Ran `build.ps1` and confirmed lint gates pass.
6. Ran `-CompilePdf` when requested and reported any environment blockers.
