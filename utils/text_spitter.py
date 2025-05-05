from langchain_text_splitters import RecursiveCharacterTextSplitter
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