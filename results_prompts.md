# Results Section Sub-Agent Prompts

Use these prompts to review and refine `journal_paper/results.tex` for a scientific paper. The prompts are designed to be run as separate sub-agent tasks with minimal overlap and clear handoff points.

## Shared Context For All Sub-Agents

- Required reading before starting:
  - `AGENTS.md`
  - `codex_skills/latex-template-compliance/SKILL.md`
  - `journal_paper/how_to_write_paper.md`
- Primary file: `journal_paper/results.tex`
- Supporting files:
  - `journal_paper/intro.tex`
  - `journal_paper/method.tex`
  - `journal_paper/experiments.tex`
- Research questions from `intro.tex`:
  - `RQ1`: actionable evidence for local embedding-model selection
  - `RQ2`: language sensitivity across English and Turkish education corpora
  - `RQ3`: domain sensitivity across Turkish education and Turkish law/regulation corpora
  - `RQ4`: quality-speed tradeoff for fit-for-purpose deployment decisions
- Repo constraints:
  - Use TeX-first manuscript sources only
  - Do not edit files under `journal_paper/build/`
  - Do not treat files under `journal_paper/build/` as authoritative source text
  - Keep `journal_paper/results.tex` focused on metric presentation, comparative evidence, tradeoffs, and findings
  - Do not push method/setup content into Results unless it is needed to justify an interpretation
  - Keep interpretation bounded to the fixed experimental snapshot
  - Do not introduce claims that are not supported by the existing evidence
- Table and figure rules:
  - Every proposed `table` or `figure` must include both `\caption{...}` and `\label{...}`
  - Prefer `booktabs` table style
  - Keep figure paths and source references flat within `journal_paper/`
  - Every table or figure must be referenced explicitly in surrounding prose and interpreted meaningfully
- Wording rules:
  - Prefer `paper` over `manuscript` in reader-facing prose
  - Prefer `practitioner` for the person applying the pipeline to local corpora
  - Avoid report-style internal traceability language unless methodologically necessary
- Logging requirement:
  - Each sub-agent must append its own separate section to `results_agent_logs.md`
  - The section title must use the prompt name, for example `## Prompt 1 - Subsection-To-Artifact Mapping Audit`
  - Each log entry must include:
    - `Date/Time`
    - `Agent/Prompt`
    - `Files Reviewed`
    - `Activities Performed`
    - `Key Findings`
    - `Suggested Revisions`
    - `Open Questions or Risks`
    - `Status`
  - The log must be structured, concise, and cumulative; agents must append rather than overwrite prior sections
- Unless the parent task explicitly says otherwise, do not modify files. Return findings and exact proposed edits only.
- When citing issues or suggestions, include file and line references.

## Suggested Execution Order

1. Prompt 1: subsection-to-artifact mapping
2. Prompt 2: numeric fidelity audit
3. Prompt 3: RQ and claim-support audit
4. Prompt 4: prose structure and style consistency audit
5. Prompt 5: missing evidence and new artifact recommendations
6. Prompt 6: synthesis into an actionable revision spec
7. Prompt 7: reviewer-style assessment of the final Results section

---

## Prompt 1: Subsection-To-Artifact Mapping Audit

### Context

You are auditing `journal_paper/results.tex` subsection by subsection. The Results section contains multiple subsections with tables and figures. The paper must ensure that each subsection cites the correct tables and figures and that each artifact is used in the most relevant subsection.

### Goal

Build an explicit mapping between subsections and the tables/figures they use, then identify any missing, weak, misplaced, or redundant references.

### Tasks

1. Enumerate every Results subsection in order.
2. For each subsection, list:
   - the subsection heading
   - all tables cited in the subsection text
   - all figures cited in the subsection text
   - all tables/figures physically located within or adjacent to that subsection
3. Identify problems such as:
   - a subsection that contains a table/figure but does not reference it in prose
   - a subsection that references a table/figure weakly or generically
   - a table/figure that would fit better in another subsection
   - a table/figure that duplicates another artifact without adding interpretive value
4. Evaluate whether each reference is meaningful:
   - does the prose explain what the artifact shows?
   - does the prose use the artifact to support a finding rather than merely mention it?

### Checks

