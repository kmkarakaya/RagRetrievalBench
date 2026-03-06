# Markdown to LaTeX Build Pipeline (Template-Ready)

## Objective
Convert the modular manuscript markdown files into a journal-ready LaTeX build using:
- semantic citation keys in markdown (`[Key]`)
- `refs.md` as the only citation metadata source
- a concrete target journal template

This pipeline is deterministic and build-generated (no manual copy/paste).

## Inputs and Outputs
- Inputs:
  - `journal_paper/main.md` (YAML + section order manifest)
  - section files: `abstract.md`, `intro.md`, `related.md`, `method.md`, `experiments.md`, `results.md`, `conculusion.md`
  - `journal_paper/refs.md` (canonical reference metadata)
  - journal template assets (see template contract below)
- Outputs:
  - `journal_paper/build/manuscript_raw.md`
  - `journal_paper/build/manuscript_cite.md`
  - `journal_paper/build/manuscript_body_cite.md` (abstract removed)
  - `journal_paper/build/refs.bib`
  - `journal_paper/build/manuscript_cas_sc.tex` (for current Elsevier CAS template)
  - optional PDF (if TeX is correctly installed)

## Template Compatibility (Current Repository)
Detected template package: Elsevier CAS (`cas-sc.cls`, `cas-dc.cls`, `cas-sc-template.tex`, `cas-dc-template.tex`).

Important compatibility rule:
- `cas-sc-template.tex` and `cas-dc-template.tex` are not Pandoc templates (they do not contain `$body$` placeholders).
- Therefore, do not pass CAS sample/template files directly via `pandoc --template=...` expecting markdown insertion.
- For CAS, generate LaTeX fragments with Pandoc, then wrap them in a CAS class document.

Citation backend rule for CAS:
- Use `--natbib` and BibTeX style `cas-model2-names.bst` (author-year).

## Step 0: Preflight Checks
Run from repository root:

```powershell
$ErrorActionPreference = "Stop"

# Required files
$required = @(
  "journal_paper/main.md",
  "journal_paper/refs.md",
  "journal_paper/abstract.md",
  "journal_paper/intro.md",
  "journal_paper/related.md",
  "journal_paper/method.md",
  "journal_paper/experiments.md",
  "journal_paper/results.md",
  "journal_paper/conculusion.md"
)
$missing = $required | Where-Object { -not (Test-Path $_) }
if ($missing.Count -gt 0) { throw "Missing required files: $($missing -join ', ')" }

# Tools
pandoc --version | Out-Null
python --version | Out-Null

# CAS template assets
$casRequired = @(
  "journal_paper/template/cas-sc.cls",
  "journal_paper/template/cas-common.sty",
  "journal_paper/template/cas-model2-names.bst"
)
$casMissing = $casRequired | Where-Object { -not (Test-Path $_) }
if ($casMissing.Count -gt 0) { throw "Missing CAS assets: $($casMissing -join ', ')" }
```

Optional TeX check (for PDF stage):

```powershell
latexmk -v
xelatex --version
```

## Step 1: Assemble `main.md` + Section Files
This preserves YAML metadata from `main.md` and concatenates sections by manifest order.

