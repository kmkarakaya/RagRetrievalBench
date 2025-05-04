import os
from pathlib import Path
from marker.convert import convert_to_markdown
from sentence_transformers import SentenceTransformer

class DocumentLoader:
    def __init__(self, pdf_folder="./pdfs", model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.pdf_folder = Path(pdf_folder)
        self.encoder = SentenceTransformer(model_name)
        
    def load_and_chunk_pdfs(self):
        """
        Load PDFs from the specified folder, convert them to text, and chunk them
        Returns a list of tuples (chunk_text, embedding)
        """
        documents = []
        
        # Process each PDF in the folder
        for pdf_file in self.pdf_folder.glob("*.pdf"):
            try:
                # Convert PDF to markdown using marker
                markdown_text = convert_to_markdown(str(pdf_file))
                
                # Split into chunks at sentence boundaries using simple heuristics
                # This uses the built-in string splitting which is sufficient for most cases
                chunks = [s.strip() for s in markdown_text.split('.') if s.strip()]
                
                # Create embeddings for all chunks at once (more efficient)
                embeddings = self.encoder.encode(chunks)
                
                # Pair each chunk with its embedding
                doc_chunks = list(zip(chunks, embeddings))
                documents.extend(doc_chunks)
                
            except Exception as e:
                print(f"Error processing {pdf_file}: {str(e)}")
        
        return documents

    def get_chunk_embedding(self, text):
        """
        Get embedding for a single chunk of text
        """
        return self.encoder.encode(text)