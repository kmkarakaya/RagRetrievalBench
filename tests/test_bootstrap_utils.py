"""Tests for the query-level uncertainty stage.

The property worth protecting is determinism: a corpus's intervals must not depend on
how many datasets were evaluated in the same invocation, in what order, or which
metrics were enabled. Everything else in this stage is standard resampling.
"""
import numpy as np
import pytest

from utils import bootstrap_utils as bs


# ----------------------------------------------------------------------------------
# per-cell seeding
# ----------------------------------------------------------------------------------

def test_cell_rng_is_reproducible_for_the_same_keys():
    a = bs.cell_rng(42, 1, 2, 3).integers(0, 100, size=20)
    b = bs.cell_rng(42, 1, 2, 3).integers(0, 100, size=20)
    assert np.array_equal(a, b)


def test_cell_rng_differs_across_keys():
    a = bs.cell_rng(42, 1, 2, 3).integers(0, 1_000_000, size=50)
    for keys in [(1, 2, 4), (1, 3, 3), (2, 2, 3)]:
        other = bs.cell_rng(42, *keys).integers(0, 1_000_000, size=50)
        assert not np.array_equal(a, other), f"stream collision with {keys}"


def test_cell_rng_differs_across_seeds():
    a = bs.cell_rng(42, 0, 0, 0).integers(0, 1_000_000, size=50)
    b = bs.cell_rng(43, 0, 0, 0).integers(0, 1_000_000, size=50)
    assert not np.array_equal(a, b)


def test_cell_rng_is_independent_of_draw_order():
    """Consuming one cell's stream must not shift another's.

    This is the guarantee that a single shared generator cannot give.
    """
    first_alone = bs.cell_rng(42, 9, 9, 9).integers(0, 100, size=10)
    bs.cell_rng(42, 1, 1, 1).integers(0, 100, size=10_000)  # unrelated heavy draw
    first_again = bs.cell_rng(42, 9, 9, 9).integers(0, 100, size=10)
    assert np.array_equal(first_alone, first_again)


# ----------------------------------------------------------------------------------
# bootstrap primitives
# ----------------------------------------------------------------------------------

def test_percentile_ci_brackets_the_mean():
    values = [0.1, 0.4, 0.2, 0.9, 0.5, 0.3, 0.7, 0.6]
    mean, lo, hi = bs.percentile_ci(values, bs.cell_rng(42, 0), B=2000, alpha=0.05)
    assert mean == pytest.approx(sum(values) / len(values))
    assert lo < mean < hi


def test_percentile_ci_handles_empty_input():
    assert bs.percentile_ci([], bs.cell_rng(42, 0), B=100, alpha=0.05) == (0.0, 0.0, 0.0)


def test_paired_ci_detects_a_consistent_difference():
    a = [0.5] * 40
    b = [0.2] * 40
    delta, lo, hi, p = bs.paired_ci(a, b, bs.cell_rng(42, 0), B=2000, alpha=0.05)
    assert delta == pytest.approx(0.3)
    assert bs.excludes_zero({"lo": lo, "hi": hi})
    assert p == pytest.approx(0.0)


def test_paired_ci_reports_no_separation_for_identical_vectors():
    v = [0.1, 0.5, 0.3, 0.9] * 10
    delta, lo, hi, p = bs.paired_ci(v, v, bs.cell_rng(42, 0), B=2000, alpha=0.05)
    assert delta == 0.0
    assert not bs.excludes_zero({"lo": lo, "hi": hi})


def test_paired_ci_cancels_shared_variation():
    """The reason the paired column is the one that discriminates.

    Two models with a small constant gap but large shared per-query variation have
    heavily overlapping marginal intervals, yet the paired interval excludes zero.
    """
    rng = np.random.default_rng(0)
    difficulty = rng.uniform(0, 1, size=60)
    a = np.clip(difficulty + 0.05, 0, 1)
    b = np.clip(difficulty, 0, 1)

    _, a_lo, a_hi = bs.percentile_ci(a, bs.cell_rng(42, 1), B=3000, alpha=0.05)
    _, b_lo, b_hi = bs.percentile_ci(b, bs.cell_rng(42, 2), B=3000, alpha=0.05)
    assert a_lo < b_hi, "marginal intervals should overlap in this construction"

    _, lo, hi, _ = bs.paired_ci(a, b, bs.cell_rng(42, 3), B=3000, alpha=0.05)
    assert bs.excludes_zero({"lo": lo, "hi": hi})


