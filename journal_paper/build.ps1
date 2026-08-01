# Builds the Springer Nature (sn-jnl) manuscript for Machine Learning (journal 10994).
#
# The retired Elsevier CAS build lives in archive_cas/build_cas.ps1 alongside the CAS
# front matter; the section files (intro..conclusion) are format-agnostic and shared.
param(
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
$TemplateDir = Join-Path $PaperDir "ML_Template"
$WrapperName = "manuscript_sn.tex"
$FullWrapperName = "manuscript_sn_full.tex"
$MasterTexPath = Join-Path $PaperDir "manuscript.tex"
$BibPath = Join-Path $PaperDir "refs.bib"

# sn-jnl selects its own .bst from the documentclass option; sn-basic (without the
# "Numbered" option) is Springer Basic author-year, which is what Machine Learning uses.
$BstName = "sn-basic.bst"

$requiredFiles = @(
    $MasterTexPath,
    $BibPath,
    (Join-Path $TemplateDir "sn-jnl.cls"),
    (Join-Path $TemplateDir "bst/$BstName")
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
$env:LINT_REPORT_PATH = (Join-Path $BuildDir "template_lint_report.json")
@'
from pathlib import Path
from datetime import datetime, timezone
import difflib
import json
import os
import re

paper = Path(os.environ["PAPER_DIR"])
report_path = Path(os.environ["LINT_REPORT_PATH"])
master = paper / "manuscript.tex"
refs = paper / "refs.bib"
tex_files = sorted(paper.glob("*.tex"))

findings = []
existing_files = {p.name for p in paper.iterdir() if p.is_file()}
allowed_image_exts = [".pdf", ".png", ".jpg", ".jpeg", ".eps"]

cite_re = re.compile(r"\\cite[a-zA-Z*]*(?:\[[^\]]*\])*\{([^}]*)\}")
input_re = re.compile(r"\\input\{([^}]+)\}")
include_re = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
env_re = re.compile(r"\\begin\{(table\*?|longtable|figure\*?)\}(.*?)\\end\{\1\}", re.S)

def add_finding(severity: str, rule_id: str, file_name: str, line: int, context: str, message: str, fix_hint: str, example_fix: str) -> None:
    findings.append(
        {
            "severity": severity,
            "rule_id": rule_id,
            "file": file_name,
            "line": line,
            "context": context,
            "message": message,
            "fix_hint": fix_hint,
            "example_fix": example_fix,
        }
    )

def line_from_pos(text: str, pos: int) -> int:
    safe_pos = max(0, min(pos, len(text)))
    return text.count("\n", 0, safe_pos) + 1

def first_line_of(pattern: str, text: str) -> int:
    m = re.search(pattern, text, re.S)
    if not m:
        return 1
    return line_from_pos(text, m.start())

def has_caption(block: str) -> bool:
    return bool(re.search(r"\\caption(?:\[[^\]]*\])?\{", block))

def has_label(block: str) -> bool:
    return bool(re.search(r"\\label\{", block))

def write_report_and_print() -> int:
    errors = [f for f in findings if f["severity"] == "ERROR"]
    warnings = [f for f in findings if f["severity"] == "WARN"]
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "errors": len(errors),
            "warnings": len(warnings),
            "total": len(findings),
        },
        "findings": findings,
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    if findings:
        print("Template lint diagnostics:")
        for sev in ("ERROR", "WARN"):
            bucket = [f for f in findings if f["severity"] == sev]
            if not bucket:
                continue
            print(f"{sev} ({len(bucket)}):")
            for item in bucket:
                loc = f"{item['file']}:{item['line']}" if item["line"] else item["file"]
                print(
                    f"- [{item['rule_id']}] {loc} {item['message']} "
                    f"Fix: {item['fix_hint']}"
                )
                if item["example_fix"]:
                    print(f"  Example: {item['example_fix']}")

    print(
        f"Lint summary: {len(errors)} errors, {len(warnings)} warnings, "
        f"report: {report_path}"
    )
    return len(errors)

if not master.exists():
    add_finding(
        "ERROR",
        "CAS000",
        "manuscript.tex",
        1,
        "project root",
        "Required source file manuscript.tex is missing.",
        "Create manuscript.tex in journal_paper root.",
        r"\documentclass[pdflatex,sn-basic,lineno]{sn-jnl}",
    )
if not refs.exists():
    add_finding(
        "ERROR",
        "CAS200",
        "refs.bib",
        1,
        "project root",
        "Required bibliography file refs.bib is missing.",
        "Create refs.bib in journal_paper root and add cited entries.",
        "@article{ExampleKey,\n  title={...},\n  author={...},\n  year={2026}\n}",
    )
if not tex_files:
    add_finding(
        "ERROR",
        "CAS002",
        "*.tex",
        1,
        "project root",
        "No TeX source files were found in flat-source folder.",
        "Keep manuscript .tex files directly under journal_paper/ (flat).",
        r"\input{introduction.tex}",
    )

if any(f["rule_id"] in {"CAS000", "CAS200", "CAS002"} for f in findings):
    if write_report_and_print() > 0:
        raise SystemExit(1)

comment_re = re.compile(r"(?<!\\)%.*?$", re.M)

def strip_comments(text: str) -> str:
    """Drop TeX line comments so that commented-out markup does not trip the gates."""
    return comment_re.sub("", text)

master_text = strip_comments(master.read_text(encoding="utf-8"))
all_tex_text = strip_comments("\n".join(p.read_text(encoding="utf-8") for p in tex_files))

# --- Springer Nature (sn-jnl) front-matter gates -------------------------------------
required_master_patterns = [
    ("SN001", r"\\documentclass\[[^\]]*\bsn-basic\b[^\]]*\]\{sn-jnl\}", r"Missing sn-jnl class with the sn-basic reference style.", r"Machine Learning uses Springer Basic author-year; do not add the Numbered option.", r"\documentclass[pdflatex,sn-basic,lineno]{sn-jnl}"),
    ("SN002", r"\\title(?:\[[^\]]*\])?\{", r"Missing \title{...}.", r"Add the manuscript title; the optional argument sets the running head.", r"\title[Short Title]{Full Manuscript Title}"),
    ("SN003", r"\\author\*?\[[^\]]+\]\{", r"Missing Springer \author entry.", r"Add \author*[1]{\fnm{First} \sur{Last}} for the corresponding author.", r"\author*[1]{\fnm{Murat} \sur{Karakaya}}\email{a@b.c}"),
    ("SN004", r"\\affil\*?\[[^\]]+\]\{", r"Missing Springer \affil entry.", r"Add \affil*[1]{...} matching each author affiliation index.", r"\affil*[1]{\orgdiv{Dept}, \orgname{University}, \orgaddress{\city{City}, \country{Country}}}"),
    ("SN005", r"\\abstract\{", r"Missing \abstract{...}.", r"sn-jnl takes the abstract as a command argument, not an environment.", r"\abstract{Abstract text.}"),
    ("SN006", r"\\keywords\{", r"Missing \keywords{...}.", r"Add a comma-separated keyword list after the abstract.", r"\keywords{keyword one, keyword two}"),
    ("SN007", r"\\maketitle\b", r"Missing \maketitle.", r"Insert \maketitle after the front-matter blocks.", r"\maketitle"),
    ("SN008", r"\\bibliography\{refs\}", r"Bibliography source must be refs.", r"Point the bibliography command at the refs.bib base name.", r"\bibliography{refs}"),
]
for rule_id, pat, message, fix_hint, example_fix in required_master_patterns:
    if not re.search(pat, master_text, re.S):
        add_finding("ERROR", rule_id, master.name, 1, "front matter", message, fix_hint, example_fix)

# sn-jnl loads natbib and sets the bibliography style from the class option. Doing either
# in the preamble causes an option clash or silently overrides the journal style.
forbidden_master_patterns = [
    ("SN010", r"\\usepackage(?:\[[^\]]*\])?\{[^}]*\bnatbib\b[^}]*\}", r"sn-jnl already loads natbib; loading it again causes an option clash.", r"Delete the \usepackage{natbib} line and let the class load it.", r"% \usepackage[authoryear]{natbib}  <- remove"),
    ("SN011", r"\\bibliographystyle\{", r"sn-jnl sets \bibliographystyle from the class option.", r"Delete \bibliographystyle; select the style via the documentclass option instead.", r"\documentclass[pdflatex,sn-basic]{sn-jnl}"),
    ("SN012", r"\\begin\{highlights\}", r"Highlights are an Elsevier construct and are not supported by sn-jnl.", r"Remove the highlights environment; Springer has no equivalent.", r"% highlights removed"),
]
for rule_id, pat, message, fix_hint, example_fix in forbidden_master_patterns:
    m = re.search(pat, master_text, re.S)
    if m:
        add_finding("ERROR", rule_id, master.name, line_from_pos(master_text, m.start()), "preamble", message, fix_hint, example_fix)

# Springer requires a Declarations block in the back matter.
if not re.search(r"\\backmatter\b", all_tex_text):
    add_finding(
        "ERROR",
        "SN013",
        "declarations.tex",
        1,
        "back matter",
        r"Missing \backmatter before the declarations.",
        r"Open the back matter with \backmatter so trailing headings are unnumbered.",
        r"\backmatter",
    )
if not re.search(r"\\section\*\{Declarations\}", all_tex_text):
    add_finding(
        "ERROR",
        "SN014",
        "declarations.tex",
        1,
        "back matter",
        r"Missing \section*{Declarations}.",
        r"Springer expects the declarations under a single 'Declarations' heading.",
        r"\section*{Declarations}",
    )
for heading in ("Funding", "Competing interests", "Data availability", "Code availability", "Author contributions"):
    if not re.search(r"\\bmhead\{" + re.escape(heading) + r"\}", all_tex_text):
        add_finding(
            "WARN",
            "SN901",
            "declarations.tex",
            1,
            "declarations",
            f"Declaration subheading '{heading}' not found.",
            "Springer asks for each declaration heading, using 'Not applicable' where it does not apply.",
            rf"\bmhead{{{heading}}}",
        )

if not re.search(r"\\email\{", master_text):
    add_finding(
        "WARN",
        "SN902",
        master.name,
        first_line_of(r"\\author\*?\[[^\]]+\]\{", master_text),
        "author metadata",
        r"Optional metadata missing: no \email{...} found.",
        r"Add the corresponding author email directly after the \author* entry.",
        r"\author*[1]{\fnm{First} \sur{Last}}\email{first.last@example.com}",
    )

bib_text = refs.read_text(encoding="utf-8")
bib_entry_count = len(re.findall(r"@\w+\s*\{", bib_text))
bib_key_list = re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bib_text)
bib_keys = set(bib_key_list)
if not bib_keys:
    add_finding(
        "ERROR",
        "CAS210",
        refs.name,
        1,
        "bibliography entries",
        "refs.bib has no valid BibTeX keys.",
        "Add at least one valid BibTeX entry with a unique key.",
        "@article{ExampleKey,\n  title={...},\n  author={...},\n  year={2026}\n}",
    )
