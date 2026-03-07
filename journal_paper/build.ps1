param(
    [ValidateSet("sc", "dc")]
    [string]$Layout = "sc",
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

function Invoke-CheckedExternal {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$ArgumentList,
        [Parameter(Mandatory = $true)][string]$StepName
    )
    & $FilePath @ArgumentList
    if ($LASTEXITCODE -ne 0) {
        throw "$StepName failed with exit code $LASTEXITCODE."
    }
}

$PaperDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BuildRoot = Join-Path $PaperDir "build"
$TemplateDir = Join-Path $PaperDir "template"
$ClassName = if ($Layout -eq "dc") { "cas-dc" } else { "cas-sc" }
$WrapperName = "manuscript_cas_$Layout.tex"
$FullWrapperName = "manuscript_cas_${Layout}_full.tex"
$MasterTexPath = Join-Path $PaperDir "manuscript.tex"
$BibPath = Join-Path $PaperDir "refs.bib"

$requiredFiles = @(
    $MasterTexPath,
    $BibPath,
    (Join-Path $TemplateDir "$ClassName.cls"),
    (Join-Path $TemplateDir "cas-common.sty"),
    (Join-Path $TemplateDir "cas-model2-names.bst")
)

$missing = @($requiredFiles | Where-Object { -not (Test-Path $_) })
if ($missing.Count -gt 0) {
    throw "Missing required files: $($missing -join ', ')"
}

Assert-Command -Name "python"

New-Item -ItemType Directory -Force $BuildRoot | Out-Null
$BuildTimestampBase = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$BuildTimestamp = $BuildTimestampBase
$BuildDir = Join-Path $BuildRoot $BuildTimestamp
$suffix = 1
while (Test-Path $BuildDir) {
    $BuildTimestamp = "{0}_{1:D2}" -f $BuildTimestampBase, $suffix
    $BuildDir = Join-Path $BuildRoot $BuildTimestamp
    $suffix++
}
New-Item -ItemType Directory -Force $BuildDir | Out-Null

Write-Host "Build folder (current run): $BuildDir"

# Lint gates: template compliance checks before any wrapper generation.
$env:PAPER_DIR = $PaperDir
@'
from pathlib import Path
import os
import re

paper = Path(os.environ["PAPER_DIR"])
master = paper / "manuscript.tex"
refs = paper / "refs.bib"
tex_files = sorted(paper.glob("*.tex"))

if not master.exists():
    raise SystemExit("Lint failed: manuscript.tex not found.")
if not refs.exists():
    raise SystemExit("Lint failed: refs.bib not found.")
if not tex_files:
    raise SystemExit("Lint failed: no .tex source files found in journal_paper root.")

bib_text = refs.read_text(encoding="utf-8")
bib_keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bib_text))
if not bib_keys:
    raise SystemExit("Lint failed: refs.bib has no BibTeX entries.")
if len(bib_keys) != len(re.findall(r"@\w+\s*\{", bib_text)):
    raise SystemExit("Lint failed: duplicate or malformed BibTeX keys in refs.bib.")

issues = []
cite_keys_used = set()
existing_files = {p.name for p in paper.iterdir() if p.is_file()}
allowed_image_exts = [".pdf", ".png", ".jpg", ".jpeg", ".eps"]

cite_re = re.compile(r"\\cite[a-zA-Z*]*(?:\[[^\]]*\])*\{([^}]*)\}")
input_re = re.compile(r"\\input\{([^}]+)\}")
include_re = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
env_re = re.compile(r"\\begin\{(table\*?|longtable|figure\*?)\}(.*?)\\end\{\1\}", re.S)

def has_caption(block: str) -> bool:
    return bool(re.search(r"\\caption(?:\[[^\]]*\])?\{", block))

def has_label(block: str) -> bool:
    return bool(re.search(r"\\label\{", block))

for tex_path in tex_files:
    text = tex_path.read_text(encoding="utf-8")

    for m in cite_re.finditer(text):
        keys = [k.strip() for k in m.group(1).split(",") if k.strip()]
        for key in keys:
            cite_keys_used.add(key)

    for m in input_re.finditer(text):
        target = m.group(1).strip()
        if "/" in target or "\\" in target:
            issues.append(f"{tex_path.name}: nested input path is not allowed: {target}")
            continue
        if not target.lower().endswith(".tex"):
            target += ".tex"
        if target not in existing_files:
            issues.append(f"{tex_path.name}: missing input target: {target}")

    for m in include_re.finditer(text):
        target = m.group(1).strip()
        if "/" in target or "\\" in target:
            issues.append(f"{tex_path.name}: nested includegraphics path is not allowed: {target}")
            continue
        if "." in Path(target).name:
            if target not in existing_files:
                issues.append(f"{tex_path.name}: includegraphics file not found: {target}")
        else:
            matches = [target + ext for ext in allowed_image_exts if (target + ext) in existing_files]
            if not matches:
                issues.append(f"{tex_path.name}: includegraphics target not found (with allowed extensions): {target}")

    env_idx = 0
    for env_match in env_re.finditer(text):
        env_idx += 1
        env_name = env_match.group(1)
        block = env_match.group(0)
        if env_name.startswith("figure"):
            if not has_caption(block):
                issues.append(f"{tex_path.name}: figure #{env_idx} missing \\caption{{...}}")
            if not has_label(block):
                issues.append(f"{tex_path.name}: figure #{env_idx} missing \\label{{...}}")
        else:
            if not has_caption(block):
                issues.append(f"{tex_path.name}: table/longtable #{env_idx} missing \\caption{{...}}")
            if not has_label(block):
                issues.append(f"{tex_path.name}: table/longtable #{env_idx} missing \\label{{...}}")

