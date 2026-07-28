"""Check the manuscript's hand-written numbers against the pipeline's artifacts.

Most of the paper's data tables are generated (`utils/paper_artifacts.py`) and so
cannot drift. What remains hand-written is prose, captions, and the one table whose
cells are partly editorial. Those are the places a stale number can survive a rerun
unnoticed, so they are checked here.

Exits non-zero when anything disagrees, which makes it usable as a release gate:

    python rag_benchmark.py --verify-paper
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config as cfg  # noqa: E402
from utils import bootstrap_utils as bs  # noqa: E402

PAPER = PROJECT_ROOT / "journal_paper"


def _load_raw(dataset: str) -> dict:
    path = cfg.get_latest_raw_results(dataset)
    if path is None:
        raise FileNotFoundError(f"No raw_results_*.json for {dataset}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _section_text() -> str:
    """All hand-authored manuscript text (generated fragments excluded)."""
    parts = []
    for path in sorted(PAPER.glob("*.tex")):
        if path.name.startswith("tbl_"):
            continue
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def _alias_to_model() -> dict[str, str]:
    return {f"M{i + 1}": m["model_name"] for i, m in enumerate(cfg.embedding_models)}


# ----------------------------------------------------------------------------------
# checks
# ----------------------------------------------------------------------------------

def check_generated_fragments_present(findings: list[str]) -> int:
    """Every \\input{tbl_*.tex} must resolve, and every fragment must be referenced."""
    text = _section_text()
    referenced = set(re.findall(r"\\input\{(tbl_[a-z0-9_]+)\.tex\}", text))
    on_disk = {p.stem for p in PAPER.glob("tbl_*.tex")}
    checks = 0
    for name in sorted(referenced - on_disk):
        findings.append(f"manuscript \\inputs {name}.tex but the fragment does not exist "
                        f"(run: python rag_benchmark.py --paper-tables)")
    for name in sorted(on_disk - referenced):
        findings.append(f"fragment {name}.tex is generated but never \\input by the manuscript")
    checks += len(referenced | on_disk)
    return checks


def check_dataset_result_summary(findings: list[str]) -> int:
    """tbl:dataset_result_summary keeps an editorial prose column, so it stays manual.

    Its two numeric columns (top MAP@10, mean MAP@10 across models) are checked here.
    """
    text = _section_text()
    marker = r"\label{tbl:dataset_result_summary}"
    if marker not in text:
        return 0
    body = text[text.index(marker):]
    body = body[:body.index(r"\end{tabular}")]

    checks = 0
    for dataset in cfg.discover_available_datasets():
        escaped = dataset.replace("_", r"\_")
        row = next((l for l in body.splitlines() if l.strip().startswith(escaped + " &")), None)
        if row is None:
            continue
        nums = re.findall(r"\d\.\d{4}", row)
        if len(nums) < 2:
            findings.append(f"tbl:dataset_result_summary[{dataset}]: expected two MAP@10 values")
            continue
        data = _load_raw(dataset)
        maps = [float(b["metrics"]["map"]) for b in data["models"].values()]
        expected = [f"{max(maps):.4f}", f"{sum(maps) / len(maps):.4f}"]
        for got, exp, what in zip(nums[:2], expected, ["top MAP@10", "mean MAP@10"]):
            checks += 1
            if got != exp:
                findings.append(
                    f"tbl:dataset_result_summary[{dataset}] {what}: paper {got}, artifacts {exp}")
    return checks


def check_inline_paired_intervals(findings: list[str]) -> int:
    """Paired intervals quoted in the results prose must match the bootstrap blocks.

    These claims carry the paper's argument (whether a corpus separates its top two
    candidates), so a stale digit here is worse than a stale digit in a table.
    """
    text = _section_text()
    pattern = re.compile(
        r"\\texttt\{(M\d)\}\$-\$\\texttt\{(M\d)\}[^.]*?"
        r"\$([+-]\d\.\d{3})\$ \[\$([+-]\d\.\d{3})\$, \$([+-]\d\.\d{3})\$\]")

    blocks = {}
    for dataset in cfg.discover_available_datasets():
        path = bs.bootstrap_output_path(dataset)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                blocks[dataset] = json.load(f)

    checks = 0
    for leader, other, delta, lo, hi in pattern.findall(text):
        match = None
        for dataset, block in blocks.items():
            if block.get("leader") != leader:
                continue
            entry = block.get("paired_map_vs_leader", {}).get(other)
            if entry and f"{entry['delta']:+.3f}" == delta:
                match = (dataset, entry)
                break
        if match is None:
            findings.append(
                f"inline interval {leader}-{other} {delta} [{lo}, {hi}] matches no "
                f"bootstrap block (stale, or the bootstrap stage has not been rerun)")
            continue
        dataset, entry = match
        checks += 2
        if f"{entry['lo']:+.3f}" != lo or f"{entry['hi']:+.3f}" != hi:
            findings.append(
                f"inline interval {leader}-{other} on {dataset}: paper [{lo}, {hi}], "
                f"artifacts [{entry['lo']:+.3f}, {entry['hi']:+.3f}]")
    return checks


def check_scored_query_counts(findings: list[str]) -> int:
    """Scored-query counts quoted in prose must match the bootstrap blocks."""
    text = _section_text()
    checks = 0
    total = 0
    for dataset in cfg.discover_available_datasets():
        path = bs.bootstrap_output_path(dataset)
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            total += json.load(f)["n_queries"]
    if total:
        checks += 1
        if re.search(r"\b%d scored queries\b" % total, text) is None:
            findings.append(
                f"prose never states the pooled scored-query total of {total}; "
                f"check the aggregate uncertainty discussion")
    return checks


def main() -> int:
    findings: list[str] = []
    checks = 0
    for fn in (check_generated_fragments_present,
               check_dataset_result_summary,
               check_inline_paired_intervals,
               check_scored_query_counts):
        try:
            checks += fn(findings)
        except FileNotFoundError as e:
            findings.append(f"{fn.__name__}: {e}")

    print(f"verify-paper: {checks} values checked against run artifacts")
    if findings:
        print(f"\n{len(findings)} problem(s):")
        for f in findings:
            print(f"  - {f}")
        return 1
    print("All hand-written manuscript numbers agree with the pipeline artifacts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
