import pytest

from utils.aggregate_report_utils import (
    extract_query_latency_matrix,
    compute_weighted_query_latency_summary,
    validate_metric_compatibility,
    get_common_metrics,
)


def _build_datasets_fixture():
    return {
        "dataset_a": {
            "models": {
                "model_1": {
                    "timing": {
                        "avg_query_latency_ms": 10.0,
                        "queries_timed": 100,
                    }
                },
                "model_2": {
                    "timing": {
                        "avg_query_latency_ms": 30.0,
                        "queries_timed": 100,
                    }
                },
            }
        },
        "dataset_b": {
            "models": {
                "model_1": {
                    "timing": {
                        "avg_query_latency_ms": 20.0,
                        "queries_timed": 50,
                    }
                },
                "model_2": {
                    "timing": {}
                },
            }
        },
    }


def test_extract_query_latency_matrix():
    datasets = _build_datasets_fixture()

    matrix = extract_query_latency_matrix(datasets)

    assert matrix["model_1"]["dataset_a"] == pytest.approx(10.0)
    assert matrix["model_1"]["dataset_b"] == pytest.approx(20.0)
    assert matrix["model_2"]["dataset_a"] == pytest.approx(30.0)
    assert matrix["model_2"]["dataset_b"] is None


def test_compute_weighted_query_latency_summary():
    datasets = _build_datasets_fixture()

    summary = compute_weighted_query_latency_summary(datasets)

    # model_1 weighted mean: (10*100 + 20*50) / 150 = 13.3333
    assert summary["model_1"]["weighted_mean_latency_ms"] == pytest.approx(13.3333333333)
    assert summary["model_1"]["best_latency_ms"] == pytest.approx(10.0)
    assert summary["model_1"]["worst_latency_ms"] == pytest.approx(20.0)
    assert summary["model_1"]["datasets_with_latency_data"] == 2
    assert summary["model_1"]["total_queries_timed"] == 150

    # model_2 only has dataset_a latency
    assert summary["model_2"]["weighted_mean_latency_ms"] == pytest.approx(30.0)
    assert summary["model_2"]["best_latency_ms"] == pytest.approx(30.0)
    assert summary["model_2"]["worst_latency_ms"] == pytest.approx(30.0)
    assert summary["model_2"]["datasets_with_latency_data"] == 1
    assert summary["model_2"]["total_queries_timed"] == 100


def test_metric_compatibility_includes_hit_rate():
    datasets = {
        "dataset_a": {
            "config": {
                "metric_flags": {
                    "compute_map": True,
                    "compute_recall": True,
                    "compute_precision": True,
                    "compute_ndcg": True,
                    "compute_mrr": True,
                    "compute_hit_rate": True,
                }
            }
        },
        "dataset_b": {
            "config": {
                "metric_flags": {
                    "compute_map": True,
                    "compute_recall": True,
                    "compute_precision": False,
                    "compute_ndcg": True,
                    "compute_mrr": True,
                    "compute_hit_rate": True,
                }
            }
        },
    }

    report = validate_metric_compatibility(datasets)
    assert report["status"] == "ok"
    assert "compute_hit_rate" in report["common_metrics"]
    common = get_common_metrics(datasets)
    assert "hit_rate" in common
    assert "precision" not in common
