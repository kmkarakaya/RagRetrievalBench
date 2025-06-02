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

client = initialize_genai_client()

def generate_content(prompt: str, max_output_tokens: int = 500, temperature: float = 0.1):
    """
    Generates content using the Google GenAI client.
    
    Args:
        prompt (str): The input prompt for content generation.
        max_output_tokens (int): Maximum number of tokens in the output.
        temperature (float): Sampling temperature for generation.
        
    Returns:
        str: The generated content.
    """
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt],
        config=types.GenerateContentConfig(
            max_output_tokens=max_output_tokens,
            temperature=temperature
        )
    )
    return response.text

# Example usage
if __name__ == "__main__":    
   try:
        prompt = "What is the capital of France?" # Example prompt    
        generated_content = generate_content(prompt)
        print("Generated Content:", generated_content)
   except ValueError as e:
        print("Error:", e)
