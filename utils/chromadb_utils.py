import chromadb
from chromadb.utils import embedding_functions
import random

def create_chroma_collection(collection_name: str, 
                             embedding_model: str, 
                             sentences: list[list[str]], 
                             from_scratch: bool = True) -> chromadb.Collection:
    """
    Creates or retrieves a ChromaDB collection and adds sentence embeddings to it.
    Args:
        collection_name (str): Name of the collection to create or retrieve
        embedding_model (str): Name of the sentence transformer model to use for embeddings
        sentences (list[list[str]]): List of sentence pairs to add to collection. Each inner list contains 2 sentences.
        from_scratch (bool, optional): If True, deletes existing collection before creating new one. Defaults to True.
    Returns:
        chromadb.Collection: ChromaDB collection object containing the added sentences and embeddings
    Raises:
        Exception: If there is an error creating/retrieving the collection unrelated to collection existence
    Example:
        >>> sentences = [["Hello world", "Hi there"], ["Good morning", "Good evening"]]
        >>> collection = create_chroma_collection("my_collection", "all-MiniLM-L6-v2", sentences)
    """
    client = client = chromadb.PersistentClient(path="utils\chromadb_collections")
    collection_name = embedding_model  # Use the embedding model name as the collection name
    # Initialize the embedding function using the specified model
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=embedding_model)

    if (from_scratch):
        # Delete the collection if it exists
        try:
            client.delete_collection(name=collection_name)
            print(f"Existing Collection '{collection_name}' found & deleted successfully.")
        except Exception as e:
            print(f"Collection '{collection_name}' does not exist...")


    # Create a new chroma collection or get the existing one
    try:
        collection = client.create_collection(name=collection_name,
                                              embedding_function=embedding_function)
        print(f"Collection '{collection_name}' created successfully.")
        start_id=0
    except Exception as e: # Catch a broader exception and check the error message
        if "already exists" in str(e):
            collection = client.get_collection(name=collection_name,
                                              embedding_function=embedding_function)
            print(f"Collection '{collection_name}' already exists. Using existing collection.")
            start_id=collection.count() # Get the current count of documents in the collection
        else:
            raise e # Re-raise the exception if it's not related to collection existence

    if(sentences):
        # Add your sentences and embeddings to the collection
        sentences_to_add = []
        embeddings_to_add = []
        ids_to_add = [] # Create a list to store unique IDs for each document
        print("Starting adding new documents from start_id: ",start_id)
        for i, pair in enumerate(sentences):
            sentences_to_add.extend(pair)
            #print('sentences_to_add: ', sentences_to_add)
            ids_to_add.extend([str(i * 2 + j+start_id) for j in range(len(pair))]) # Generate unique IDs, e.g., "0", "1", "2", "3"...

        collection.add(
            documents=sentences_to_add,
            ids=ids_to_add # Add the 'ids' argument
        )

        end_id=collection.count()
        print(f"Added {end_id-start_id} documents to the collection.")
    return collection

def list_collections(client: chromadb.PersistentClient) -> list:
    """
    Lists all collections in the ChromaDB client.
    
    Args:
        client (chromadb.PersistentClient): The ChromaDB client instance.
        
    Returns:
        list: A list of collection names.
    """
    return client.list_collections()

def get_random_chunks(client: chromadb.PersistentClient, 
                     collection_name: str, 
                     n_chunks: int = 5) -> list:
    """
    Retrieves a random selection of chunks from the specified collection.
    
    Args:
        client (chromadb.PersistentClient): The ChromaDB client instance
        collection_name (str): Name of the collection to retrieve chunks from
        n_chunks (int, optional): Number of chunks to retrieve. Defaults to 5.
        
    Returns:
        list: A list of randomly selected chunks (documents)
        
    Raises:
        ValueError: If n_chunks is greater than the total number of documents in the collection
    """
    # Get the collection
    collection = client.get_collection(name=collection_name)
    
    # Get total number of documents in collection
    total_docs = collection.count()
    
    if n_chunks > total_docs:
        raise ValueError(f"Requested {n_chunks} chunks but collection only has {total_docs} documents")
    
    # Generate random indices
    random_indices = random.sample(range(total_docs), n_chunks)
    
    # Convert indices to string IDs (since we store IDs as strings)
    random_ids = [str(idx) for idx in random_indices]
    
    # Retrieve the random chunks
    result = collection.get(
        ids=random_ids,
        include=['documents']
    )
    
    return result['documents']
