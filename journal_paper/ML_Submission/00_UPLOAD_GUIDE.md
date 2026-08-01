# Upload guide — *Machine Learning* (Springer, journal 10994)

Submission portal: **Editorial Manager** — <https://www.editorialmanager.com/mach/>

Everything in this folder is ready to upload **except one item you must complete first**
(see *Before you upload*, below).

---

## Before you upload

- [ ] **Fill in the four suggested reviewers** in the boxed placeholder on page 2 of
      `02_information_sheet.pdf`. MLJ requires up to four candidates with name, affiliation,
      email and a one-line justification. Edit `src/information_sheet.tex`, then recompile:
      ```
      cd src && pdflatex information_sheet.tex && pdflatex information_sheet.tex
      copy information_sheet.pdf ..\02_information_sheet.pdf
      ```
      None may be from TED University, a co-author, or a recent collaborator.

- [ ] **Make the GitHub repository public.**
      <https://github.com/kmkarakaya/RagRetrievalBench> currently returns 404 anonymously.
      The manuscript's *Data availability* and *Code availability* statements and two inline
      citations point at it. A referee who clicks that link and hits a 404 in the first five
      minutes forms an opinion that is hard to reverse. This is the single largest gap between
      what the paper claims and what a referee can verify.

- [ ] **Confirm the blinding model** on the live submission-guidelines page. The evidence
      points to single-blind (reviewers see author identities), so author names and
      affiliation are left in the manuscript. If MLJ has moved to double-blind, the front
      matter in `latex_source/manuscript.tex` must be anonymised and the PDF rebuilt.

---

## Upload order

| # | File | Suggested Editorial Manager item type |
|---|---|---|
| 1 | `01_cover_letter.pdf` | Cover Letter |
| 2 | `03_manuscript.pdf` | Manuscript (the PDF reviewers read) |
| 3 | `04_manuscript.tex` | LaTeX Source — or upload `latex_source.zip` instead, see below |
| 4 | `latex_source.zip` | LaTeX Source / Supplementary File |
| 5 | `02_information_sheet.pdf` | Supplementary Material / Attachment |
| 6 | `05_prior_conference_paper_ICCSIS2025.pdf` | Related Manuscript / Supplementary Material |

**On items 3 and 4:** MLJ requires the *original source including all style files and figures*
plus the compiled PDF, at every submission and revision. `latex_source.zip` satisfies this in a
single upload. If the portal will not accept a `.zip`, upload `04_manuscript.tex` plus each of
the 11 PNGs from `latex_source/` individually, together with `sn-jnl.cls`, `sn-basic.bst` and
`refs.bib`.

**On item 6:** upload the prior paper so the editor can see the overlap for themselves rather
than take the cover letter's word for it. The extension is disclosed in three places already —
cover letter, information sheet §5, and manuscript §1 and §2.6.

---

## What is in each file

| File | Description |
|---|---|
| `01_cover_letter.pdf` | One page to the Editors. States the contribution, the fit with MLJ, the ICCSIS 2025 extension with its delta, and that the work is not under review elsewhere. |
| `02_information_sheet.pdf` | Two pages answering MLJ's six required questions: main claim, evidence, 3–5 closest related works, 5 general + 5 specific keywords, conflicts of interest, suggested reviewers. **Reviewer block is a placeholder.** |
| `03_manuscript.pdf` | The compiled manuscript. 47 pages, line-numbered for referees. |
| `04_manuscript.tex` | Single-file LaTeX source, every `\input` inlined — Springer asks for one `.tex` document. |
| `05_prior_conference_paper_ICCSIS2025.pdf` | The preliminary version (ICCSIS 2025, Madrid, 10–11 Aug 2025, pp. 1–6; also published in IJAECS 12(9)). |
| `latex_source/` | Complete recompilable source: `manuscript.tex`, `sn-jnl.cls`, `sn-basic.bst`, `refs.bib`, `manuscript.bbl`, and 11 figure PNGs. |
| `latex_source.zip` | The same 16 files, zipped. |
| `src/` | LaTeX sources for the cover letter and information sheet. **Not for upload** — kept so you can edit and recompile them. |

---

## Verification already performed

| Check | Result |
|---|---|
| `build.ps1` template lint | 0 errors, 0 warnings |
| Undefined citations / references | 0 |
| `.aux` convergence | converged (no "Rerun to get") |
| Page count | 47 |
| `python rag_benchmark.py --verify-paper` | 33 values checked, all agree with pipeline artifacts |
| `git status --porcelain -- datasets/` | empty — frozen run untouched |
| **Package self-test** | `latex_source/` copied to an empty folder with `manuscript.bbl` deleted, then `pdflatex` → `bibtex` → `pdflatex` ×3: 47 pages, 0 undefined, 0 missing files, 0 BibTeX warnings |

The self-test is the one that matters for the upload: it proves the source set is complete and
that the reviewer's or production editor's rebuild will reproduce the same PDF.

---

## Formatting compliance

The manuscript uses the Springer Nature template in `journal_paper/ML_Template/`:

- `\documentclass[pdflatex,sn-basic,lineno]{sn-jnl}` — `sn-basic` without `Numbered` gives
  Springer Basic author–year references, which is MLJ's style; `lineno` prints line numbers
  for referees.
- Springer front matter: `\title[running head]{}`, `\author*[1]{\fnm{} \sur{}}\email{}`,
  `\affil*[1]{\orgdiv{}, \orgname{}, \orgaddress{}}`, `\abstract{}`, `\keywords{}`.
- Back matter: `\backmatter`, `\section*{Declarations}` with `\bmhead{}` subheadings for
  Funding, Competing interests, Ethics approval, Consent for publication, Data availability,
  Materials availability, Code availability, and Author contributions.
- The class supplies `natbib` and `\bibliographystyle{sn-basic}` itself, so neither appears in
  the preamble.

ORCID (0000-0002-9542-6965) is **not** in the LaTeX source — `sn-jnl`'s `\orcid` macro needs an
`Orcidlogo.eps` that does not ship with the template. Enter it in the portal instead.

---

*Package built 2026-08-01 from `journal_paper/build/2026-08-01_15-33-03/`.*
