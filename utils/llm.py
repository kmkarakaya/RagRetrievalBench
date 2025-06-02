from google import genai
from google.genai import types
import os 

def initialize_genai_client():
    """
    Initializes the Google GenAI client with the provided API key.
    Checks for API key in environment variables or .env file.
    
    Returns:
        genai.Client: An instance of the GenAI client.
    
    Raises:
        ValueError: If GEMINI_API_KEY is not found in environment variables or .env file.
    """
    import os.path
    from dotenv import load_dotenv

    # Check if .env file exists
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        print("Warning: .env file not found at", env_path)
    
    # Get API key from environment variables
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found. Please either:\n"
            "1. Create a .env file in the project root with GEMINI_API_KEY=your_key or\n"
            "2. Set GEMINI_API_KEY as an environment variable"
        )
    
    return genai.Client(api_key=api_key)

# Initialize the client once at module level
_client = None

def get_client():
    """
    Get or initialize the Gemini client.
    """
    global _client
    if _client is None:
        _client = initialize_genai_client()
    return _client

def generate_content(prompt: str, max_output_tokens: int = 500, temperature: float = 0.1) -> str:
    """
    Generate content using the Gemini API.
    
    Args:
        prompt (str): The input prompt for content generation
        max_output_tokens (int, optional): Maximum number of tokens in output. Defaults to 500.
        temperature (float, optional): Sampling temperature. Defaults to 0.1.
    
    Returns:
        str: The generated content text
    """
    client = get_client()
    response = client.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=max_output_tokens,
            temperature=temperature
        )
    )
    return response.text

# Example usage
if __name__ == "__main__":    
   try:
        prompt = "What is the capital of France?"
        generated_content = generate_content(prompt)
        print("Generated Content:", generated_content)
   except ValueError as e:
        print("Error:", e)
