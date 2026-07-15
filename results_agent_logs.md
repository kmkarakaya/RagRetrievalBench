# Results Agent Logs

Use this file as the cumulative activity log for all Results-section sub-agents working from `results_prompts.md`.

## Logging Rules

- Each agent must append a new section instead of overwriting prior content.
- Each section must use the exact prompt identity in the heading, for example:
  - `## Prompt 1 - Subsection-To-Artifact Mapping Audit`
- Keep entries structured and concise.
- Include file and line references where useful.

## Template

```md
## Prompt X - Prompt Name

- Date/Time: YYYY-MM-DD HH:MM
- Agent/Prompt: Prompt X - Prompt Name
- Files Reviewed: `journal_paper/results.tex`, `journal_paper/intro.tex`
- Activities Performed: Brief description of the checks completed
- Key Findings:
  - Finding 1
  - Finding 2
- Suggested Revisions:
  - Suggestion 1
  - Suggestion 2
- Open Questions or Risks:
  - Risk 1
  - Risk 2
- Status: Complete / Partial / Blocked
```
