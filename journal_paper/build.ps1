param(
    [ValidateSet("sc", "dc")]
    [string]$Layout = "sc",
    [string]$RunId = "2026-03-05_11-32-49",
    [switch]$CompilePdf
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Assert-Command {
    param([Parameter(Mandatory = $true)][string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command not found: $Name"
    }
}

$PaperDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $PaperDir
$BuildDir = Join-Path $PaperDir "build"
$TemplateDir = Join-Path $PaperDir "template"
$ClassName = if ($Layout -eq "dc") { "cas-dc" } else { "cas-sc" }
$WrapperName = "manuscript_cas_$Layout.tex"
$ResourcePath = "$PaperDir;$RepoRoot\aggregated_reports\$RunId"
$BodyFragmentPath = Join-Path $BuildDir "body_fragment.tex"
$AbstractFragmentPath = Join-Path $BuildDir "abstract_fragment.tex"

$requiredFiles = @(
    (Join-Path $PaperDir "main.md"),
    (Join-Path $PaperDir "refs.md"),
    (Join-Path $PaperDir "abstract.md"),
    (Join-Path $PaperDir "intro.md"),
    (Join-Path $PaperDir "related.md"),
    (Join-Path $PaperDir "method.md"),
    (Join-Path $PaperDir "experiments.md"),
    (Join-Path $PaperDir "results.md"),
    (Join-Path $PaperDir "conculusion.md"),
    (Join-Path $TemplateDir "$ClassName.cls"),
    (Join-Path $TemplateDir "cas-common.sty"),
    (Join-Path $TemplateDir "cas-model2-names.bst")
)

$missing = @($requiredFiles | Where-Object { -not (Test-Path $_) })
if ($missing.Count -gt 0) {
    throw "Missing required files: $($missing -join ', ')"
}

Assert-Command -Name "pandoc"
Assert-Command -Name "python"

New-Item -ItemType Directory -Force $BuildDir | Out-Null

$env:PAPER_DIR = $PaperDir
$env:BUILD_DIR = $BuildDir
$env:CLASS_NAME = $ClassName
$env:WRAPPER_NAME = $WrapperName

# Step 1: Assemble manuscript from main.md manifest
@'
from pathlib import Path
import os
import re

paper = Path(os.environ["PAPER_DIR"])
build = Path(os.environ["BUILD_DIR"])
main_text = (paper / "main.md").read_text(encoding="utf-8")

yaml_match = re.match(r"^---\n.*?\n---\n", main_text, re.S)
if not yaml_match:
    raise SystemExit("main.md is missing a top YAML block")
yaml_block = yaml_match.group(0)

manifest = re.findall(r"^\d+\.\s+`([^`]+\.md)`\s*$", main_text, re.M)
if not manifest:
    raise SystemExit("No section manifest found in main.md")

parts = [yaml_block, "\n"]
for section in manifest:
    section_path = paper / section
    if not section_path.exists():
        raise SystemExit(f"Manifest entry missing: {section}")
    text = section_path.read_text(encoding="utf-8").strip()
    parts.append(f"\n<!-- BEGIN {section} -->\n\n{text}\n\n<!-- END {section} -->\n")

(build / "manuscript_raw.md").write_text("".join(parts), encoding="utf-8")
print("Wrote manuscript_raw.md")
'@ | python -

# Step 2: Convert [Key] to [@Key], normalize adjacent citations, remove abstract block from body
@'
from pathlib import Path
import os
import re

paper = Path(os.environ["PAPER_DIR"])
build = Path(os.environ["BUILD_DIR"])
refs_text = (paper / "refs.md").read_text(encoding="utf-8")
manuscript = (build / "manuscript_raw.md").read_text(encoding="utf-8")

keys = re.findall(r"^\[([A-Za-z][A-Za-z0-9_]*)\]\s*$", refs_text, re.M)
if not keys:
    raise SystemExit("No citation keys found in refs.md")

for key in sorted(set(keys), key=len, reverse=True):
    manuscript = re.sub(rf"\[{re.escape(key)}\]", f"[@{key}]", manuscript)

pattern = re.compile(r"(?:\[@[A-Za-z][A-Za-z0-9_]*\]){2,}")
def collapse(match):
    ids = re.findall(r"@([A-Za-z][A-Za-z0-9_]*)", match.group(0))
    return "[" + "; ".join(f"@{x}" for x in ids) + "]"

manuscript = pattern.sub(collapse, manuscript)
(build / "manuscript_cite.md").write_text(manuscript, encoding="utf-8")

body_only = re.sub(
    r"(?s)\n<!-- BEGIN abstract\.md -->.*?<!-- END abstract\.md -->\n",
    "\n",
    manuscript
)
(build / "manuscript_body_cite.md").write_text(body_only, encoding="utf-8")
print("Wrote manuscript_cite.md and manuscript_body_cite.md")
'@ | python -

# Step 3: Build refs.bib from refs.md
@'
from pathlib import Path
import os
import re

def clean(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`"):
        value = value[1:-1]
    return value.strip()

def esc(value: str) -> str:
    return value.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")

paper = Path(os.environ["PAPER_DIR"])
build = Path(os.environ["BUILD_DIR"])
text = (paper / "refs.md").read_text(encoding="utf-8")
matches = list(re.finditer(r"^\[([A-Za-z][A-Za-z0-9_]*)\]\s*$", text, re.M))

entries = []
for i, match in enumerate(matches):
    key = match.group(1)
    start = match.end()
    end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
    block = text[start:end]
    fields = dict((k.strip(), clean(v)) for k, v in re.findall(r"^\-\s+([a-z_]+):\s*(.+)$", block, re.M))
    if "title" not in fields:
        continue

    ref_type = fields.get("type", "misc")
    bib_type = "misc"
    if ref_type in {"article", "article-preprint"}:
        bib_type = "article"
    elif ref_type in {"conference-paper"}:
        bib_type = "inproceedings"
    elif ref_type in {"report", "dataset-artifact-report"}:
        bib_type = "techreport"

    author = fields.get("authors_or_org", "Unknown")
    title = fields.get("title", key)
    year = fields.get("year", "n.d.")
    publisher = fields.get("venue_or_publisher", "")
    url = fields.get("path_or_url", "")
    note = fields.get("note", "")
    urldate = fields.get("accessed_or_retrieved", "")

    lines = [
        f"@{bib_type}{{{key},",
        f"  author = {{{esc(author)}}},",
        f"  title = {{{esc(title)}}},",
        f"  year = {{{esc(year)}}},"
    ]
    if publisher:
        lines.append(f"  publisher = {{{esc(publisher)}}},")
    if url:
        lines.append(f"  url = {{{esc(url)}}},")
    if urldate:
        lines.append(f"  urldate = {{{esc(urldate)}}},")
    if note:
        lines.append(f"  note = {{{esc(note)}}},")
    lines.append("}")
    entries.append("\n".join(lines))

(build / "refs.bib").write_text("\n\n".join(entries).strip() + "\n", encoding="utf-8")
print("Wrote refs.bib")
'@ | python -

# Step 4: Create body and abstract latex fragments
pandoc (Join-Path $BuildDir "manuscript_body_cite.md") `
    --from markdown+yaml_metadata_block+pipe_tables+raw_tex `
    --to latex `
    --natbib `
    --wrap=none `
    --resource-path="$ResourcePath" `
    --output="$BodyFragmentPath"

pandoc (Join-Path $PaperDir "abstract.md") `
    --from markdown+pipe_tables+raw_tex `
    --to latex `
    --wrap=none `
    --output="$AbstractFragmentPath"

# Step 5: Copy CAS assets to build folder
Copy-Item (Join-Path $TemplateDir "$ClassName.cls") $BuildDir -Force
Copy-Item (Join-Path $TemplateDir "cas-common.sty") $BuildDir -Force
Copy-Item (Join-Path $TemplateDir "cas-model2-names.bst") $BuildDir -Force

# Step 6: Create wrapper tex
@'
from pathlib import Path
import os
import re

paper = Path(os.environ["PAPER_DIR"])
build = Path(os.environ["BUILD_DIR"])
class_name = os.environ["CLASS_NAME"]
wrapper_name = os.environ["WRAPPER_NAME"]

main_text = (paper / "main.md").read_text(encoding="utf-8")
title_match = re.search(r'^title:\s*"(.*)"\s*$', main_text, re.M)
title = title_match.group(1).strip() if title_match else "TODO: Title"

abstract = (build / "abstract_fragment.tex").read_text(encoding="utf-8").strip()
if not abstract:
    abstract = "TODO: Add abstract text."

wrapper = rf"""\documentclass[a4paper,fleqn]{{{class_name}}}
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

(build / wrapper_name).write_text(wrapper, encoding="utf-8")
print(f"Wrote {wrapper_name}")
'@ | python -

if ($CompilePdf) {
    Assert-Command -Name "xelatex"
    Assert-Command -Name "bibtex"
    Push-Location $BuildDir
    try {
        & xelatex -interaction=nonstopmode -halt-on-error $WrapperName | Out-Null
        & bibtex ([System.IO.Path]::GetFileNameWithoutExtension($WrapperName)) | Out-Null
        & xelatex -interaction=nonstopmode -halt-on-error $WrapperName | Out-Null
        & xelatex -interaction=nonstopmode -halt-on-error $WrapperName | Out-Null
    }
    finally {
        Pop-Location
    }
}

Write-Host "Build complete."
Write-Host "  Layout: $Layout"
Write-Host "  Wrapper: $(Join-Path $BuildDir $WrapperName)"
Write-Host "  Bib: $(Join-Path $BuildDir 'refs.bib')"
if ($CompilePdf) {
    Write-Host "  PDF: $(Join-Path $BuildDir ($WrapperName -replace '\.tex$', '.pdf'))"
}
