
2. The three open items
   Item A — Report PDFs have never worked (bigger than I first said)
   I under-reported this. It is not aggregate-only: zero generated report PDFs exist anywhere, for either report type, though pandoc and MiKTeX are both installed. Meanwhile the README advertises PDF output in Features, in the Installation prerequisites, and in --generate-aggregate-report.

I diagnosed rather than guessed: xelatex and lualatex fail identically to pdflatex, so it is not an engine problem; and removing the wide pairwise matrices does not fix it either, so it is not simply the widest table. Some longtable in the report body cannot be broken across pages.

Option	Effort	Outcome
Make the README honest — describe PDF as best-effort, drop it from prerequisites	~15 min	Docs correct, feature still absent
Bisect the report to find the offending table, then constrain its column widths	half a day	Feature actually works
Emit HTML instead of PDF	~1 hour	Reliable, no LaTeX dependency, loses print fidelity
Leave as-is	none	README keeps promising something that never happens
Recommendation: fix the README now, then bisect. The doc fix is the urgent part — you are currently telling users to install two large dependencies for a feature that produces nothing.

Item B — Diagrams and one table under-describe the pipeline
conceptual_overview.jpg (Figure 1, "Conceptual overview of the proposed pipeline") predates the uncertainty stage, as do evaluation_workflow.png and report_generation.png. tbl:method_reporting_outputs also omits it — and that one is text, so it is free to fix.

This matters more than a normal stale-figure issue: MJ1's criticism was precisely that the paper's description of the pipeline did not match the tool. Having fixed that in prose and in tbl:method_pipeline_stages, a reviewer who compares Figure 1 against Table 1 finds them disagreeing about how many stages exist.

Option	Effort	Outcome
Fix tbl:method_reporting_outputs + add a caption note pointing to Table 1 as authoritative	~20 min (I can do it)	Contradiction acknowledged, figure still stale
Also redraw conceptual_overview.jpg	needs you — no source file in the repo	Figure 1 correct
Redraw all three diagrams	needs you	Fully consistent
There are no editable diagram sources in journal_paper/ — only flattened .jpg/.png. So redrawing needs whatever tool you originally used.

Recommendation: let me do the text fixes now; you redraw conceptual_overview.jpg only. The other two are stage-internal and less exposed.

Item C — --build-all artifact contamination
Lowest severity, and already documented with a warning box. For a normal user the behaviour is arguably correct — they want tables for their own datasets. It only bites this repo, where the paper must be built from exactly three.

Option	Effort	Outcome
Documentation only (already done)	done	Relies on you remembering
Add paper_datasets to config.py, pinning which datasets feed manuscript artifacts	~30 min	Paper build deterministic regardless of what else is in datasets/
Require an explicit --datasets list for --paper-tables	~20 min	Safe but adds friction to every call
Recommendation: add paper_datasets. It composes naturally with paper_comparisons, which already pins the corpus pairs, and it removes a footgun that already caught me once during testing.

Suggested order: README PDF honesty (urgent, docs are wrong) → tbl:method_reporting_outputs + caption note → paper_datasets → then the PDF bisect and the Figure 1 redraw when you have time.

Say which of these you want and I'll do them. Nothing further edited.
