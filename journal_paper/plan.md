# Reusable Journal Writing Plan (TeX-First)

## Purpose and Positioning
The manuscript contribution is an end-to-end embedding benchmarking pipeline for local datasets, focused on practical model selection.

Positioning rule:
- This is a pipeline utility paper, not a universal best-model paper.

Primary objective:
- Demonstrate a reusable local evaluation workflow.
- Generate automatic benchmarking reports across multiple quality and runtime metrics.
- Support dataset-specific model selection with cross-dataset comparison.
- Demonstrate with 3 datasets and 5 embedding models.

## Canonical Source Structure (Flat TeX)
Source of truth is now TeX-first in `journal_paper/`.

Master file:
- `manuscript.tex`

Section files:
- `abstract.tex`
- `intro.tex`
- `related.tex`
- `method.tex`
- `experiments.tex`
- `results.tex`
- `conclusion.tex`

References:
- `refs.bib` (direct BibTeX source)

Layout rule:
- Keep manuscript `.tex` files and image files in the same flat folder (`journal_paper/`).
- Do not use source subfolders for sections or figures.

## Build Contract
Use:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1 -CompilePdf
```

Options:
- `-Layout sc|dc`
- `-CompilePdf`

Build behavior:
- Creates timestamped run folder under `journal_paper/build/`.
- Copies flat-source `.tex`, images, and `refs.bib`.
- Copies CAS assets from `journal_paper/template/`.
- Produces:
  - wrapper: `manuscript_cas_<layout>.tex`
  - inlined debug file: `manuscript_cas_<layout>_full.tex`
  - PDF/log/aux artifacts (when compile enabled)

## Citation and Reference Contract
- Use natbib citation commands in TeX (`\citep{...}`, `\citet{...}`).
- Every citation key must resolve in `refs.bib`.
- Do not use placeholder A/E numeric evidence tags as citation substitutes.
- Keep key names stable after first use.

## Frozen Evidence Snapshot (Current Baseline)
- Aggregate run id: `2026-03-05_11-32-49`
- Dataset runs:
  - `education_eng`: `2026-03-05_11-27-28`
  - `education_tr`: `2026-03-05_11-29-07`
  - `law_tr`: `2026-03-05_11-30-27`

Dataset provenance baseline:
- TED source (`education_eng`, `education_tr`): `https://www.tedu.edu.tr/en/regulations-and-guidelines-education`
- BDDK source (`law_tr`): `https://www.bddk.org.tr/Mevzuat/Liste/49`
- Retrieval date used in manuscript: `01/01/2026`

Rule:
- Do not mix numeric claims from different run timestamps in one manuscript snapshot.

## Writing Workflow
1. Edit section `.tex` files directly.
2. Keep tables/figures in section files with explicit `\caption{}` and `\label{}`.
3. Keep model names, dataset ids, and metric labels consistent:
   - datasets: `education_eng`, `education_tr`, `law_tr`
   - metrics: `MAP@10`, `Recall@10`, `Precision@10`, `NDCG@10`, `MRR@10`, `Success@10`
4. Rebuild with `build.ps1`.
5. Verify PDF/log in latest timestamped build folder.

## Quality Gates
1. Scope gate:
   - no universal superiority claim
   - conclusions remain dataset/setup bounded
2. Consistency gate:
   - manuscript consistently states 3 datasets and 5 models
3. Citation gate:
   - all citation keys resolve in `refs.bib`
4. Provenance gate:
   - TED/BDDK sources and retrieval date remain explicit
5. Build gate:
   - `build.ps1` succeeds for wrapper generation
   - PDF compile succeeds when MiKTeX environment is healthy

## Practical Verification Commands
```powershell
rg --line-number "2026-03-05_11-32-49|2026-03-05_11-27-28|2026-03-05_11-29-07|2026-03-05_11-30-27" journal_paper/*.tex
rg --line-number "tedu.edu.tr/en/regulations-and-guidelines-education|bddk.org.tr/Mevzuat/Liste/49|01/01/2026" journal_paper/*.tex
rg --line-number "\\\\citep\\{|\\\\citet\\{" journal_paper/*.tex
powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1
```

## Changelog
| Date | Change |
|---|---|
| 2026-03-06 | Initialized journal plan with frozen run evidence and pipeline-first framing. |
| 2026-03-07 | Migrated manuscript workflow to TeX-first flat source (`manuscript.tex` + section `.tex` + direct `refs.bib`). |
