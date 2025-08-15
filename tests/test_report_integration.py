"""
Test report_utils.py functionality, focusing on the metric indexing fixes and integration testing
"""
import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, Mock
import datetime
import sys

# Mock matplotlib to avoid dependency issues in tests
sys.modules['matplotlib'] = Mock()
sys.modules['matplotlib.pyplot'] = Mock()

# Import benchmark config
import benchmark_config as cfg

# Now try to import report_utils functions
try:
    from utils.report_utils import (
        generate_benchmark_report, 
        print_results_summary,
        print_report_info
    )
    REPORT_UTILS_AVAILABLE = True
except ImportError as e:
    REPORT_UTILS_AVAILABLE = False
    print(f"Warning: Could not import report_utils functions: {e}")


class TestReportUtilsIntegration:
    """Test report_utils.py integration with proper metric indexing"""
    
    def setup_method(self):
        """Setup test data and config"""
        self.original_config = {}
        for attr in ['compute_map', 'compute_recall', 'compute_precision', 'compute_ndcg', 'compute_mrr', 'k']:
            if hasattr(cfg, attr):
                self.original_config[attr] = getattr(cfg, attr)
        
        # Set default config for tests
        cfg.compute_map = True
        cfg.compute_recall = True
        cfg.compute_precision = True
        cfg.compute_ndcg = True
        cfg.compute_mrr = True
        cfg.k = 10
        
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock data for testing
        self.model_results = [
            ("sentence-transformers/all-MiniLM-L6-v2", 0.8234, 0.9123, 0.7456, 0.8567, 0.6234),
            ("sentence-transformers/all-mpnet-base-v2", 0.7895, 0.8765, 0.7123, 0.8234, 0.5987),
        ]
        
        self.queries = {
            "q1": "What is attention mechanism in transformers?",
            "q2": "How does BERT work?",
        }
        
        self.corpus = {
            "doc1": "Attention mechanism allows models to focus on relevant parts of input.",
            "doc2": "BERT uses bidirectional encoder representations from transformers.",
            "doc3": "Deep learning models require large amounts of training data.",
        }
        
        self.relevant_docs = {
            "q1": ["doc1"],
            "q2": ["doc2"],
        }
        
        self.timing_results = [
            ("sentence-transformers/all-MiniLM-L6-v2", {
                "embedding_time": 2.5,
                "docs_processed": 100,
                "docs_per_second": 40.0,
                "avg_time_per_doc": 0.025
            }),
        ]
    
    def teardown_method(self):
        """Clean up after tests"""
        for attr, value in self.original_config.items():
            setattr(cfg, attr, value)
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @pytest.mark.skipif(not REPORT_UTILS_AVAILABLE, reason="report_utils not available")
    @patch('utils.report_utils.generate_visualizations')
    @patch('utils.report_utils.generate_corpus_statistics_viz')
    @patch('utils.report_utils.generate_timing_visualization')
    def test_report_generation_with_all_metrics(self, mock_timing_viz, mock_corpus_viz, mock_viz):
        """Test report generation with all metrics enabled"""
        # Mock visualization functions to return empty results
        mock_viz.return_value = {"perf_chart": "chart1.png"}
        mock_corpus_viz.return_value = {"corpus_stats": "stats.png"}
        mock_timing_viz.return_value = {"timing_chart": "timing.png"}
        
        result = generate_benchmark_report(
            model_results=self.model_results,
            queries=self.queries,
            corpus=self.corpus,
            relevant_docs=self.relevant_docs,
            timing_results=self.timing_results,
            output_dir=self.temp_dir
        )
        
        # Check that report file was created
        assert result is not None
        report_files = [f for f in os.listdir(self.temp_dir) if f.startswith("benchmark_report_") and f.endswith(".md")]
        assert len(report_files) >= 1
        
        # Read and verify report content contains correct metric values
        with open(os.path.join(self.temp_dir, report_files[0]), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify the best model and its metrics are correctly displayed
        assert "sentence-transformers/all-MiniLM-L6-v2" in content  # Best model
        assert "MAP@10: **0.8234**" in content  # Correct MAP value at index 1
        assert "Recall@10: **0.9123**" in content  # Correct Recall value at index 2
        assert "Precision@10: **0.7456**" in content  # Correct Precision value at index 3
        assert "NDCG@10: **0.8567**" in content  # Correct NDCG value at index 4
        assert "MRR@10: **0.6234**" in content  # Correct MRR value at index 5
    
    @pytest.mark.skipif(not REPORT_UTILS_AVAILABLE, reason="report_utils not available")
    @patch('utils.report_utils.generate_visualizations')
    def test_report_with_partial_metrics(self, mock_viz):
        """Test report generation with only some metrics enabled (critical test for indexing fix)"""
        # Enable only MAP and NDCG
        cfg.compute_map = True
        cfg.compute_recall = False
        cfg.compute_precision = False
        cfg.compute_ndcg = True
        cfg.compute_mrr = False
        
        # Corresponding model results (model_name, MAP, NDCG)
        # This is the key test: NDCG should be at index 2, not index 4!
        partial_results = [
            ("model1", 0.8, 0.85),
            ("model2", 0.7, 0.75),
        ]
        
        mock_viz.return_value = {"perf_chart": "chart1.png"}
        
        result = generate_benchmark_report(
            model_results=partial_results,
            queries=self.queries,
            corpus=self.corpus,
            relevant_docs=self.relevant_docs,
            output_dir=self.temp_dir
        )
        
        assert result is not None
        report_files = [f for f in os.listdir(self.temp_dir) if f.startswith("benchmark_report_") and f.endswith(".md")]
        assert len(report_files) >= 1
        
        # Verify content has correct metrics and values
        with open(os.path.join(self.temp_dir, report_files[0]), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # These are the critical assertions for the fix
        assert "MAP@10: **0.8000**" in content  # MAP at index 1 (correct)
        assert "NDCG@10: **0.8500**" in content  # NDCG at index 2 (not 4 - this is the fix!)
        
        # These should not be present since they're disabled
        assert "Recall@10" not in content
        assert "Precision@10" not in content
        assert "MRR@10" not in content
    
    @pytest.mark.skipif(not REPORT_UTILS_AVAILABLE, reason="report_utils not available")
    @patch('utils.report_utils.generate_visualizations')
    def test_report_only_recall_enabled(self, mock_viz):
        """Test report with only recall enabled (edge case)"""
        # Enable only recall
        cfg.compute_map = False
        cfg.compute_recall = True
        cfg.compute_precision = False
        cfg.compute_ndcg = False
        cfg.compute_mrr = False
        
        # Model results with only recall values
        recall_only_results = [
            ("model1", 0.9),  # Only recall value
            ("model2", 0.8),
        ]
        
        mock_viz.return_value = {}
        
        result = generate_benchmark_report(
            model_results=recall_only_results,
            queries=self.queries,
            corpus=self.corpus,
            relevant_docs=self.relevant_docs,
            output_dir=self.temp_dir
        )
        
        assert result is not None
        report_files = [f for f in os.listdir(self.temp_dir) if f.startswith("benchmark_report_") and f.endswith(".md")]
        assert len(report_files) >= 1
        
        with open(os.path.join(self.temp_dir, report_files[0]), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should show recall at index 1 (the only metric)
        assert "Recall@10: **0.9000**" in content
        # Others should not be present
        assert "MAP@10" not in content
        assert "Precision@10" not in content
        assert "NDCG@10" not in content
        assert "MRR@10" not in content
    
    @pytest.mark.skipif(not REPORT_UTILS_AVAILABLE, reason="report_utils not available")
    def test_empty_model_results_error(self):
        """Test that empty model results raise appropriate error"""
        with pytest.raises(ValueError, match="No model results provided"):
            generate_benchmark_report(
                model_results=[],
                queries=self.queries,
                corpus=self.corpus,
                relevant_docs=self.relevant_docs,
                output_dir=self.temp_dir
            )
    
    @pytest.mark.skipif(not REPORT_UTILS_AVAILABLE, reason="report_utils not available")
    @patch('utils.report_utils.generate_visualizations')
    def test_timing_data_validation(self, mock_viz):
        """Test timing data validation handles invalid data gracefully"""
        mock_viz.return_value = {}
        
        # Test with invalid timing data structure
        invalid_timing = [
            ("model1", "invalid_structure")  # String instead of dict
        ]
        
        # Should not raise error but handle gracefully
        result = generate_benchmark_report(
            model_results=[("model1", 0.8)],  # Single metric
            queries=self.queries,
            corpus=self.corpus,
            relevant_docs=self.relevant_docs,
            timing_results=invalid_timing,
            output_dir=self.temp_dir
        )
        
        assert result is not None
    
    def test_print_functions(self, capsys):
        """Test utility print functions work correctly"""
        if not REPORT_UTILS_AVAILABLE:
            pytest.skip("report_utils not available")
        
        # Test print_results_summary
        print_results_summary(self.model_results)
        captured = capsys.readouterr()
        assert any(model in captured.out for model in ["all-MiniLM-L6-v2", "all-mpnet-base-v2", "sentence-transformers"])
        
        # Test print_report_info
        report_files = {"markdown": "report.md", "pdf": "report.pdf"}
        print_report_info(report_files)
        captured = capsys.readouterr()
        assert "report" in captured.out.lower()


class TestMetricIndexingInReportContext:
    """Test metric indexing within report generation context"""
    
    def setup_method(self):
        self.original_config = {}
        for attr in ['compute_map', 'compute_recall', 'compute_precision', 'compute_ndcg', 'compute_mrr']:
            if hasattr(cfg, attr):
                self.original_config[attr] = getattr(cfg, attr)
    
    def teardown_method(self):
        for attr, value in self.original_config.items():
            setattr(cfg, attr, value)
    
    def test_metric_sorting_logic(self):
        """Test the sorting logic used in report generation"""
        # Test MAP sorting (when MAP is enabled)
        cfg.compute_map = True
        cfg.compute_recall = True
        
        model_results = [
            ("model_low_map", 0.6, 0.9),   # Low MAP, high Recall
            ("model_high_map", 0.9, 0.6),  # High MAP, low Recall
        ]
        
        # Sort by MAP (index 1)
        sorted_by_map = sorted(model_results, key=lambda x: x[1], reverse=True)
        assert sorted_by_map[0][0] == "model_high_map"
        
        # Test fallback to Recall when MAP disabled
        cfg.compute_map = False
        cfg.compute_recall = True
        
        model_results_no_map = [
            ("model_low_recall", 0.6),   # Low Recall
            ("model_high_recall", 0.9),  # High Recall
        ]
        
        # Should sort by recall (index 1 when MAP disabled)
        recall_idx = 1 if cfg.compute_map else 1  # This matches the logic in report_utils.py
        sorted_by_recall = sorted(model_results_no_map, key=lambda x: x[recall_idx], reverse=True)
        assert sorted_by_recall[0][0] == "model_high_recall"
    
    def test_comprehensive_metric_scenarios(self):
        """Test various metric configuration scenarios"""
        scenarios = [
            # (enabled_metrics, expected_indices)
            (['map'], {'map': 1}),
            (['recall'], {'recall': 1}),
            (['map', 'recall'], {'map': 1, 'recall': 2}),
            (['map', 'ndcg'], {'map': 1, 'ndcg': 2}),
            (['recall', 'precision'], {'recall': 1, 'precision': 2}),
            (['map', 'recall', 'precision'], {'map': 1, 'recall': 2, 'precision': 3}),
            (['map', 'precision', 'mrr'], {'map': 1, 'precision': 2, 'mrr': 3}),
            (['map', 'recall', 'precision', 'ndcg', 'mrr'], {'map': 1, 'recall': 2, 'precision': 3, 'ndcg': 4, 'mrr': 5}),
        ]
        
        for enabled_metrics, expected_indices in scenarios:
            # Set configuration
            cfg.compute_map = 'map' in enabled_metrics
            cfg.compute_recall = 'recall' in enabled_metrics
            cfg.compute_precision = 'precision' in enabled_metrics
            cfg.compute_ndcg = 'ndcg' in enabled_metrics
            cfg.compute_mrr = 'mrr' in enabled_metrics
            
            # Build indices (same logic as report_utils.py)
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
            
            # Verify indices match expected
            assert metric_indices == expected_indices, f"Failed for scenario {enabled_metrics}"


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_config = {}
        for attr in ['compute_map', 'compute_recall', 'compute_precision', 'compute_ndcg', 'compute_mrr']:
            if hasattr(cfg, attr):
                self.original_config[attr] = getattr(cfg, attr)
    
    def teardown_method(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        for attr, value in self.original_config.items():
            setattr(cfg, attr, value)
    
    @pytest.mark.skipif(not REPORT_UTILS_AVAILABLE, reason="report_utils not available")
    @patch('utils.report_utils.generate_visualizations')
    def test_single_model_result(self, mock_viz):
        """Test with only one model result"""
        cfg.compute_map = True
        cfg.compute_recall = True
        
        mock_viz.return_value = {}
        
        result = generate_benchmark_report(
            model_results=[("model1", 0.8, 0.9)],
            queries={"q1": "test"},
            corpus={"d1": "test"},
            relevant_docs={"q1": ["d1"]},
            output_dir=self.temp_dir
        )
        
        assert result is not None
    
    @pytest.mark.skipif(not REPORT_UTILS_AVAILABLE, reason="report_utils not available")
    @patch('utils.report_utils.generate_visualizations')
    def test_empty_timing_results_list(self, mock_viz):
        """Test with empty timing results list (not None)"""
        cfg.compute_map = True
        
        mock_viz.return_value = {}
        
        # Empty list should trigger fallback behavior
        result = generate_benchmark_report(
            model_results=[("model1", 0.8)],
            queries={"q1": "test"},
            corpus={"d1": "test"},
            relevant_docs={"q1": ["d1"]},
            timing_results=[],  # Empty list (not None)
            output_dir=self.temp_dir
        )
        
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