if len(bib_keys) != len(bib_key_list):
    seen = set()
    duplicates = []
    for key in bib_key_list:
        if key in seen and key not in duplicates:
            duplicates.append(key)
        seen.add(key)
    dup_text = ", ".join(duplicates) if duplicates else "unknown duplicate keys"
    add_finding(
        "ERROR",
        "CAS211",
        refs.name,
        1,
        "bibliography keys",
        f"Duplicate BibTeX keys detected: {dup_text}.",
        "Ensure each @entry{key,...} has a unique key.",
        "@article{UniqueKey2026,\n  ...\n}",
    )
if bib_entry_count > len(bib_key_list):
    add_finding(
        "ERROR",
        "CAS212",
        refs.name,
        1,
        "bibliography entries",
        "Malformed BibTeX entry detected (missing or invalid key).",
        "Fix each @type{key,...} to include a valid key followed by a comma.",
        "@misc{ValidKey,\n  title={...},\n  year={2026}\n}",
    )

cite_keys_used = set()
for tex_path in tex_files:
    text = tex_path.read_text(encoding="utf-8")

    for m in cite_re.finditer(text):
        keys = [k.strip() for k in m.group(1).split(",") if k.strip()]
        for key in keys:
            cite_keys_used.add(key)

    for m in input_re.finditer(text):
        target = m.group(1).strip()
        line = line_from_pos(text, m.start())
        if "/" in target or "\\" in target:
            add_finding(
                "ERROR",
                "CAS301",
                tex_path.name,
                line,
                target,
                f"Nested input path is not allowed in flat-source mode: {target}",
                r"Move the file to journal_paper root and reference only file name.",
                r"\input{section_name.tex}",
            )
            continue
        if not target.lower().endswith(".tex"):
            target += ".tex"
        if target not in existing_files:
            add_finding(
                "ERROR",
                "CAS302",
                tex_path.name,
                line,
                target,
                f"Input target file not found: {target}",
                "Create the missing .tex file in journal_paper root or fix the input name.",
                rf"\input{{{target}}}",
            )

    for m in include_re.finditer(text):
        target = m.group(1).strip()
        line = line_from_pos(text, m.start())
        if "/" in target or "\\" in target:
            add_finding(
                "ERROR",
                "CAS303",
                tex_path.name,
                line,
                target,
                f"Nested includegraphics path is not allowed in flat-source mode: {target}",
                "Copy the image into journal_paper root and reference by file name only.",
                r"\includegraphics[width=\linewidth]{figure_name.png}",
            )
            continue
        if "." in Path(target).name:
            if target not in existing_files:
                add_finding(
                    "ERROR",
                    "CAS304",
                    tex_path.name,
                    line,
                    target,
                    f"includegraphics file not found: {target}",
                    "Add the image file to journal_paper root or fix the file name/extension.",
                    rf"\includegraphics[width=\linewidth]{{{target}}}",
                )
        else:
            matches = [target + ext for ext in allowed_image_exts if (target + ext) in existing_files]
            if not matches:
                add_finding(
                    "ERROR",
                    "CAS305",
                    tex_path.name,
                    line,
                    target,
                    f"includegraphics target not found with allowed extensions: {target}",
                    "Provide an existing image file (.pdf/.png/.jpg/.jpeg/.eps) in journal_paper root.",
                    rf"\includegraphics[width=\linewidth]{{{target}.png}}",
                )

    env_idx = 0
    for env_match in env_re.finditer(text):
        env_idx += 1
        env_name = env_match.group(1)
        block = env_match.group(0)
        line = line_from_pos(text, env_match.start())
        if env_name.startswith("figure"):
            if not has_caption(block):
                add_finding(
                    "ERROR",
                    "CAS101",
                    tex_path.name,
                    line,
                    f"{env_name} #{env_idx}",
                    f"{env_name} #{env_idx} is missing \\caption{{...}}",
                    "Add \\caption{...} inside the figure environment before \\label.",
                    r"\caption{Descriptive figure caption}",
                )
            if not has_label(block):
                add_finding(
                    "ERROR",
                    "CAS102",
                    tex_path.name,
                    line,
                    f"{env_name} #{env_idx}",
                    f"{env_name} #{env_idx} is missing \\label{{...}}",
                    "Add unique \\label{fig:...} after \\caption in the same figure.",
                    r"\label{fig:example_result}",
                )
            if not re.search(r"\\centering\b", block):
                add_finding(
                    "ERROR",
                    "CAS103",
                    tex_path.name,
                    line,
                    f"{env_name} #{env_idx}",
                    f"{env_name} #{env_idx} is missing \\centering.",
                    "Add \\centering inside the figure before \\includegraphics.",
                    r"\centering",
                )
        else:
            if not has_caption(block):
                add_finding(
                    "ERROR",
                    "CAS101",
                    tex_path.name,
                    line,
                    f"{env_name} #{env_idx}",
                    f"{env_name} #{env_idx} is missing \\caption{{...}}",
                    "Add \\caption{...} inside the table/longtable before \\label.",
                    r"\caption{Descriptive table caption}",
                )
            if not has_label(block):
                add_finding(
                    "ERROR",
                    "CAS102",
                    tex_path.name,
                    line,
                    f"{env_name} #{env_idx}",
                    f"{env_name} #{env_idx} is missing \\label{{...}}",
                    "Add unique \\label{tab:...} after \\caption in the same table/longtable.",
                    r"\label{tab:example_results}",
                )
            if env_name.startswith("table") and not re.search(r"\\centering\b", block):
                add_finding(
                    "ERROR",
                    "CAS103",
                    tex_path.name,
                    line,
                    f"{env_name} #{env_idx}",
                    f"{env_name} #{env_idx} is missing \\centering.",
                    "Add \\centering inside the table environment before tabular/longtable content.",
                    r"\centering",
                )

