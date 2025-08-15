"""
Test script to reproduce and verify the metric indexing fix
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import benchmark_config as cfg
from unittest.mock import patch, Mock
import tempfile

# Mock matplotlib to avoid dependency issues
sys.modules['matplotlib'] = Mock()
sys.modules['matplotlib.pyplot'] = Mock()

from utils.report_utils import generate_benchmark_report

def test_recall_only_scenario():
    """Test the exact scenario that was failing"""
    print("Testing recall-only scenario...")
    
    # Save original config
    original_config = {}
    for attr in ['compute_map', 'compute_recall', 'compute_precision', 'compute_ndcg', 'compute_mrr']:
        if hasattr(cfg, attr):
            original_config[attr] = getattr(cfg, attr)
    
    try:
        # Set to recall only (like the failing test)
        cfg.compute_map = False
        cfg.compute_recall = True
        cfg.compute_precision = False
        cfg.compute_ndcg = False
        cfg.compute_mrr = False
        
        # Model results with only recall (single metric after model name)
        model_results = [
            ("model1", 0.9),  # Only recall value
            ("model2", 0.8),
        ]
        
        queries = {"q1": "test"}
        corpus = {"d1": "test"}
        relevant_docs = {"q1": ["d1"]}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('utils.report_utils.generate_visualizations') as mock_viz:
                mock_viz.return_value = {}
                
                try:
                    result = generate_benchmark_report(
                        model_results=model_results,
                        queries=queries,
                        corpus=corpus,
                        relevant_docs=relevant_docs,
                        output_dir=temp_dir
                    )
                    print("✓ Report generation succeeded")
                    
                    # Check the generated report content
                    report_files = [f for f in os.listdir(temp_dir) if f.endswith('.md')]
                    if report_files:
                        with open(os.path.join(temp_dir, report_files[0]), 'r') as f:
                            content = f.read()
                        
                        # Verify the problems from test failures
                        if "MAP@10" in content:
                            print("❌ ISSUE: Report still contains MAP@10 references when MAP is disabled")
                            # Find and print the lines containing MAP@10
                            lines_with_map = [line.strip() for line in content.split('\n') if 'MAP@10' in line]
                            for line in lines_with_map:
                                print(f"   Found: {line}")
                        else:
                            print("✓ No MAP@10 references found when MAP is disabled")
                            
                        if "Recall@10: **0.9000**" in content:
                            print("✓ Recall@10 correctly displayed")
                        else:
                            print("❌ Recall@10 not found in report")
                    
                except Exception as e:
                    print(f"❌ Report generation failed: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
                    
    finally:
        # Restore config
        for attr, value in original_config.items():
            setattr(cfg, attr, value)
    
    return True

def test_single_metric_scenario():
    """Test with insufficient metrics for model results tuple"""
    print("\nTesting single metric scenario...")
    
    original_config = {}
    for attr in ['compute_map', 'compute_recall', 'compute_precision', 'compute_ndcg', 'compute_mrr']:
        if hasattr(cfg, attr):
            original_config[attr] = getattr(cfg, attr)
    
    try:
        # Enable MAP and Recall but provide insufficient data
        cfg.compute_map = True
        cfg.compute_recall = True
        cfg.compute_precision = False
        cfg.compute_ndcg = False
        cfg.compute_mrr = False
        
        # Model results with insufficient metrics (IndexError scenario)
        model_results = [
            ("model1", 0.8),  # Only one metric value, but two are expected
        ]
        
        queries = {"q1": "test"}
        corpus = {"d1": "test"}
        relevant_docs = {"q1": ["d1"]}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('utils.report_utils.generate_visualizations') as mock_viz:
                mock_viz.return_value = {}
                
                try:
                    result = generate_benchmark_report(
                        model_results=model_results,
                        queries=queries,
                        corpus=corpus,
                        relevant_docs=relevant_docs,
                        output_dir=temp_dir
                    )
                    print("❌ This should have failed with IndexError but didn't")
                    
                except IndexError as e:
                    print(f"✓ Correctly caught IndexError: {e}")
                    print("   This is the issue we need to fix in report_utils.py")
                    return True
                except Exception as e:
                    print(f"❌ Unexpected error: {e}")
                    
    finally:
        # Restore config
        for attr, value in original_config.items():
            setattr(cfg, attr, value)
    
    return False

if __name__ == "__main__":
    print("=== Testing Report Utils Metric Indexing Issues ===\n")
    
    test1_passed = test_recall_only_scenario()
    test2_passed = test_single_metric_scenario()
    
    print(f"\n=== Summary ===")
    print(f"Recall-only test: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"IndexError test: {'EXPECTED BEHAVIOR' if test2_passed else 'UNEXPECTED'}")
    
    if not test1_passed or not test2_passed:
        print("\n❌ Issues found that need to be fixed in report_utils.py")
        sys.exit(1)
    else:
        print("\n✓ All tests show expected behavior")