missing_cites = sorted(k for k in cite_keys_used if k not in bib_keys)
for key in missing_cites:
    issues.append(f"Missing BibTeX key in refs.bib: {key}")

if issues:
    msg = "Lint failed with rule violations:\\n" + "\\n".join(f"- {x}" for x in issues)
    raise SystemExit(msg)

print("Lint checks passed: template/rule gates are satisfied.")
'@ | python -

# Copy flat-source TeX files.
Get-ChildItem -Path $PaperDir -File -Filter "*.tex" | ForEach-Object {
    Copy-Item $_.FullName $BuildDir -Force
}

# Copy direct bibliography source.
Copy-Item $BibPath (Join-Path $BuildDir "refs.bib") -Force

# Copy image assets from flat source folder.
$imageExtensions = @("*.png", "*.jpg", "*.jpeg", "*.pdf", "*.eps")
foreach ($ext in $imageExtensions) {
    Get-ChildItem -Path $PaperDir -File -Filter $ext | ForEach-Object {
        Copy-Item $_.FullName $BuildDir -Force
    }
}

# Copy required CAS template assets.
Copy-Item (Join-Path $TemplateDir "$ClassName.cls") $BuildDir -Force
Copy-Item (Join-Path $TemplateDir "cas-common.sty") $BuildDir -Force
Copy-Item (Join-Path $TemplateDir "cas-model2-names.bst") $BuildDir -Force
if (Test-Path (Join-Path $TemplateDir "thumbnails")) {
    Copy-Item (Join-Path $TemplateDir "thumbnails") $BuildDir -Recurse -Force
}

# Generate layout-specific wrapper from manuscript.tex.
$masterText = Get-Content -Path $MasterTexPath -Raw
if ($masterText -notmatch "__CAS_CLASS__") {
    throw "manuscript.tex must contain __CAS_CLASS__ token in \\documentclass{...}."
}
$wrapperText = $masterText -replace "__CAS_CLASS__", $ClassName
$WrapperPath = Join-Path $BuildDir $WrapperName
Set-Content -Path $WrapperPath -Value $wrapperText -Encoding UTF8

# Generate full/inlined wrapper for debugging and inspection.
$env:BUILD_DIR = $BuildDir
$env:WRAPPER_NAME = $WrapperName
$env:FULL_WRAPPER_NAME = $FullWrapperName
@'
from pathlib import Path
import os
import re

build = Path(os.environ["BUILD_DIR"])
wrapper_name = os.environ["WRAPPER_NAME"]
full_wrapper_name = os.environ["FULL_WRAPPER_NAME"]

input_re = re.compile(r"\\input\{([^}]+)\}")

def normalize_tex_name(name: str) -> str:
    name = name.strip()
    if "/" in name or "\\" in name:
        raise SystemExit(
            f"Nested input path is not allowed in flat-source mode: {name}"
        )
    if not name.lower().endswith('.tex'):
        name += '.tex'
    return name

def inline_inputs(tex_text: str, stack: list[str]) -> str:
    def repl(m: re.Match) -> str:
        target = normalize_tex_name(m.group(1))
        if target in stack:
            raise SystemExit(f"Recursive \\input detected: {' -> '.join(stack + [target])}")
        path = build / target
        if not path.exists():
            raise SystemExit(f"Missing input file in build folder: {target}")
        child = path.read_text(encoding='utf-8')
        return inline_inputs(child, stack + [target])

    return input_re.sub(repl, tex_text)

wrapper_text = (build / wrapper_name).read_text(encoding='utf-8')
full_text = inline_inputs(wrapper_text, [wrapper_name])
(build / full_wrapper_name).write_text(full_text, encoding='utf-8')
print(f"Wrote {wrapper_name} and {full_wrapper_name}")
'@ | python -

if ($CompilePdf) {
    Assert-Command -Name "xelatex"
    Assert-Command -Name "bibtex"

    $texBaseName = [System.IO.Path]::GetFileNameWithoutExtension($WrapperName)
    Push-Location $BuildDir
    try {
        Invoke-CheckedExternal -FilePath "xelatex" -ArgumentList @("-interaction=nonstopmode", "-halt-on-error", $WrapperName) -StepName "XeLaTeX pass 1"
        Invoke-CheckedExternal -FilePath "bibtex" -ArgumentList @($texBaseName) -StepName "BibTeX pass"
        Invoke-CheckedExternal -FilePath "xelatex" -ArgumentList @("-interaction=nonstopmode", "-halt-on-error", $WrapperName) -StepName "XeLaTeX pass 2"
        Invoke-CheckedExternal -FilePath "xelatex" -ArgumentList @("-interaction=nonstopmode", "-halt-on-error", $WrapperName) -StepName "XeLaTeX pass 3"
    }
    finally {
        Pop-Location
    }
}

$pdfPath = Join-Path $BuildDir ($WrapperName -replace '\.tex$', '.pdf')

Write-Host "Build complete."
Write-Host "  Layout: $Layout"
Write-Host "  Build folder: $BuildDir"
Write-Host "  Wrapper: $(Join-Path $BuildDir $WrapperName)"
Write-Host "  Full wrapper: $(Join-Path $BuildDir $FullWrapperName)"
Write-Host "  Bib: $(Join-Path $BuildDir 'refs.bib')"
if ($CompilePdf) {
    Write-Host "  PDF: $pdfPath"
} else {
    Write-Host "  PDF: not generated (use -CompilePdf)"
}
