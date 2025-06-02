from utils.document_loader import load_document
from utils.text_spitter import split_text
from utils.chromadb_utils import create_chroma_collection, list_collections, get_random_chunks
import chromadb

# Use pathlib.Path
file_path = "C:/Users/murat.karakaya/CODES/RagRetrievalBench/utils/pdfs/Proje Önerisi.pdf"
doc = load_document(file_path)  # Convert Path object to string when calling load_document

embedding_models = ["all-MiniLM-L6-v2",
                    "distiluse-base-multilingual-cased-v1"
]

# split the document into chunks
chunks = split_text(doc, chunk_size=1000, chunk_overlap=200)
print("Number of chunks:", len(chunks))

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="utils/chromadb_collections")

# Create or retrieve a ChromaDB collection and add the chunks to it
for model in embedding_models:
    print(f"Creating collection for model: {model}")
    # Create or retrieve the collection
    collection = create_chroma_collection("test_collection", 
                         model, 
                         [chunks], 
                         from_scratch=True)

collections = list_collections(client)
print("Collections in ChromaDB:") 
for collection in collections:
    print(collection.name)  # Print each collection name

# Get random chunks from each collection
print("\nRetrieving random chunks from collections:")
for collection in collections:
    print(f"\nRandom chunks from {collection.name}:")
    random_chunks = get_random_chunks(client, collection.name, n_chunks=2)
    for i, chunk in enumerate(random_chunks, 1):
        print(f"\nChunk {i}:")
        print(chunk)
