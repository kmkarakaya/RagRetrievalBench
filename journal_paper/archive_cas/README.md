# Retired Elsevier CAS front matter

The manuscript was reformatted for **Machine Learning** (Springer, journal 10994) on
2026-08-01. This folder keeps the previous Elsevier CAS version of the *format-specific*
files only:

| File | Was |
|---|---|
| `manuscript_cas.tex` | `journal_paper/manuscript.tex` — `cas-sc` front matter, `highlights`, `\credit`/`\cormark`/`\ead`, `\bibliographystyle{cas-model2-names}` |
| `declarations_cas.tex` | `journal_paper/declarations.tex` — `\printcredits` plus flat `\section*` declarations |
| `build_cas.ps1` | `journal_paper/build.ps1` — `__CAS_CLASS__` substitution, CAS001–CAS016 lint rules, `template/` assets, xelatex |

The seven section files (`intro.tex` … `conclusion.tex`) and every `tbl_*.tex` fragment are
format-agnostic and were **not** changed by the conversion. They are shared, not duplicated
here.

Nothing in this folder is part of the build. `build.ps1`, `utils/verify_paper_numbers.py`
and the lint gates all glob `journal_paper/*.tex` non-recursively, so these files are
invisible to them.

To restore the Elsevier build, copy the three files back over their originals and restore
`journal_paper/template/` (still present). The last commit in which the CAS build was live
is `0fb00b2`.
