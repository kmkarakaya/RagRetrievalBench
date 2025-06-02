from utils.document_loader import load_document
from utils.text_spitter import split_text
from utils.chromadb_utils import create_chroma_collection, list_collections, get_random_chunks
import chromadb
import os

# Use OS path join for better cross-platform compatibility
file_path = os.path.join("utils", "pdfs", "SamplePdf.pdf")
doc = load_document(file_path)

embedding_models = ["all-MiniLM-L6-v2",
                   "distiluse-base-multilingual-cased-v1"
]

# split the document into chunks
chunks = split_text(doc, chunk_size=1000, chunk_overlap=200)
print("Number of chunks:", len(chunks))

# Initialize ChromaDB client
client = chromadb.PersistentClient(path=os.path.join("utils", "chromadb_collections"))

# Create or retrieve a ChromaDB collection and add the chunks to it
for i, model in enumerate(embedding_models):
    collection_name = f"test_collection_{i+1}"  # Unique collection name for each model
    print(f"Creating collection '{collection_name}' with model: {model}")
    collection = create_chroma_collection(
        collection_name=collection_name,
        embedding_model=model,
        sentences=[chunks],
        from_scratch=True
    )

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
