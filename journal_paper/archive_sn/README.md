# Retired Springer Nature (sn-jnl) front matter

The manuscript was reformatted for **PeerJ Computer Science** (`wlpeerj` class) on
2026-10-15, after the *Machine Learning* (Springer, journal 10994) submission was
rejected. This folder keeps the previous Springer version of the *format-specific* files
only:

| File | Was |
|---|---|
| `manuscript_sn.tex` | `journal_paper/manuscript.tex` — `sn-jnl` front matter, `\author*`/`\fnm`/`\sur`, `\affil*` with `\orgdiv`, `\abstract{}` command, `\keywords{}` |
| `declarations_sn.tex` | `journal_paper/declarations.tex` — `\backmatter` plus eight `\bmhead{}` declarations |
| `build_sn.ps1` | `journal_paper/build.ps1` — SN001–SN014 lint rules, `ML_Template/` assets, `manuscript_sn*.tex` wrappers |

The seven section files (`intro.tex` … `conclusion.tex`) and every `tbl_*.tex` fragment are
format-agnostic and were **not** changed by the conversion. They are shared, not duplicated
here.

Nothing in this folder is part of the build. `build.ps1`, `utils/verify_paper_numbers.py`
and the lint gates all glob `journal_paper/*.tex` non-recursively, so these files are
invisible to them.

To restore the Springer build, copy the three files back over their originals (dropping the
`_sn` suffix); `journal_paper/ML_Template/` is still present. The last commit in which the
Springer build was live is `d4d8eac`.
