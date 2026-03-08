# CAS Template Rules (Repo-Specific Extraction)

Source files:
- `journal_paper/template/cas-sc-template.tex`
- `journal_paper/template/cas-dc-template.tex`
- `journal_paper/template/cas-sc-sample.tex`
- `journal_paper/template/cas-dc-sample.tex`

Use these rules as the template baseline for this repository.

## Front Matter Contract
Keep these blocks in `manuscript.tex`:

1. `\shorttitle{...}`
2. `\shortauthors{...}`
3. `\title[mode=title]{...}`
4. One or more `\author[...]` entries
5. Matching `\affiliation[...]` entries
6. Author contact metadata as needed:
   - `\ead{...}`
   - `\ead[url]{...}`
   - `\cortext[...]` for corresponding author
7. `\begin{abstract}...\end{abstract}`
8. `\begin{highlights}...\end{highlights}`
9. `\begin{keywords}...\end{keywords}`
10. `\maketitle`

## Sectioning and Labels
- Prefer `\section{...}\label{...}` style for top-level sections.
- Keep labels stable and unique.

## Tables
Template examples use:
- `\begin{table}[width=.9\linewidth,cols=...,pos=...]`
- `\begin{tabular*}{\tblwidth}{...}`
- `\toprule`, `\midrule`, `\bottomrule`
- required `\caption{...}\label{...}`

Repo allowance:
- `longtable` is allowed for multi-page tables.
- For `longtable`, still require:
  - `\caption{...}\label{...}`
  - `booktabs` rules where practical.

## Figures
Template examples use:
- `\begin{figure}`
- `\centering`
- `\includegraphics[width=.9\textwidth]{...}`
- `\caption{...}\label{...}`

## Bibliography
Keep:
- `\bibliographystyle{cas-model2-names}`
- `\bibliography{refs}`

Use natbib citation commands and ensure all keys resolve in `refs.bib`.

## Flat Source Policy (Repo Decision)
- Keep manuscript sources and figure assets in `journal_paper/` flat folder.
- Do not use nested paths in `\input{...}` or `\includegraphics{...}`.