- Every table and figure in `results.tex` must be accounted for exactly once in your inventory.
- Distinguish between “present in subsection” and “meaningfully interpreted in subsection”.
- Do not comment on number correctness here unless it affects whether the reference is meaningful.
- Keep the Results-section boundary intact: evidence and interpretation only.

### Output Format

- Start with a compact subsection-to-artifact matrix.
- Then list findings ordered by severity.
- For each finding, include:
  - location
  - issue
  - why it matters
  - exact improvement recommendation

---

## Prompt 2: Numeric Fidelity Audit

### Context

You are checking whether the prose in `journal_paper/results.tex` uses the correct numbers from its cited tables and figures. The goal is strict factual accuracy.

### Goal

Verify every quantitative statement in the Results prose against the referenced tables and figures, and detect any mismatches, overstatements, omissions, or misleading summaries.

### Tasks

1. Scan every Results subsection for explicit quantitative claims:
   - metric values
   - ranks
   - deltas
   - “best”, “highest”, “lowest”, “stable”, “sharp drop”, “clustered”, and similar comparative claims
2. For each quantitative or comparative claim, verify it against the cited table or figure.
3. Identify:
   - incorrect numbers
   - correct numbers used in the wrong context
   - claims that imply a direction not supported by the values
   - claims that say “all models” or similar when exceptions exist
4. When a claim is weak but not false, suggest a tighter wording using the exact values already present in the manuscript.

### Checks

- Do not infer new numeric results from external sources.
- If a figure is qualitative, rely on its underlying table when available.
- Flag both hard errors and soft accuracy issues.
- If the prose uses a model-family label, verify that the label matches the roster in `journal_paper/experiments.tex`.

### Output Format

- Findings first, ordered by severity.
- For each finding, include:
  - prose location
  - cited artifact
  - exact mismatch or weakness
  - corrected wording

---

## Prompt 3: Research-Question And Claim Support Audit

### Context

The Results section must support the paper’s overall objective and research questions from `journal_paper/intro.tex`. It should not read as disconnected dataset commentary.

### Goal

Evaluate whether each Results subsection meaningfully supports one or more research questions or core paper claims, and identify where the reasoning is too weak, indirect, or missing.

### Tasks

1. Extract the core paper claims and RQs from `intro.tex`.
2. For each subsection in `results.tex`, determine:
   - which RQ(s) it supports
   - which paper-level claim(s) it advances
   - whether the subsection explicitly says so or only implies it
3. Identify gaps such as:
   - subsection discusses evidence without connecting it to an RQ
   - subsection states a claim without clarifying why it matters for fit-for-purpose selection
   - subsection uses an artifact but does not explain the implication for the paper’s argument
4. Recommend exact additions or rewrites to strengthen the link between evidence and paper claim.

### Checks

- Stay within the paper’s declared scope: fixed snapshot, controlled local benchmarking, no universal superiority claims.
- Treat RQ alignment as a logical support check, not merely a keyword match.
- Ensure recommendations preserve the Results role rather than drifting into Method or Experiments.

### Output Format

- Start with a subsection-to-RQ mapping.
- Then provide findings and targeted rewrite suggestions.
- For each recommendation, include the specific claim that would be better supported after the change.

---

## Prompt 4: Prose Structure And Style Consistency Audit

### Context

The Results subsections should follow a similar rhetorical pattern without sounding copied. Each subsection should reflect the paper’s ideas and research questions while remaining distinct in content.

### Goal

Assess structural consistency, tone, and rhetorical format across Results subsections, then propose improvements that make the section feel coherent without making every paragraph formulaic.

### Tasks

1. Compare the subsection structures across:
   - dataset-level result subsections
   - cross-cutting interpretation subsections
   - statistical note
2. Evaluate whether each subsection has a clear pattern such as:
   - opening claim
   - evidence reference
   - interpretation
   - implication
3. Identify problems such as:
   - subsections that only restate tables
   - subsections that are too short relative to the importance of the topic
   - repeated sentence templates or overly mechanical phrasing
   - subsections that drift away from the paper’s fit-for-purpose framing
4. Recommend structural rewrite patterns for each subsection type.

### Checks

