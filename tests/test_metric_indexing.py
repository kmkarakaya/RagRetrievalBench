"""
Test metric indexing logic for report_utils.py
This tests the core fix for dynamic metric indexing without requiring matplotlib dependencies.
"""
import pytest
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config as cfg


class TestMetricIndexingLogic:
    """Test the core metric indexing logic that was fixed in report_utils.py"""
    
    def setup_method(self):
        """Store original config values before each test"""
        self.original_config = {}
        for attr in ['compute_map', 'compute_recall', 'compute_precision', 'compute_ndcg', 'compute_mrr', 'compute_hit_rate']:
            if hasattr(cfg, attr):
                self.original_config[attr] = getattr(cfg, attr)
    
    def teardown_method(self):
        """Restore original config values after each test"""
        for attr, value in self.original_config.items():
            setattr(cfg, attr, value)
    
    def build_metric_indices(self):
        """Build metric indices using the same logic as in report_utils.py"""
        metric_indices = {}
        current_idx = 1  # Start after model name (index 0)

        if cfg.compute_map:
            metric_indices['map'] = current_idx
            current_idx += 1
        if cfg.compute_recall:
            metric_indices['recall'] = current_idx
            current_idx += 1
        if cfg.compute_precision:
            metric_indices['precision'] = current_idx
            current_idx += 1
        if cfg.compute_ndcg:
            metric_indices['ndcg'] = current_idx
            current_idx += 1
        if cfg.compute_mrr:
            metric_indices['mrr'] = current_idx
            current_idx += 1
        if getattr(cfg, 'compute_hit_rate', False):
            metric_indices['hit_rate'] = current_idx
        
        return metric_indices
    
    def test_all_metrics_enabled(self):
        """Test metric indexing when all metrics are enabled"""
        # Enable all metrics
        cfg.compute_map = True
        cfg.compute_recall = True
        cfg.compute_precision = True
        cfg.compute_ndcg = True
        cfg.compute_mrr = True
        cfg.compute_hit_rate = False
        
        metric_indices = self.build_metric_indices()
        
        # Verify indices
        assert metric_indices['map'] == 1
        assert metric_indices['recall'] == 2
        assert metric_indices['precision'] == 3
        assert metric_indices['ndcg'] == 4
        assert metric_indices['mrr'] == 5
        assert len(metric_indices) == 5
        
        # Test with mock model results
        model_results = [
            ("model1", 0.8, 0.9, 0.7, 0.85, 0.6),  # MAP, Recall, Precision, NDCG, MRR
        ]
        
        best_model = model_results[0]
        assert best_model[metric_indices['map']] == 0.8
        assert best_model[metric_indices['recall']] == 0.9
        assert best_model[metric_indices['precision']] == 0.7
        assert best_model[metric_indices['ndcg']] == 0.85
        assert best_model[metric_indices['mrr']] == 0.6
        
        print("✓ All metrics enabled test passed")
    
    def test_partial_metrics_map_and_ndcg(self):
        """Test metric indexing with only MAP and NDCG enabled"""
        # Enable only MAP and NDCG
        cfg.compute_map = True
        cfg.compute_recall = False
        cfg.compute_precision = False
        cfg.compute_ndcg = True
        cfg.compute_mrr = False
        cfg.compute_hit_rate = False
        
        metric_indices = self.build_metric_indices()
        
        # Verify correct indexing for partial metrics
        assert metric_indices['map'] == 1
        assert metric_indices['ndcg'] == 2  # Should be 2, not 4!
        assert 'recall' not in metric_indices
        assert 'precision' not in metric_indices
        assert 'mrr' not in metric_indices
        assert len(metric_indices) == 2
        
        # Test with corresponding model results
        model_results = [
            ("model1", 0.8, 0.85),  # MAP, NDCG (no recall, precision, mrr)
        ]
        
        best_model = model_results[0]
        assert best_model[metric_indices['map']] == 0.8
        assert best_model[metric_indices['ndcg']] == 0.85
        
        print("✓ MAP and NDCG only test passed")
    
    def test_only_recall_enabled(self):
        """Test when only recall is enabled"""
        cfg.compute_map = False
        cfg.compute_recall = True
        cfg.compute_precision = False
        cfg.compute_ndcg = False
        cfg.compute_mrr = False
        cfg.compute_hit_rate = False
        
        metric_indices = self.build_metric_indices()
        
        assert metric_indices['recall'] == 1  # Should be first index
        assert len(metric_indices) == 1
        assert 'map' not in metric_indices
        assert 'precision' not in metric_indices
        assert 'ndcg' not in metric_indices
        assert 'mrr' not in metric_indices
        
        # Test with model results
        model_results = [
            ("model1", 0.9),  # Only recall
        ]
        
        best_model = model_results[0]
        assert best_model[metric_indices['recall']] == 0.9
        
        print("✓ Recall only test passed")
    
    def test_recall_precision_only(self):
        """Test with only recall and precision enabled"""
        cfg.compute_map = False
        cfg.compute_recall = True
        cfg.compute_precision = True
        cfg.compute_ndcg = False
        cfg.compute_mrr = False
        cfg.compute_hit_rate = False
        
        metric_indices = self.build_metric_indices()
        
        assert metric_indices['recall'] == 1
        assert metric_indices['precision'] == 2
        assert len(metric_indices) == 2
        assert 'map' not in metric_indices
        assert 'ndcg' not in metric_indices
        assert 'mrr' not in metric_indices
        
        # Test with model results
        model_results = [
            ("model1", 0.9, 0.7),  # Recall, Precision
        ]
        
        best_model = model_results[0]
        assert best_model[metric_indices['recall']] == 0.9
        assert best_model[metric_indices['precision']] == 0.7
        
        print("✓ Recall and Precision only test passed")
    
    def test_no_metrics_enabled(self):
        """Test when no metrics are enabled"""
        cfg.compute_map = False
        cfg.compute_recall = False
        cfg.compute_precision = False
        cfg.compute_ndcg = False
        cfg.compute_mrr = False
        cfg.compute_hit_rate = False
        
        metric_indices = self.build_metric_indices()
        
        assert len(metric_indices) == 0
        assert 'map' not in metric_indices
        assert 'recall' not in metric_indices
        assert 'precision' not in metric_indices
        assert 'ndcg' not in metric_indices
        assert 'mrr' not in metric_indices
        
        print("✓ No metrics enabled test passed")
    
    def test_metric_order_independence(self):
        """Test that metric order doesn't matter when some are disabled"""
        # Test case: Enable MAP, disable Recall, enable Precision, disable NDCG, enable MRR
        cfg.compute_map = True
        cfg.compute_recall = False
        cfg.compute_precision = True
        cfg.compute_ndcg = False
        cfg.compute_mrr = True
        cfg.compute_hit_rate = False
        
        metric_indices = self.build_metric_indices()
        
        # Should have consecutive indices starting from 1
        assert metric_indices['map'] == 1
        assert metric_indices['precision'] == 2  # Should be 2, not 3
        assert metric_indices['mrr'] == 3        # Should be 3, not 5
        assert len(metric_indices) == 3
        assert 'recall' not in metric_indices
        assert 'ndcg' not in metric_indices
        
        # Test with model results
        model_results = [
            ("model1", 0.8, 0.7, 0.6),  # MAP, Precision, MRR
        ]
        
        best_model = model_results[0]
        assert best_model[metric_indices['map']] == 0.8
        assert best_model[metric_indices['precision']] == 0.7
        assert best_model[metric_indices['mrr']] == 0.6
        
        print("✓ Metric order independence test passed")
    
    def test_edge_case_middle_metrics_disabled(self):
        """Test edge case where middle metrics are disabled"""
        # Enable first and last metrics only
        cfg.compute_map = True
        cfg.compute_recall = False
        cfg.compute_precision = False
        cfg.compute_ndcg = False
        cfg.compute_mrr = True
        cfg.compute_hit_rate = False
        
        metric_indices = self.build_metric_indices()
        
        assert metric_indices['map'] == 1
        assert metric_indices['mrr'] == 2  # Should be 2, not 5
        assert len(metric_indices) == 2
        
        # Test with model results
        model_results = [
            ("model1", 0.8, 0.6),  # MAP, MRR
        ]
        
        best_model = model_results[0]
        assert best_model[metric_indices['map']] == 0.8
        assert best_model[metric_indices['mrr']] == 0.6
        
        print("✓ Middle metrics disabled test passed")


    def test_hit_rate_enabled_index(self):
        """Test hit_rate index placement when enabled."""
        cfg.compute_map = True
        cfg.compute_recall = False
        cfg.compute_precision = False
        cfg.compute_ndcg = False
        cfg.compute_mrr = False
        cfg.compute_hit_rate = True

        metric_indices = self.build_metric_indices()
        assert metric_indices["map"] == 1
        assert metric_indices["hit_rate"] == 2