# ----------------------------------------------------------------------------------
# per-query metrics
# ----------------------------------------------------------------------------------

def test_per_query_metrics_drops_queries_without_positives():
    assert bs.per_query_metrics(["a", "b"], set(), k=10) is None


def test_per_query_metrics_perfect_ranking():
    m = bs.per_query_metrics(["a", "b", "c"], {"a", "b"}, k=10)
    assert m["hit_rate"] == 1.0
    assert m["mrr"] == 1.0
    assert m["recall"] == 1.0
    assert m["map"] == pytest.approx(1.0)
    assert m["ndcg"] == pytest.approx(1.0)


def test_per_query_metrics_miss():
    m = bs.per_query_metrics(["x", "y"], {"a"}, k=10)
    assert m["hit_rate"] == 0.0
    assert m["mrr"] == 0.0
    assert m["map"] == 0.0


def test_per_query_metrics_respects_cutoff():
    """A relevant document past the cutoff must not count."""
    ranked = ["x"] * 9 + ["a"]
    assert bs.per_query_metrics(ranked, {"a"}, k=10)["hit_rate"] == 1.0
    assert bs.per_query_metrics(ranked, {"a"}, k=5)["hit_rate"] == 0.0


def test_map_denominator_uses_min_k_and_relevant_count():
    """AP is normalised by min(k, |R|), matching InformationRetrievalEvaluator."""
    m = bs.per_query_metrics(["a", "b"], {"a", "b", "c", "d"}, k=2)
    assert m["map"] == pytest.approx(1.0)


# ----------------------------------------------------------------------------------
# aggregation
# ----------------------------------------------------------------------------------

def _scored(vectors):
    return {lab: {"per_query": {m: list(v) for m in bs.METRICS}, "qids": list(range(len(v)))}
            for lab, v in vectors.items()}


def test_compute_dataset_bootstrap_picks_the_leader_and_pairs_against_it():
    scored = _scored({"M1": [0.9] * 30, "M2": [0.4] * 30, "M5": [0.5] * 30})
    block = bs.compute_dataset_bootstrap("demo", scored=scored, B=500, alpha=0.05, seed=42)

    assert block["leader"] == "M1"
    assert block["n_queries"] == 30
    assert set(block["paired_map_vs_leader"]) == {"M2", "M5"}
    assert "M1" not in block["paired_map_vs_leader"], "leader is not paired against itself"
    assert block["paired_map_vs_leader"]["M2"]["delta"] == pytest.approx(0.5)


def test_compute_dataset_bootstrap_is_order_independent():
    """Same corpus, computed twice with unrelated work in between."""
    scored = _scored({"M1": [0.3, 0.8, 0.5, 0.6] * 8, "M5": [0.2, 0.7, 0.4, 0.9] * 8})
    first = bs.compute_dataset_bootstrap("demo", scored=scored, B=800, alpha=0.05, seed=42)
    bs.compute_dataset_bootstrap("other", scored=scored, B=800, alpha=0.05, seed=42)
    second = bs.compute_dataset_bootstrap("demo", scored=scored, B=800, alpha=0.05, seed=42)
    assert first == second


def test_compute_pooled_bootstrap_marks_itself_unstratified():
    vectors = {"a": {"M1": [0.5] * 10}, "b": {"M1": [0.1] * 20}}
    pooled = bs.compute_pooled_bootstrap(vectors, B=500, alpha=0.05, seed=42)
    assert pooled["stratified"] is False
    assert pooled["n_queries"] == 30
    # pooled mean is query-weighted, not the macro mean of 0.5 and 0.1
    assert pooled["ci_map"]["M1"]["mean"] == pytest.approx((0.5 * 10 + 0.1 * 20) / 30)
