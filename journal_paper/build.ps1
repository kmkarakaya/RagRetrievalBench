# Builds the PeerJ Computer Science manuscript (wlpeerj class, Peerj_template/).
#
# With -CompilePdf the compiled PDF, the single-file LaTeX source and the separately
# numbered figure files are exported to "Peerj Submision/".
#
# The retired Springer sn-jnl build lives in archive_sn/build_sn.ps1 and the Elsevier CAS
# build in archive_cas/build_cas.ps1; the section files (intro..conclusion) are
# format-agnostic and shared.
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
$TemplateDir = Join-Path $PaperDir "Peerj_template"
$SubmissionDir = Join-Path $PaperDir "Peerj Submision"
$WrapperName = "manuscript_peerj.tex"
$FullWrapperName = "manuscript_peerj_full.tex"
$MasterTexPath = Join-Path $PaperDir "manuscript.tex"
$BibPath = Join-Path $PaperDir "refs.bib"
$ClsName = "wlpeerj.cls"

# wlpeerj sets \bibliographystyle{apalike} itself; apalike.bst ships with every TeX
# distribution, so only the class file is copied from the template folder.
$requiredFiles = @(
    $MasterTexPath,
    $BibPath,
    (Join-Path $TemplateDir $ClsName)
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
        r"\documentclass[fleqn,10pt,lineno]{wlpeerj}",
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

# --- PeerJ (wlpeerj) front-matter gates ----------------------------------------------
required_master_patterns = [
    ("PJ001", r"\\documentclass\[[^\]]*\blineno\b[^\]]*\]\{wlpeerj\}", r"Missing wlpeerj class with the lineno option.", r"PeerJ requires line numbers on peer-review submissions.", r"\documentclass[fleqn,10pt,lineno]{wlpeerj}"),
    ("PJ002", r"\\title\{", r"Missing \title{...} (wlpeerj takes no running-head optional argument).", r"Use the plain article form \title{...}.", r"\title{Full Manuscript Title}"),
    ("PJ003", r"\\author\[[^\]]+\]\{", r"Missing authblk \author entry.", r"Add \author[1]{First Last} for each author.", r"\author[1]{Murat Karakaya}"),
    ("PJ004", r"\\affil\[[^\]]+\]\{", r"Missing authblk \affil entry.", r"Add \affil[1]{...} matching each author affiliation index.", r"\affil[1]{Dept, University, City, Country}"),
    ("PJ005", r"\\corrauthor\[[^\]]+\]\{[^}]+\}\{[^}]+@[^}]+\}", r"Missing \corrauthor with an email address.", r"wlpeerj v1.2 prints the corresponding author block from \corrauthor.", r"\corrauthor[1]{Murat Karakaya}{a@b.c}"),
    ("PJ006", r"\\begin\{abstract\}.*?\\end\{abstract\}.*?\\begin\{document\}", r"Missing abstract environment before \begin{document}.", r"wlpeerj captures the abstract in the preamble; use the environment, not \abstract{...}, and do not nest \begin/\end inside it.", r"\begin{abstract} ... \end{abstract}"),
    ("PJ007", r"\\maketitle\b", r"Missing \maketitle.", r"Insert \maketitle after \begin{document}.", r"\maketitle"),
    ("PJ008", r"\\bibliography\{refs\}", r"Bibliography source must be refs.", r"Point the bibliography command at the refs.bib base name.", r"\bibliography{refs}"),
]
for rule_id, pat, message, fix_hint, example_fix in required_master_patterns:
    if not re.search(pat, master_text, re.S):
        add_finding("ERROR", rule_id, master.name, 1, "front matter", message, fix_hint, example_fix)

# wlpeerj loads natbib and sets \bibliographystyle{apalike}. Doing either in the preamble
# causes an option clash or a second style. Keywords go in the PeerJ submission form.
forbidden_master_patterns = [
    ("PJ010", r"\\usepackage(?:\[[^\]]*\])?\{[^}]*\bnatbib\b[^}]*\}", r"wlpeerj already loads natbib; loading it again causes an option clash.", r"Delete the \usepackage{natbib} line and let the class load it.", r"% \usepackage{natbib}  <- remove"),
    ("PJ011", r"\\bibliographystyle\{", r"wlpeerj sets \bibliographystyle{apalike} itself.", r"Delete \bibliographystyle.", r"% \bibliographystyle{...}  <- remove"),
    ("PJ012", r"\\keywords\{", r"wlpeerj has no \keywords; PeerJ collects keywords in the submission form.", r"Keep the keyword list as a comment and enter it in the form.", r"% \keywords{keyword one, keyword two}"),
    ("PJ013", r"\\begin\{highlights\}", r"Highlights are an Elsevier construct and are not supported by wlpeerj.", r"Remove the highlights environment.", r"% highlights removed"),
]
for rule_id, pat, message, fix_hint, example_fix in forbidden_master_patterns:
    m = re.search(pat, master_text, re.S)
    if m:
        add_finding("ERROR", rule_id, master.name, line_from_pos(master_text, m.start()), "preamble", message, fix_hint, example_fix)

# Constructs that are undefined under wlpeerj, or that PeerJ wants outside the manuscript.
forbidden_any_patterns = [
    ("PJ014", r"\\(?:fnm|sur|orgdiv|orgname|orgaddress|bmhead|backmatter)\b", r"sn-jnl-only command is undefined under wlpeerj.", r"Use authblk \author/\affil and plain \section* headings.", r"\section*{Data availability}"),
    ("PJ015", r"\\begin\{(?:table|figure)\*\}", r"Starred floats are not used in the single-column wlpeerj layout.", r"Use table/figure and size content with \linewidth.", r"\begin{table}"),
    ("PJ016", r"\\(?:sub)*section\*?\{(?:Funding|Competing interests|Author contributions|Declarations)\}", r"PeerJ collects funding, competing interests and author contributions in the submission form.", r"Move the statement text to Peerj Submision/portal_statements.txt.", r"% entered in the PeerJ form"),
]
for tex_path in tex_files:
    tex_text = strip_comments(tex_path.read_text(encoding="utf-8"))
    for rule_id, pat, message, fix_hint, example_fix in forbidden_any_patterns:
        m = re.search(pat, tex_text)
        if m:
            add_finding("ERROR", rule_id, tex_path.name, line_from_pos(tex_text, m.start()), m.group(0), message, fix_hint, example_fix)

for heading in ("Data availability", "Code availability"):
    if not re.search(r"\\section\*\{" + re.escape(heading) + r"\}", all_tex_text):
        add_finding(
            "WARN",
            "PJ901",
            "declarations.tex",
            1,
            "back matter",
            f"Unnumbered section '{heading}' not found.",
            "Keep the data and code availability statements at the end of the paper.",
            rf"\section*{{{heading}}}",
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

# Copy the PeerJ class file. apalike.bst is resolved from the TeX distribution.
Copy-Item (Join-Path $TemplateDir $ClsName) $BuildDir -Force

# Generate the build wrapper. There is no class placeholder to substitute:
# manuscript.tex already names wlpeerj directly.
$masterText = Get-Content -Path $MasterTexPath -Raw
$WrapperPath = Join-Path $BuildDir $WrapperName
# Write UTF-8 without a BOM. Windows PowerShell's -Encoding UTF8 emits one, and the
# BOM then leads the submitted .tex file. Our pdflatex copes, but the publisher
# compiles the submitted source on their own toolchain, so keep it pure ASCII.
[System.IO.File]::WriteAllText(
    $WrapperPath, $masterText, (New-Object System.Text.UTF8Encoding($false)))

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

wrapper_text = (build / wrapper_name).read_text(encoding='utf-8-sig')
full_text = inline_inputs(wrapper_text, [wrapper_name])
(build / full_wrapper_name).write_text(full_text, encoding='utf-8')
print(f"Wrote {wrapper_name} and {full_wrapper_name}")
'@ | python -
if ($LASTEXITCODE -ne 0) {
    throw "Wrapper inlining step failed."
}

if ($CompilePdf) {
    # wlpeerj loads inputenc/times/mathptmx, i.e. it is a pdflatex class. All source is
    # ASCII with escaped accents, so 8-bit TeX is safe.
    Assert-Command -Name "pdflatex"
    Assert-Command -Name "bibtex"

    $texBaseName = [System.IO.Path]::GetFileNameWithoutExtension($WrapperName)
    Push-Location $BuildDir
    try {
        Invoke-CheckedExternal -FilePath "pdflatex" -ArgumentList @("-interaction=nonstopmode", "-halt-on-error", $WrapperName) -StepName "pdfLaTeX pass 1"
        Invoke-CheckedExternal -FilePath "bibtex" -ArgumentList @($texBaseName) -StepName "BibTeX pass"
        Invoke-CheckedExternal -FilePath "pdflatex" -ArgumentList @("-interaction=nonstopmode", "-halt-on-error", $WrapperName) -StepName "pdfLaTeX pass 2"
        Invoke-CheckedExternal -FilePath "pdflatex" -ArgumentList @("-interaction=nonstopmode", "-halt-on-error", $WrapperName) -StepName "pdfLaTeX pass 3"
        # lastpage and lineno can shift labels on the third pass; rerun until stable.
        $logName = "$texBaseName.log"
        $extraPass = 4
        while ((Select-String -Path $logName -Pattern "Rerun to get cross-references right" -Quiet) -and $extraPass -le 6) {
            Invoke-CheckedExternal -FilePath "pdflatex" -ArgumentList @("-interaction=nonstopmode", "-halt-on-error", $WrapperName) -StepName "pdfLaTeX pass $extraPass"
            $extraPass++
        }
        if (Select-String -Path $logName -Pattern "Rerun to get cross-references right" -Quiet) {
            throw "Cross-references did not stabilise after $($extraPass - 1) pdfLaTeX passes."
        }
    }
    finally {
        Pop-Location
    }
}

$pdfPath = Join-Path $BuildDir ($WrapperName -replace '\.tex$', '.pdf')

if ($CompilePdf) {
    # Export the PeerJ submission package. Only the generated items below are replaced;
    # anything else in the folder (portal_statements.txt, cover letter) is left alone.
    #   latex_source/       single-file manuscript.tex + refs.bib + .bbl + class +
    #                       Figure1..N images, numbered in order of appearance; these
    #                       are the exact files uploaded to PeerJ one by one
    #   latex_source.zip    the same, zipped
    #   manuscript.pdf      compiled from latex_source/ itself, so PDF and sources match
    $env:SUBMISSION_DIR = $SubmissionDir
    $env:CLS_NAME = $ClsName
    @'
from pathlib import Path
import os
import re
import shutil

build = Path(os.environ["BUILD_DIR"])
out = Path(os.environ["SUBMISSION_DIR"])
full_tex = build / os.environ["FULL_WRAPPER_NAME"]
bbl = build / (Path(os.environ["WRAPPER_NAME"]).stem + ".bbl")
cls_name = os.environ["CLS_NAME"]

from PIL import Image
import subprocess

out.mkdir(parents=True, exist_ok=True)
src = out / "latex_source"
for d in (src, out / "figures"):  # figures/ is the retired second copy
    if d.exists():
        shutil.rmtree(d)
src.mkdir()
zip_path = out / "latex_source.zip"
if zip_path.exists():
    zip_path.unlink()

full_text = full_tex.read_text(encoding="utf-8")
uncommented = re.sub(r"(?<!\\)%.*?$", "", full_text, flags=re.M)
images = list(dict.fromkeys(
    re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", uncommented)))

# PeerJ rejects figure files smaller than 900 x 900 px. Wide workflow diagrams and
# small plots fall short in height, so they are centered on a white canvas of at
# least that size. The padded file is the only copy: the TEX, the PDF and the
# upload all use it.
MIN_SIDE = 900

def export_figure(image, dest):
    with Image.open(image) as im:
        w, h = im.size
        if w >= MIN_SIDE and h >= MIN_SIDE:
            shutil.copy2(image, dest)
            return
        rgba = im.convert("RGBA")
    canvas = Image.new("RGB", (max(w, MIN_SIDE), max(h, MIN_SIDE)), "white")
    canvas.paste(rgba, ((canvas.width - w) // 2, (canvas.height - h) // 2), rgba)
    canvas.save(dest)

renamed = {}
for i, name in enumerate(images, 1):
    image = build / name
    renamed[name] = f"Figure{i}{image.suffix.lower()}"
    export_figure(image, src / renamed[name])

full_text = re.sub(
    r"(\\includegraphics(?:\[[^\]]*\])?\{)([^}]+)\}",
    lambda m: m.group(1) + renamed.get(m.group(2), m.group(2)) + "}",
    full_text)
(src / "manuscript.tex").write_text(full_text, encoding="utf-8")
shutil.copy2(bbl, src / "manuscript.bbl")
shutil.copy2(build / "refs.bib", src / "refs.bib")
shutil.copy2(build / cls_name, src / cls_name)

# Compile the exported package on its own, so the submitted PDF is built from
# exactly the files that are uploaded. The .bbl is shipped, so no BibTeX pass.
check = build / "submission_check"
if check.exists():
    shutil.rmtree(check)
shutil.copytree(src, check)
for n in range(3):
    r = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "manuscript.tex"],
        cwd=check, capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        raise SystemExit(f"Exported latex_source/ failed to compile (pass {n + 1}); see {check}")
log = (check / "manuscript.log").read_text(encoding="latin-1")
if re.search(r"undefined|File `[^']+' not found", log):
    raise SystemExit(f"Exported latex_source/ has unresolved references or files; see {check}")
shutil.copy2(check / "manuscript.pdf", out / "manuscript.pdf")

shutil.make_archive(str(zip_path.with_suffix("")), "zip", root_dir=src)
print(f"Exported submission package to {out} (PDF compiled from latex_source/)")
for name, new in renamed.items():
    print(f"  {new}: {name}")
'@ | python -
    if ($LASTEXITCODE -ne 0) {
        throw "Submission export step failed."
    }
}

Write-Host "Build complete."
Write-Host "  Journal: PeerJ Computer Science - wlpeerj / apalike author-year"
Write-Host "  Build folder: $BuildDir"
Write-Host "  Wrapper: $(Join-Path $BuildDir $WrapperName)"
Write-Host "  Submission file (single .tex, all inputs inlined): $(Join-Path $BuildDir $FullWrapperName)"
Write-Host "  Bib: $(Join-Path $BuildDir 'refs.bib')"
if ($CompilePdf) {
    Write-Host "  PDF: $pdfPath"
    Write-Host "  Submission package: $SubmissionDir"
} else {
    Write-Host "  PDF: not generated (use -CompilePdf)"
}