missing_cites = sorted(k for k in cite_keys_used if k not in bib_keys)
for key in missing_cites:
    suggestions = difflib.get_close_matches(key, sorted(bib_keys), n=3, cutoff=0.45)
    suggestion_text = ", ".join(suggestions) if suggestions else "no close key found"
    add_finding(
        "ERROR",
        "CAS201",
        refs.name,
        1,
        key,
        f"Citation key '{key}' is used in TeX but missing from refs.bib.",
        f"Add this key to refs.bib or replace the citation key. Closest keys: {suggestion_text}.",
        f"\\citep{{{key}}}",
    )

error_count = write_report_and_print()
if error_count > 0:
    raise SystemExit(1)

print("Lint checks passed: template/rule gates are satisfied.")
'@ | python -
if ($LASTEXITCODE -ne 0) {
    throw "Template lint gates failed. See $env:LINT_REPORT_PATH for details."
}

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

# Copy required Springer Nature template assets.
Copy-Item (Join-Path $TemplateDir "sn-jnl.cls") $BuildDir -Force
Copy-Item (Join-Path $TemplateDir "bst/$BstName") $BuildDir -Force

# Generate the build wrapper. Unlike the CAS build there is no class placeholder to
# substitute: manuscript.tex already names sn-jnl directly.
$masterText = Get-Content -Path $MasterTexPath -Raw
$WrapperPath = Join-Path $BuildDir $WrapperName
Set-Content -Path $WrapperPath -Value $masterText -Encoding UTF8

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
if ($LASTEXITCODE -ne 0) {
    throw "Wrapper inlining step failed."
}

