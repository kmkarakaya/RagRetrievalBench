# Springer Nature `sn-jnl` Template Rules (Repo-Specific Extraction)

Target journal: **Machine Learning** (Springer, journal 10994).

Source files:
- `journal_paper/ML_Template/sn-jnl.cls`
- `journal_paper/ML_Template/sn-article.tex` (annotated sample)
- `journal_paper/ML_Template/user-manual.pdf`
- `journal_paper/ML_Template/bst/sn-basic.bst`

Use these rules as the template baseline for this repository. The retired Elsevier CAS rules are
archived with the files they governed in `journal_paper/archive_cas/`.

## Document Class

```latex
\documentclass[pdflatex,sn-basic,lineno]{sn-jnl}
```

- `sn-basic` **without** the `Numbered` option gives Springer Basic author-year, which is what
  Machine Learning uses. The class then loads `\usepackage[authoryear]{natbib}`, applies
  `\setcitestyle{aysep={}}`, and issues `\bibliographystyle{sn-basic}` itself.
- `lineno` prints margin line numbers for referees (needs `vruler`).
- `referee` would add double line spacing; not currently used.
- The class is pdflatex-oriented. `build.ps1` compiles with pdflatex, not xelatex.

### Packages the class assumes
`sn-jnl` calls `\allowdisplaybreaks` in a `\begin{document}` hook, so **`amsmath` must be
loaded** or the compile dies with `Undefined control sequence`. The repo preamble carries
`graphicx`, `amsmath,amssymb,amsfonts`, and `longtable,booktabs,array,calc`.

## Front Matter Contract

Keep these in `manuscript.tex`:

1. `\title[Running Head]{Full Title}`
2. `\author*[1]{\fnm{First} \sur{Last}}\email{address}` — the starred form marks the
   corresponding author
3. `\affil*[1]{\orgdiv{Department}, \orgname{University}, \orgaddress{\city{City}, \country{Country}}}`
4. `\abstract{...}` — a **command**, not an environment
5. `\keywords{comma, separated, list}`
6. `\maketitle`

### Forbidden in the preamble
The lint gates reject all three because the class already provides them:

| Construct | Why |
|---|---|
| `\usepackage{natbib}` | `sn-jnl` loads natbib; a second load is an option clash |
| `\bibliographystyle{...}` | selected by the documentclass option |
| `\begin{highlights}` | Elsevier-only; Springer has no equivalent |

### Not carried over from CAS
`\shorttitle`, `\shortauthors`, `\title[mode=title]`, `\credit`, `\cormark`, `\cortext`,
`\ead`, `\affiliation[...]{organization=...}`, `\printcredits`. The running head moves into
`\title`'s optional argument; the CRediT roles move to the Author contributions declaration.

### ORCID
`sn-jnl` defines `\orcid{url}` but it expands to `\includegraphics{Orcidlogo.eps}`, and that
file does not ship with the template package. Do not use `\orcid`; enter the ORCID in the
submission portal instead.

## Back Matter Contract

`journal_paper/declarations.tex` is `\input` last, before `\bibliography{refs}`:

```latex
\backmatter
\section*{Declarations}
\bmhead{Funding} ...
\bmhead{Competing interests} ...
\bmhead{Ethics approval and consent to participate} ...
\bmhead{Consent for publication} ...
\bmhead{Data availability} ...
\bmhead{Materials availability} ...
\bmhead{Code availability} ...
\bmhead{Author contributions} ...
```

`\backmatter` unnumbers everything that follows. Use `Not applicable` where a heading does not
apply rather than omitting it.

## Sectioning and Labels
- Prefer `\section{...}\label{...}` for top-level sections.
- Keep labels stable and unique.

## Tables
- `sn-jnl` is single-column: use `table`, never `table*`.
- Size with `\linewidth`.
- `\caption{...}` then `\label{...}`, plus `\centering`.
- `booktabs` rules (`\toprule`, `\midrule`, `\bottomrule`).
- `longtable` is allowed for genuinely multi-page tables and still needs caption and label.

## Figures
- `\begin{figure}`, `\centering`, `\includegraphics[width=0.95\linewidth]{...}`,
  `\caption{...}\label{...}`.
- Never `figure*`.

## Bibliography
- `\bibliography{refs}` and nothing else.
- Author-year natbib commands: `\citep`, `\citet`.
- Every key must resolve in `journal_paper/refs.bib`; the lint gate checks this and suggests
  near-matches on failure.
- To move to numbered references, add `Numbered` to the documentclass options — never add a
  `\bibliographystyle` line.

## Flat Source Policy (Repo Decision)
- Keep manuscript sources and figure assets in `journal_paper/` flat folder.
- Do not use nested paths in `\input{...}` or `\includegraphics{...}`.
- Springer wants a single `.tex` document at submission. `build.ps1` satisfies this by emitting
  `build/<timestamp>/manuscript_sn_full.tex` with every `\input` inlined; submit that file.

## Lint Rule Map (`build.ps1`)

| Rule | Checks |
|---|---|
| SN001 | `sn-jnl` class with the `sn-basic` option |
| SN002–SN008 | `\title`, `\author*`, `\affil*`, `\abstract{`, `\keywords{`, `\maketitle`, `\bibliography{refs}` |
| SN010–SN012 | forbidden `natbib` load, `\bibliographystyle`, `highlights` |
| SN013–SN014 | `\backmatter`, `\section*{Declarations}` |
| SN901–SN902 | warnings: missing declaration subheading, missing `\email` |
| CAS101–CAS103 | every float has `\caption`, `\label`, `\centering` |
| CAS2xx | bibliography well-formedness and citation-key resolution |
| CAS301–CAS305 | flat-source policy for `\input` and `\includegraphics` |

TeX line comments are stripped before the front-matter scans, so commented-out markup does not
trip the gates.

## Build Environment Notes
Packages installed into MiKTeX for `sn-jnl`: `threeparttable`, `appendix`, `amscls` (supplies
`amsthm.sty`). If a compile hangs with a static log, MiKTeX is blocking on an on-the-fly
install: run `pdflatex -disable-installer` to name the missing `.sty`, then `mpm --install=<pkg>`.
