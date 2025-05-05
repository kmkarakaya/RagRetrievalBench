from utils.document_loader import load_document

# Use pathlib.Path
file_path = "C:/Users/murat.karakaya/CODES/RagRetrievalBench/utils/pdfs/Proje Önerisi.pdf"
doc = load_document(file_path)  # Convert Path object to string when calling load_document
print(doc)

# split the document into chunks
from utils.text_spitter import split_text

chunks = split_text(doc, chunk_size=1000, chunk_overlap=200)
print("Number of chunks:", len(chunks))
print("First chunk:\n", chunks[0])
print("Second chunk:\n", chunks[1])
print("Third chunk:\n", chunks[2])