- “Similar format” should mean shared logic, not repeated wording.
- Preserve the Results-section role: evidence and interpretation, not method restatement.
- Keep terminology aligned with `AGENTS.md`: `paper`, `practitioner`, and bounded claim wording.

### Output Format

- Provide a short structural assessment of the Results section as a whole.
- Then list subsection-level style findings and rewrite guidance.
- Where helpful, give one replacement opening sentence and one replacement closing sentence.

---

## Prompt 5: Missing Evidence And New Artifact Recommendations

### Context

The Results section may or may not have enough tables and figures to support all paper claims and research questions. Your job is to decide whether more evidence artifacts are needed.

### Goal

Judge whether the current tables and figures are sufficient, and if not, recommend the minimum set of additional artifacts needed to make the Results section convincing and complete.

### Tasks

1. Review the current artifact set in `results.tex`.
2. Evaluate sufficiency against:
   - `RQ1` pipeline utility
   - `RQ2` language effect
   - `RQ3` domain effect
   - `RQ4` quality-speed tradeoff
3. For any missing or weak area, specify:
   - whether a new table or figure is needed
   - exactly what it should show
   - which subsection it belongs in
   - why the existing artifacts are insufficient
4. Distinguish between:
   - must-add artifacts
   - useful-but-optional artifacts
   - artifacts that would be redundant

### Checks

- Recommend additions only when they materially improve support for a claim or RQ.
- Prefer compact artifacts over proliferation of similar tables.
- If the current evidence is already sufficient, say so clearly.
- Proposed artifacts must be CAS-compliant and realistically placeable in `journal_paper/results.tex`.

### Output Format

- Start with a sufficiency verdict for each RQ.
- Then provide artifact recommendations in priority order.
- For each proposed artifact, include:
  - type: `table` or `figure`
  - exact purpose
  - candidate caption
  - target subsection

---

## Prompt 6: Results Revision Synthesizer

### Context

You are the integration agent. Other sub-agents have already reviewed artifact references, numeric fidelity, RQ support, style consistency, and evidence sufficiency.

### Goal

Convert the audit findings into an implementation-ready revision spec for `journal_paper/results.tex`.

### Inputs

- Output from Prompt 1
- Output from Prompt 2
- Output from Prompt 3
- Output from Prompt 4
- Output from Prompt 5

### Tasks

1. Consolidate the findings into one coherent revision plan.
2. Remove duplicate or overlapping recommendations.
3. Resolve conflicts between recommendations by prioritizing:
   - factual correctness
   - RQ support
   - artifact relevance
   - prose quality
4. Produce a subsection-by-subsection edit specification:
   - keep
   - revise
   - add reference
   - add table/figure
   - remove or relocate weak content
5. If a new artifact is recommended, include the exact intended role and the sentence-level place where it should be interpreted.

### Checks

- The final spec must be implementable without additional decisions.
- Do not leave vague directions such as “improve wording” without saying how.
- Any suggested new artifact must include its rhetorical role in the subsection, not just its data content.

### Output Format

- Start with a short overall diagnosis.
- Then provide a subsection-by-subsection revision checklist.
- End with a short prioritized sequence of edits.

---

## Prompt 7: Journal Reviewer Report For Results Section

### Context

The Results section has already been audited and refined. You are now acting as a journal reviewer reading only the Results section in the context of the paper’s stated objective and research questions.

### Goal

Produce a reviewer-style assessment of `journal_paper/results.tex` from the perspective of a rigorous but fair journal referee.

### Tasks

1. Assess the Results section for:
   - clarity
   - evidential sufficiency
   - internal consistency
   - alignment with research questions
   - appropriateness of interpretation
2. Identify major comments:
   - issues that materially affect publication quality or argument validity
3. Identify minor comments:
   - phrasing, structure, or presentation issues that should still be improved
4. Conclude with an overall verdict specifically about the Results section:
   - strong
   - acceptable with revisions
   - weak and needing substantial revision

### Checks

- Write in the voice of a journal reviewer, not a coding assistant.
- Evaluate the Results section on scholarly standards, not repository engineering preferences.
- Be specific and evidence-based.

### Output Format

- `Summary`
- `Major Comments`
- `Minor Comments`
- `Overall Verdict`
