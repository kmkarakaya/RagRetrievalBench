# LaTeX Compliance Checklist

1. Edited only TeX-first manuscript files (`manuscript.tex`, section `.tex`, `refs.bib`).
2. Kept flat source policy (no nested `\input` or image paths).
3. Verified CAS front matter exists (`\shorttitle`, `\shortauthors`, `\title[mode=title]`, `\author`, `\affiliation`, abstract/highlights/keywords, `\maketitle`).
4. Verified abstract handling for CAS classes:
   - final prose is directly in `manuscript.tex` abstract block
   - no `\input{abstract.tex}` or macro placeholders inside `\begin{abstract}...\end{abstract}`
   - compiled `.abs` file contains prose, not literal filename/token artifacts
5. Verified every table/longtable/figure has both `\caption` and `\label`.
6. Verified table style is template-aligned (`booktabs` rules where possible).
7. Verified all citation keys resolve in `refs.bib`.
8. Verified bibliography lines are `\bibliographystyle{cas-model2-names}` and `\bibliography{refs}`.
9. Ran `build.ps1` and confirmed lint gates pass.
10. Ran `-CompilePdf` when requested and reported any environment blockers.
