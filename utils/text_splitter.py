from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import fitz  # PyMuPDF
from typing import List

def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list:
    """
    Split the text into smaller chunks for processing.
    
    Args:
        text (str): The text to be split.
        chunk_size (int): The size of each chunk.
        chunk_overlap (int): The overlap between chunks.
        
    Returns:
        list: A list of text chunks.
    """
    # Initialize the text splitter with specified chunk size and overlap
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    
    # Split the text into chunks
    chunks = text_splitter.split_text(text)
    
    return chunks

def split_pdfs_to_chunks(pdf_dir: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[object]:
    """
    Loads all PDFs from a directory, splits their text into chunks, and returns a list of chunk objects.
    Each chunk object has 'doc_id' and 'page_content'.
    
    Args:
        pdf_dir (str): Directory containing PDF files
        chunk_size (int): Size of each chunk
        chunk_overlap (int): Overlap between chunks
        
    Returns:
        List[object]: List of chunk objects with doc_id and page_content attributes
    """
    chunks = []
    print(f"Looking for PDFs in {pdf_dir}")
    
    if not os.path.exists(pdf_dir):
        print(f"Warning: Directory {pdf_dir} does not exist!")
        return chunks
        
    for filename in os.listdir(pdf_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, filename)
            print(f"Processing PDF: {filename}")
            
            try:
                doc = fitz.open(pdf_path)
                full_text = ""
                for page in doc:
                    full_text += page.get_text()
                doc.close()
                
                split_chunks = split_text(full_text, chunk_size, chunk_overlap)
                print(f"  Created {len(split_chunks)} chunks from {filename}")
                
                for idx, chunk in enumerate(split_chunks):
                    chunk_obj = type("Chunk", (), {})()
                    chunk_obj.doc_id = f"{os.path.splitext(filename)[0]}_chunk{idx+1}"
                    chunk_obj.page_content = chunk
                    chunks.append(chunk_obj)
            except Exception as e:
                print(f"  Error processing {filename}: {e}")
                
    print(f"Total chunks created: {len(chunks)}")
    return chunks