```powershell
New-Item -ItemType Directory -Force journal_paper/build | Out-Null

@'
from pathlib import Path
import re

root = Path("journal_paper")
build = root / "build"

main_text = (root / "main.md").read_text(encoding="utf-8")
yaml_match = re.match(r"^---\n.*?\n---\n", main_text, re.S)
if not yaml_match:
    raise SystemExit("main.md is missing a top YAML block.")
yaml_block = yaml_match.group(0)

manifest = re.findall(r"^\d+\.\s+`([^`]+\.md)`\s*$", main_text, re.M)
if not manifest:
    raise SystemExit("No section manifest found in main.md.")

parts = [yaml_block, "\n"]
for section in manifest:
    p = root / section
    if not p.exists():
        raise SystemExit(f"Manifest entry missing: {section}")
    text = p.read_text(encoding="utf-8").strip()
    if not text:
        print(f"WARNING: section is empty: {section}")
    parts.append(f"\n<!-- BEGIN {section} -->\n\n{text}\n\n<!-- END {section} -->\n")

(build / "manuscript_raw.md").write_text("".join(parts), encoding="utf-8")
print("Wrote journal_paper/build/manuscript_raw.md")
'@ | python -
```

## Step 2: Convert In-Text Citation Keys to Pandoc Cite Syntax
Convert only keys defined in `refs.md`: `[Key] -> [@Key]`.

```powershell
@'
from pathlib import Path
import re

root = Path("journal_paper")
build = root / "build"
refs_text = (root / "refs.md").read_text(encoding="utf-8")
manuscript = (build / "manuscript_raw.md").read_text(encoding="utf-8")

keys = re.findall(r"^\[([A-Za-z][A-Za-z0-9_]*)\]\s*$", refs_text, re.M)
if not keys:
    raise SystemExit("No citation keys found in refs.md")

for key in sorted(set(keys), key=len, reverse=True):
    manuscript = re.sub(rf"\[{re.escape(key)}\]", f"[@{key}]", manuscript)

# Normalize adjacent citations: [@A][@B] -> [@A; @B]
pattern = re.compile(r"(?:\[@[A-Za-z][A-Za-z0-9_]*\]){2,}")
def collapse(match):
    ids = re.findall(r"@([A-Za-z][A-Za-z0-9_]*)", match.group(0))
    return "[" + "; ".join(f"@{x}" for x in ids) + "]"
manuscript = pattern.sub(collapse, manuscript)

(build / "manuscript_cite.md").write_text(manuscript, encoding="utf-8")
print("Wrote journal_paper/build/manuscript_cite.md")

# Remove abstract block from body manuscript to avoid duplicate abstract in CAS output
body_only = re.sub(
    r"(?s)\n<!-- BEGIN abstract\.md -->.*?<!-- END abstract\.md -->\n",
    "\n",
    manuscript
)
(build / "manuscript_body_cite.md").write_text(body_only, encoding="utf-8")
print("Wrote journal_paper/build/manuscript_body_cite.md")
'@ | python -
```

## Step 3: Generate `build/refs.bib` from `refs.md`
Use this deterministic parser (supports current `refs.md` structure).

```powershell
@'
from pathlib import Path
import re

def clean(v: str) -> str:
    v = v.strip()
    if v.startswith("`") and v.endswith("`"):
        v = v[1:-1]
    return v.strip()

def esc(v: str) -> str:
    return v.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")

root = Path("journal_paper")
text = (root / "refs.md").read_text(encoding="utf-8")
keys = list(re.finditer(r"^\[([A-Za-z][A-Za-z0-9_]*)\]\s*$", text, re.M))

entries = []
for i, m in enumerate(keys):
    key = m.group(1)
    start = m.end()
    end = keys[i + 1].start() if i + 1 < len(keys) else len(text)
    block = text[start:end]
    fields = dict((k.strip(), clean(v)) for k, v in re.findall(r"^\-\s+([a-z_]+):\s*(.+)$", block, re.M))
    if "title" not in fields:
        continue
    rtype = fields.get("type", "misc")
    bibtype = "misc"
    if rtype in {"article", "article-preprint"}:
        bibtype = "article"
    elif rtype in {"conference-paper"}:
        bibtype = "inproceedings"
    elif rtype in {"report", "dataset-artifact-report"}:
        bibtype = "techreport"

    author = fields.get("authors_or_org", "Unknown")
    title = fields.get("title", key)
    year = fields.get("year", "n.d.")
    venue = fields.get("venue_or_publisher", "")
    url = fields.get("path_or_url", "")
    note = fields.get("note", "")
    accessed = fields.get("accessed_or_retrieved", "")

    bib = [f"@{bibtype}{{{key},",
           f"  author = {{{esc(author)}}},",
           f"  title = {{{esc(title)}}},",
           f"  year = {{{esc(year)}}},"]
    if venue:
        bib.append(f"  publisher = {{{esc(venue)}}},")
    if url:
        bib.append(f"  url = {{{esc(url)}}},")
    if accessed:
        bib.append(f"  urldate = {{{esc(accessed)}}},")
    if note:
        bib.append(f"  note = {{{esc(note)}}},")
    bib.append("}")
    entries.append("\n".join(bib))

out = "\n\n".join(entries).strip() + "\n"
(root / "build" / "refs.bib").write_text(out, encoding="utf-8")
print("Wrote journal_paper/build/refs.bib")
'@ | python -
```

## Step 4: Render LaTeX for the Given Template
### CAS-Ready Path (Recommended for This Repository)
1) Generate body and abstract fragments from markdown:

```powershell
pandoc journal_paper/build/manuscript_body_cite.md `
  --from markdown+yaml_metadata_block+pipe_tables+raw_tex `
  --to latex `
  --natbib `
  --wrap=none `
  --resource-path='journal_paper;aggregated_reports/2026-03-05_11-32-49' `
  --output=journal_paper/build/body_fragment.tex

pandoc journal_paper/abstract.md `
  --from markdown+pipe_tables+raw_tex `
  --to latex `
  --wrap=none `
  --output=journal_paper/build/abstract_fragment.tex
```

2) Create CAS wrapper document (`manuscript_cas_sc.tex`) and copy required class/style assets:

```powershell
Copy-Item journal_paper/template/cas-sc.cls journal_paper/build -Force
Copy-Item journal_paper/template/cas-common.sty journal_paper/build -Force
Copy-Item journal_paper/template/cas-model2-names.bst journal_paper/build -Force

@'
from pathlib import Path
import re

root = Path("journal_paper")
build = root / "build"
main_text = (root / "main.md").read_text(encoding="utf-8")
title_match = re.search(r'^title:\s*"(.*)"\s*$', main_text, re.M)
title = title_match.group(1).strip() if title_match else "TODO: Title"

abstract = (build / "abstract_fragment.tex").read_text(encoding="utf-8").strip()
if not abstract:
    abstract = "TODO: Add abstract text."

wrapper = rf"""\documentclass[a4paper,fleqn]{{cas-sc}}
\usepackage[authoryear,longnamesfirst]{{natbib}}
\begin{{document}}
\shorttitle{{{title}}}
\shortauthors{{TODO: Authors}}
\title[mode=title]{{{title}}}
\author[1]{{TODO: Author Name}}
\ead{{TODO: email}}
\affiliation[1]{{organization={{TODO: Organization}},city={{TODO: City}},country={{TODO: Country}}}}
\begin{{abstract}}
{abstract}
\end{{abstract}}
\begin{{highlights}}
\item TODO: highlight 1
\item TODO: highlight 2
\item TODO: highlight 3
\end{{highlights}}
\begin{{keywords}}
embedding benchmarking \sep retrieval \sep model selection \sep local dataset
\end{{keywords}}
\maketitle
\input{{body_fragment.tex}}
\bibliographystyle{{cas-model2-names}}
\bibliography{{refs}}
\end{{document}}
"""

(build / "manuscript_cas_sc.tex").write_text(wrapper, encoding="utf-8")
print("Wrote journal_paper/build/manuscript_cas_sc.tex")
'@ | python -
```

## Step 5: Optional PDF Build
If TeX is initialized correctly:

```powershell
Push-Location journal_paper/build
latexmk -pdf -interaction=nonstopmode manuscript_cas_sc.tex
Pop-Location
```

If TeX is not initialized, stop at `.tex` output (still valid for journal submission systems that compile server-side).

## Validation Checklist (Correctness + Completeness)
Run after each build:

```powershell
# Forbidden citation styles must not exist
rg --line-number "\[[AE][0-9]+\]|\[[0-9]+\]" journal_paper/build/manuscript_cite.md

# All key-style citations should already be converted to [@Key] in compiled markdown
rg --line-number "\[[A-Za-z][A-Za-z0-9_]*\]" journal_paper/build/manuscript_cite.md

# Bibliography output exists and is non-empty
Get-Item journal_paper/build/refs.bib | Select-Object FullName,Length

# CAS LaTeX outputs exist
Get-Item journal_paper/build/body_fragment.tex | Select-Object FullName,Length
Get-Item journal_paper/build/manuscript_body_cite.md | Select-Object FullName,Length
Get-Item journal_paper/build/manuscript_cas_sc.tex | Select-Object FullName,Length
```

Expected:
- first `rg` returns no matches
- second `rg` returns no matches (except intentional non-citation bracket tokens, if any)
- `refs.bib`, `manuscript_body_cite.md`, `body_fragment.tex`, and `manuscript_cas_sc.tex` are present and non-empty

## Notes for This Repository
- Current journal template package is Elsevier CAS; use the CAS-ready path above.
- `main.md` already defines `bibliography: build/refs.bib`, but CAS wrapper frontmatter fields must still be filled manually.
- Citation keys are semantic and defined in `refs.md`.
- `abstract.md` currently exists but may be empty; fill it before journal submission build.
- Frozen evidence sources are in `aggregated_reports/2026-03-05_11-32-49/` and dataset raw JSON report folders.
