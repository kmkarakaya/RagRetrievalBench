"""Draw the manuscript's conceptual pipeline overview (Figure 1).

The figure is drawn from shapes and text only, so it stays sharp at any print size.
It follows the stage sequence of Table "tbl:method_pipeline_stages" in
journal_paper/method.tex and overwrites journal_paper/conceptual_overview.png, the
filename referenced by the figure environment there.

    python utils/generate_conceptual_overview_figure.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "journal_paper" / "conceptual_overview.png"

INK = "#1b2a41"
MUTED = "#4a5568"
GRAY_FILL = "#eeeeee"
GRAY_EDGE = "#9a9a9a"
TEAL_FILL = "#cfe6e1"
TEAL_EDGE = "#4f9a8c"
BLUE_FILL = "#d6e4f5"
BLUE_EDGE = "#4a78b5"
CONTAINER_FILL = "#f4f7fa"

# Stage columns, left to right. x is the column center in axis units (0.1 inch).
STAGE_X = [6.5, 19.0, 31.5, 44.0, 56.5, 69.0, 81.5, 94.0]
BOX_W = 9.6
BOX_BOTTOM, BOX_TOP = 15.0, 29.0
BOX_MID = (BOX_BOTTOM + BOX_TOP) / 2


def _box(ax, x, y0, y1, fill, edge, w=BOX_W, lw=1.4):
    ax.add_patch(FancyBboxPatch(
        (x - w / 2, y0), w, y1 - y0, boxstyle="round,pad=0,rounding_size=0.9",
        facecolor=fill, edgecolor=edge, linewidth=lw, zorder=2))


def _arrow(ax, x0, y0, x1, y1, color=INK, lw=2.2, style="-|>", ms=14, rad=0.0, z=3):
    ax.add_patch(FancyArrowPatch(
        (x0, y0), (x1, y1), arrowstyle=style, mutation_scale=ms, color=color,
        linewidth=lw, connectionstyle=f"arc3,rad={rad}", zorder=z, shrinkA=0, shrinkB=0))


def _document(ax, x, y, w=4.0, h=5.2, lines=4, fill="white"):
    """A page with a folded corner and text lines; (x, y) is the lower-left corner."""
    fold = 1.1
    ax.add_patch(Polygon(
        [(x, y), (x + w, y), (x + w, y + h - fold), (x + w - fold, y + h), (x, y + h)],
        closed=True, facecolor=fill, edgecolor=INK, linewidth=1.3, zorder=4))
    ax.plot([x + w - fold, x + w - fold, x + w], [y + h, y + h - fold, y + h - fold],
            color=INK, linewidth=1.1, zorder=5)
    for i in range(lines):
        ly = y + h - 1.9 - i * (h - 2.6) / max(lines - 1, 1)
        ax.plot([x + 0.7, x + w - 0.7], [ly, ly], color=INK, linewidth=1.0, zorder=5)


def _document_stack(ax, x, y, n=3, w=4.0, h=5.2, step=0.8):
    for i in reversed(range(n)):
        _document(ax, x + i * step, y - i * step, w=w, h=h, lines=4 if i == 0 else 0)


def draw(output_path: Path) -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans"})
    fig = plt.figure(figsize=(10.0, 4.3))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 43)
    ax.axis("off")

    # Dataset-isolated container: everything inside runs once per corpus.
    ax.add_patch(FancyBboxPatch(
        (0.8, 8.6), 98.4, 33.4, boxstyle="round,pad=0,rounding_size=2.0",
        facecolor=CONTAINER_FILL, edgecolor=GRAY_EDGE, linewidth=1.3,
        linestyle=(0, (5, 3)), zorder=0))
    ax.text(50, 39.3, "Dataset-isolated and reproducible benchmarking workflow",
            ha="center", va="center", fontsize=13.5, fontweight="bold", color=INK)

    titles = [
        "Dataset\nRouting", "PDF\nIngestion", "Chunking", "Query\nGeneration",
        "Relevance\nConstruction", "Multi-Model\nIndexing and\nEvaluation",
        "Uncertainty\nEstimation", "Reporting",
    ]
    artifacts = [
        "document\ncollections", "PDF\ncollection", "chunked\ncorpus",
        "synthetic\nqueries", "qrels", "per-model\ncollections and\nrankings",
        "confidence\nintervals", "",
    ]
    for x, title, artifact in zip(STAGE_X, titles, artifacts):
        ax.text(x, 33.4, title, ha="center", va="center", fontsize=11,
                fontweight="bold", color=INK, linespacing=1.15)
        if artifact:
            ax.text(x, BOX_BOTTOM - 1.0, artifact, ha="center", va="top", fontsize=10.5,
                    color=MUTED, linespacing=1.1)

    # 1. Dataset routing: the local collections, one routed at a time.
    _document_stack(ax, STAGE_X[0] - 2.8, BOX_MID - 1.0)

    # 2. PDF ingestion.
    x = STAGE_X[1]
    _box(ax, x, BOX_BOTTOM, BOX_TOP, GRAY_FILL, GRAY_EDGE)
    _document(ax, x - 2.2, BOX_MID - 3.0, w=4.4, h=6.0, lines=5)

    # 3. Chunking: a grid of segments.
    x = STAGE_X[2]
    _box(ax, x, BOX_BOTTOM, BOX_TOP, GRAY_FILL, GRAY_EDGE)
    for row in range(2):
        for col in range(3):
            ax.add_patch(Rectangle((x - 3.9 + col * 2.4, BOX_MID + 0.4 - row * 2.8), 1.9, 2.2,
                                   facecolor="white", edgecolor=INK, linewidth=1.2, zorder=4))
    ax.text(x + 3.9, BOX_MID - 1.6, "...", ha="center", va="center", fontsize=11, color=INK)

    # 4. Query generation (LLM-assisted): question bubbles.
    x = STAGE_X[3]
    _box(ax, x, BOX_BOTTOM, BOX_TOP, TEAL_FILL, TEAL_EDGE)
    for bx, by, mark in ((x - 3.6, BOX_MID + 0.6, "?"), (x - 0.6, BOX_MID - 3.2, "?")):
        ax.add_patch(FancyBboxPatch((bx, by), 4.2, 3.0, boxstyle="round,pad=0,rounding_size=1.0",
                                    facecolor="white", edgecolor=INK, linewidth=1.2, zorder=4))
        ax.text(bx + 2.1, by + 1.5, mark, ha="center", va="center", fontsize=13,
                fontweight="bold", color=INK, zorder=5)

    # 5. Relevance construction (LLM-assisted): binary judgments.
    x = STAGE_X[4]
    _box(ax, x, BOX_BOTTOM, BOX_TOP, TEAL_FILL, TEAL_EDGE)
    for i, label in enumerate(("1", "0", "1")):
        cy = BOX_MID + 3.0 - i * 3.0
        ax.add_patch(Rectangle((x - 3.6, cy - 0.9), 1.8, 1.8, facecolor="white",
                               edgecolor=INK, linewidth=1.2, zorder=4))
        ax.text(x - 2.7, cy, label, ha="center", va="center", fontsize=10,
                fontweight="bold", color=INK, zorder=5)
        ax.plot([x - 1.0, x + 3.4], [cy, cy], color=INK, linewidth=1.3, zorder=4)

    # 6. Multi-model indexing and evaluation: one collection per candidate model.
    x = STAGE_X[5]
    model_rows = [(BOX_TOP - 2.0, "Model 1"), (BOX_MID, "Model 2"), (BOX_BOTTOM + 2.0, "Model n")]
    for cy, label in model_rows:
        _box(ax, x, cy - 1.7, cy + 1.7, "white", GRAY_EDGE, lw=1.3)
        ax.text(x, cy, label, ha="center", va="center", fontsize=11, color=INK, zorder=5)
    ax.text(x, (BOX_MID + BOX_BOTTOM + 2.0) / 2, "⋮", ha="center", va="center",
            fontsize=11, color=INK)

    # 7. Uncertainty estimation: interval glyphs.
    x = STAGE_X[6]
    _box(ax, x, BOX_BOTTOM, BOX_TOP, BLUE_FILL, BLUE_EDGE)
    for i, (lo, mid, hi) in enumerate(((-3.0, 0.3, 3.2), (-2.4, -0.2, 2.0), (-3.4, 0.6, 2.6))):
        cy = BOX_MID + 3.2 - i * 3.2
        ax.plot([x + lo, x + hi], [cy, cy], color=INK, linewidth=1.4, zorder=4)
        for end in (lo, hi):
            ax.plot([x + end, x + end], [cy - 0.6, cy + 0.6], color=INK, linewidth=1.4, zorder=4)
        ax.plot(x + mid, cy, "o", color=INK, markersize=5, zorder=5)

    # 8. Reporting: dataset-level report (primary) and aggregate report (secondary).
    x = STAGE_X[7]
    rep_top = (BOX_MID + 0.5, BOX_TOP + 0.3)
    rep_bottom = (BOX_BOTTOM - 0.3, BOX_MID - 0.5)
    _box(ax, x, *rep_top, BLUE_FILL, BLUE_EDGE)
    _box(ax, x, *rep_bottom, GRAY_FILL, GRAY_EDGE)
    ax.text(x, rep_top[1] - 1.4, "Dataset-level", ha="center", va="center", fontsize=9.5,
            color=INK)
    ax.plot([x - 3.4, x - 1.6, x - 0.2, x + 1.4, x + 3.2],
            [rep_top[0] + 1.2, rep_top[0] + 2.6, rep_top[0] + 2.0, rep_top[0] + 3.4, rep_top[0] + 3.9],
            color=INK, linewidth=1.3, marker="o", markersize=3.5, zorder=4)
    ax.text(x, rep_bottom[1] - 1.4, "Aggregate", ha="center", va="center", fontsize=9.5,
            color=INK)
    for i, h in enumerate((1.6, 2.6, 1.9, 3.2)):
        ax.add_patch(Rectangle((x - 3.0 + i * 1.6, rep_bottom[0] + 0.9), 1.0, h,
                               facecolor=INK, edgecolor="none", zorder=4))

    # Flow arrows between stage columns.
    gap = (STAGE_X[1] - STAGE_X[0] - BOX_W) / 2
    for left, right in zip(STAGE_X[:4], STAGE_X[1:5]):
        _arrow(ax, left + BOX_W / 2 + gap * 0.25, BOX_MID, right - BOX_W / 2 - gap * 0.25, BOX_MID)
    for left, right in ((STAGE_X[6], STAGE_X[7]),):
        _arrow(ax, left + BOX_W / 2 + gap * 0.25, BOX_MID, right - BOX_W / 2 - gap * 0.25, BOX_MID)

    # Qrels and queries fan out to every model collection, whose rankings fan in to
    # the uncertainty stage.
    for cy, _ in model_rows:
        _arrow(ax, STAGE_X[4] + BOX_W / 2, BOX_MID, STAGE_X[5] - BOX_W / 2, cy,
               color=TEAL_EDGE, lw=2.4, ms=12)
        _arrow(ax, STAGE_X[5] + BOX_W / 2, cy, STAGE_X[6] - BOX_W / 2, BOX_MID,
               color=BLUE_EDGE, lw=2.4, ms=12)

    # Reports leave the per-corpus container.
    ax.plot([STAGE_X[7], STAGE_X[7]], [BOX_BOTTOM - 0.3, 7.6], color=MUTED, linewidth=1.2,
            linestyle=(0, (3, 2)), zorder=1)
    _document_stack(ax, STAGE_X[7] - 2.2, 2.0, w=3.6, h=4.6, step=0.7)
    ax.text(STAGE_X[7] - 4.2, 4.3, "benchmark reports", ha="right", va="center",
            fontsize=11.5, fontweight="bold", color=INK)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=400, facecolor="white")
    plt.close(fig)
    print(f"Wrote {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()
    draw(args.output)


if __name__ == "__main__":
    main()
