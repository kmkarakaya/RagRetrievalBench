# LaTeX Compliance Checklist

1. Edited only TeX-first manuscript files (`manuscript.tex`, section `.tex`, `refs.bib`).
2. Kept flat source policy (no nested `\input` or image paths).
3. Verified CAS front matter exists (`\shorttitle`, `\shortauthors`, `\title[mode=title]`, `\author`, `\affiliation`, abstract/highlights/keywords, `\maketitle`).
4. Verified every table/longtable/figure has both `\caption` and `\label`.
5. Verified table style is template-aligned (`booktabs` rules where possible).
6. Verified all citation keys resolve in `refs.bib`.
7. Verified bibliography lines are `\bibliographystyle{cas-model2-names}` and `\bibliography{refs}`.
8. Ran `build.ps1` and confirmed lint gates pass.
9. Ran `-CompilePdf` when requested and reported any environment blockers.
