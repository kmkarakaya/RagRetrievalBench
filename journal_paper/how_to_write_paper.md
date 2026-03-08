# How To Write This Paper With Codex (TeX-First)

This file is the practical guide for a human working with Codex in VS Code.

## 1) What to edit
Edit only these source files:
- `journal_paper/manuscript.tex`
- `journal_paper/*.tex`
- `journal_paper/refs.bib`

Do not edit generated files inside `journal_paper/build/...`.

## 2) What each control file does
- `AGENTS.md`
  - repo-wide rules automatically available to Codex in this repository
  - use this as the non-negotiable policy layer
- `journal_paper/codex_session_prompt.txt`
  - short session bootstrap text you can paste into a new Codex chat
  - use this to force the session into the paper workflow immediately
- `codex_skills/latex-template-compliance/SKILL.md`
  - detailed CAS/LaTeX workflow guidance
  - use this when the task is about tables, figures, labels, citations, layout, or template compliance

## 3) How the human should use them
For a normal paper-writing session in VS Code:
1. Start a new Codex chat.
2. Tell Codex to read:
   - `AGENTS.md`
   - `journal_paper/codex_session_prompt.txt`
3. If the task is formatting-heavy or template-sensitive, also tell Codex to use:
   - `codex_skills/latex-template-compliance/SKILL.md`
4. Then give the actual section-editing task.

Use the skill explicitly when:
- editing tables or figures
- moving content between sections
- fixing labels/cross-references
- checking template compliance
- resolving LaTeX build/layout issues

## 4) Recommended session starter prompt
At the start of a new chat, paste:

```text
Use this repo workflow exactly.
Read and follow AGENTS.md and journal_paper/codex_session_prompt.txt.
If the task is template-sensitive, also use codex_skills/latex-template-compliance/SKILL.md.
Edit only journal_paper/manuscript.tex, journal_paper/*.tex, and journal_paper/refs.bib.
Follow Elsevier CAS template conventions.
Run powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1 -CompilePdf before declaring success.
```

## 5) How to use `build.ps1`
`journal_paper/build.ps1` is the required validation gate.

Use:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1
```

This checks:
- repo/template lint rules
- captions/labels
- path and structural rules
- other manuscript gate checks

Use:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1 -CompilePdf
```

This does the full validation path:
- lint/template checks
- wrapper generation
- XeLaTeX/BibTeX/PDF build

For real manuscript editing, prefer `-CompilePdf`, because some failures only appear during actual LaTeX compilation.

## 6) How to interpret build results
- If lint fails:
  - fix manuscript-rule violations first
- If PDF compile fails but lint passes:
  - inspect LaTeX/layout issues such as floats, tables, references, or environment problems
- If MiKTeX or environment setup fails:
  - treat that as a machine issue, not a manuscript-logic issue

Always ask Codex to report:
- files changed
- summary of fixes
- latest build folder
- PDF path if compiled
- remaining warnings, if any

## 7) Practical advice for section work
- Tell Codex which section owns the content before asking for edits.
- Ask Codex to keep prose, tables, and figures aligned.
- Ask Codex to reference tables/figures in the text.
- Ask Codex to regenerate the PDF after each substantial section change.
- If a small table causes LaTeX trouble, ask Codex to prefer `table` over `longtable` unless multi-page behavior is required.
- If a figure does not exist yet, ask Codex to:
  - insert a CAS-compliant figure placeholder with `\caption{...}` and `\label{...}`
  - add a short design prompt in a nearby LaTeX comment
  - write a reusable image-generation prompt you can paste into Banana 2 or another image model

Recommended wording:

```text
If the figure is not available yet, add a placeholder figure in the section with a proper caption and label, and include a short nearby prompt/comment so I can later generate the figure with Banana 2.
```

## 8) Copy-Paste Prompt Library
Use these as ready-made prompts in VS Code instead of rewriting the same instructions each time.

### A. Start a new manuscript-editing session

```text
Use this repo workflow exactly.
Read and follow AGENTS.md and journal_paper/codex_session_prompt.txt.
Use codex_skills/latex-template-compliance/SKILL.md if the task is template-sensitive.
Edit only journal_paper/manuscript.tex, journal_paper/*.tex, and journal_paper/refs.bib.
Follow Elsevier CAS template conventions.
Always run powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1 -CompilePdf before declaring success.
```

### B. Rewrite one section in journal style

```text
Focus on journal_paper/<section>.tex only.
Rewrite this section in scientific journal style using the facts already available in the repo and generated reports.
Keep the section within its proper manuscript scope and do not duplicate content that belongs in other sections.
Keep prose, tables, and figures aligned.
Reference tables and figures in the text where appropriate.
Always regenerate the PDF before declaring success.
```

### C. Keep section boundaries strict

```text
Be careful about section ownership.
Keep method.tex focused on the proposed pipeline and workflow.
Keep experiments.tex focused on the manuscript-specific setup, datasets, provenance, model roster, and limitations.
Keep results.tex focused on metrics, evidence, findings, and tradeoff interpretation.
Do not let Method absorb results discussion.
```

### D. Add or revise a figure placeholder

```text
Add a CAS-compliant figure placeholder in the target section with \caption{...} and \label{...}.
Include a short nearby LaTeX comment that can later be used to generate the image with Banana 2.
Also write a reusable Banana 2 prompt for the figure.
Keep the figure path flat inside journal_paper/.
```

### E. Review an image and replace a placeholder

```text
Check whether this image is appropriate for the intended figure in the section.
If it is acceptable, replace the placeholder in the relevant .tex file with the real image.
Keep the template figure structure correct and regenerate the PDF.
If the image is only partially acceptable, say what is still weak but insert it if it is usable.
```

### F. Align prose with a figure

```text
Considering the figure, revise the surrounding subsection text if necessary so the prose follows the actual workflow shown in the figure.
Do not change the section scope.
Keep the writing in scientific journal style.
Regenerate the PDF after the revision.
```

### G. Align tables with section text

```text
In this section, compare the table captions, headings, and row content with the surrounding prose.
Revise the tables or the text so they describe the same workflow, artifacts, and terminology.
Keep labels stable unless renaming is necessary.
Regenerate the PDF after the revision.
```

### H. Move content to the correct section

```text
This content belongs in another section.
Move it to the correct .tex file, repair the surrounding prose and references, and keep section boundaries clean.
Do not duplicate the same content in both places.
Regenerate the PDF after the change.
```

### I. Generalize method wording

```text
For method.tex, use reusable pipeline wording unless a specific format is methodologically important.
For example, prefer document collection over PDF collection, but keep factual implementation details where needed.
Revise the text, tables, and captions consistently.
Regenerate the PDF after the change.
```

### J. Template-compliance check for one section

```text
Read AGENTS.md and use codex_skills/latex-template-compliance/SKILL.md.
Check journal_paper/<section>.tex for alignment with the Elsevier CAS template and local repo rules.
If anything is weak or inconsistent, fix it.
Then run powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1 -CompilePdf and report the result.
```

## 9) Definition of done
- Changes are made only in intended TeX-first source files.
- `journal_paper/build.ps1 -CompilePdf` completes successfully, unless you explicitly accept an environment blocker.
- Codex reports the latest build folder and PDF path.
