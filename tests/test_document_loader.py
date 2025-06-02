import pytest
from utils.document_loader import load_document, load_pdf
import os
from pathlib import Path

def test_load_document_with_invalid_path():
    with pytest.raises(FileNotFoundError):
        load_document("nonexistent.pdf")

def test_load_document_with_unsupported_extension(tmp_path):
    # Create a temporary text file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    
    with pytest.raises(ValueError, match="Unsupported file type"):
        load_document(str(test_file))

def test_load_pdf_text_cleaning():
    test_pdf_path = os.path.join("utils", "pdfs", "SamplePdf.pdf")
    
    if not os.path.exists(test_pdf_path):
        pytest.skip(f"Test PDF file not found at {test_pdf_path}")
    
    text = load_pdf(test_pdf_path)
    assert isinstance(text, str)
    assert len(text) > 0
    # No multiple spaces
    assert "  " not in text
    # No spaces before punctuation
    assert " ." not in text
    assert " ," not in text