if ($CompilePdf) {
    # sn-jnl is a pdflatex class (the "pdflatex" documentclass option selects its
    # graphics path). All source is ASCII with escaped accents, so 8-bit TeX is safe.
    Assert-Command -Name "pdflatex"
    Assert-Command -Name "bibtex"

    $texBaseName = [System.IO.Path]::GetFileNameWithoutExtension($WrapperName)
    Push-Location $BuildDir
    try {
        Invoke-CheckedExternal -FilePath "pdflatex" -ArgumentList @("-interaction=nonstopmode", "-halt-on-error", $WrapperName) -StepName "pdfLaTeX pass 1"
        Invoke-CheckedExternal -FilePath "bibtex" -ArgumentList @($texBaseName) -StepName "BibTeX pass"
        Invoke-CheckedExternal -FilePath "pdflatex" -ArgumentList @("-interaction=nonstopmode", "-halt-on-error", $WrapperName) -StepName "pdfLaTeX pass 2"
        Invoke-CheckedExternal -FilePath "pdflatex" -ArgumentList @("-interaction=nonstopmode", "-halt-on-error", $WrapperName) -StepName "pdfLaTeX pass 3"
    }
    finally {
        Pop-Location
    }
}

$pdfPath = Join-Path $BuildDir ($WrapperName -replace '\.tex$', '.pdf')

Write-Host "Build complete."
Write-Host "  Journal: Machine Learning (Springer) - sn-jnl / sn-basic author-year"
Write-Host "  Build folder: $BuildDir"
Write-Host "  Wrapper: $(Join-Path $BuildDir $WrapperName)"
Write-Host "  Submission file (single .tex, all inputs inlined): $(Join-Path $BuildDir $FullWrapperName)"
Write-Host "  Bib: $(Join-Path $BuildDir 'refs.bib')"
if ($CompilePdf) {
    Write-Host "  PDF: $pdfPath"
} else {
    Write-Host "  PDF: not generated (use -CompilePdf)"
}
