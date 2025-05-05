import os
from pathlib import Path
import pymupdf # imports the pymupdf library
import re

def load_document(file_path: str) -> str:
    """
    Load a document from the given file path.
    
    Args:
        file_path (str): The path to the document file.
        
    Returns:
        str: The text content of the document.
    """
    # Convert the file path to a Path object
    file_path = Path(file_path)
    
    # Check if the file exists
    if not file_path.exists():
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    # Get the file extension
    ext = file_path.suffix
    
    # Load the document based on its extension
    if ext.lower() == '.pdf':
        return load_pdf(str(file_path))  # Convert Path object back to string for load_pdf
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
def load_pdf(file_path: str) -> str:
    """
    Load a PDF document and extract its text content with improved spacing handling.
    
    Args:
        file_path (str): The path to the PDF file.
        
    Returns:
        str: The cleaned text content of the PDF document.
    """
    # Open the PDF file using pymupdf
    doc = pymupdf.open(file_path)
    
    # Initialize empty list to store text from each page
    pages_text = []
    
    # Extract text from each page with specific options
    for page in doc:
        # Get text with options to preserve natural reading order
        text = page.get_text("text")
        
        # Clean the text
        # Replace various types of whitespace with single space
        text = re.sub(r'[\n\r\t]+', ' ', text)
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        # Remove spaces before punctuation
        text = re.sub(r'\s+([.,!?])', r'\1', text)
        # Strip whitespace
        text = text.strip()
        
        if text:  # Only add non-empty pages
            pages_text.append(text)
    
    # Join all pages with a single space
    full_text = ' '.join(pages_text)
    
    # Final cleaning of the complete text
    full_text = re.sub(r' +', ' ', full_text)
    full_text = full_text.strip()
    
    return full_text