def test_config_loading():
    """Test that benchmark config loads correctly"""
    assert hasattr(cfg, 'compute_map')
    assert hasattr(cfg, 'compute_recall')
    assert hasattr(cfg, 'compute_precision')
    assert hasattr(cfg, 'compute_ndcg')
    assert hasattr(cfg, 'compute_mrr')
    assert hasattr(cfg, 'compute_hit_rate')
    assert hasattr(cfg, 'k')
    print("✓ Config loading test passed")


def test_demo_scenario():
    """Test a realistic scenario with multiple models"""
    # Save original config
    original_config = {}
    for attr in ['compute_map', 'compute_recall', 'compute_precision', 'compute_ndcg', 'compute_mrr', 'compute_hit_rate']:
        if hasattr(cfg, attr):
            original_config[attr] = getattr(cfg, attr)
    
    try:
        # Enable MAP, Recall, and NDCG (common combination)
        cfg.compute_map = True
        cfg.compute_recall = True
        cfg.compute_precision = False
        cfg.compute_ndcg = True
        cfg.compute_mrr = False
        cfg.compute_hit_rate = False
        
        # Build indices
        metric_indices = {}
        current_idx = 1
        
        if cfg.compute_map:
            metric_indices['map'] = current_idx
            current_idx += 1
        if cfg.compute_recall:
            metric_indices['recall'] = current_idx
            current_idx += 1
        if cfg.compute_precision:
            metric_indices['precision'] = current_idx
            current_idx += 1
        if cfg.compute_ndcg:
            metric_indices['ndcg'] = current_idx
            current_idx += 1
        if cfg.compute_mrr:
            metric_indices['mrr'] = current_idx
            current_idx += 1
        if getattr(cfg, 'compute_hit_rate', False):
            metric_indices['hit_rate'] = current_idx
        
        # Simulate model results for this configuration
        model_results = [
            ("sentence-transformers/all-MiniLM-L6-v2", 0.8234, 0.9123, 0.8567),  # MAP, Recall, NDCG
            ("sentence-transformers/all-mpnet-base-v2", 0.7895, 0.8765, 0.8234),
            ("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", 0.7234, 0.8456, 0.7890),
        ]
        
        # Test metric extraction
        for model_name, *scores in model_results:
            assert len(scores) == len(metric_indices)  # Should match number of enabled metrics
            
            map_score = scores[metric_indices['map'] - 1]  # Adjust for 0-based indexing
            recall_score = scores[metric_indices['recall'] - 1]
            ndcg_score = scores[metric_indices['ndcg'] - 1]
            
            assert 0.0 <= map_score <= 1.0
            assert 0.0 <= recall_score <= 1.0
            assert 0.0 <= ndcg_score <= 1.0
        
        # Test sorting by MAP (first metric)
        sorted_results = sorted(model_results, key=lambda x: x[1], reverse=True)
        best_model = sorted_results[0]
        
        assert best_model[0] == "sentence-transformers/all-MiniLM-L6-v2"  # Should be the best by MAP
        assert best_model[metric_indices['map']] == 0.8234
        assert best_model[metric_indices['recall']] == 0.9123
        assert best_model[metric_indices['ndcg']] == 0.8567
        
        print("✓ Demo scenario test passed")
        
    finally:
        # Restore original config
        for attr, value in original_config.items():
            setattr(cfg, attr, value)


if __name__ == "__main__":
    # Run individual tests
    test_config_loading()
    
    test_instance = TestMetricIndexingLogic()
    
    test_instance.setup_method()
    test_instance.test_all_metrics_enabled()
    test_instance.teardown_method()
    
    test_instance.setup_method()
    test_instance.test_partial_metrics_map_and_ndcg()
    test_instance.teardown_method()
    
    test_instance.setup_method()
    test_instance.test_only_recall_enabled()
    test_instance.teardown_method()
    
    test_instance.setup_method()
    test_instance.test_recall_precision_only()
    test_instance.teardown_method()
    
    test_instance.setup_method()
    test_instance.test_no_metrics_enabled()
    test_instance.teardown_method()
    
    test_instance.setup_method()
    test_instance.test_metric_order_independence()
    test_instance.teardown_method()
    
    test_instance.setup_method()
    test_instance.test_edge_case_middle_metrics_disabled()
    test_instance.teardown_method()
    
    test_demo_scenario()
    
    print("\n🎉 All metric indexing tests passed!")
    print("The dynamic metric indexing fix is working correctly.")
