import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import os

def initialize_genai_client():
    """
    Initializes the Google GenAI configuration with the provided API key.
    Checks for API key in environment variables or .env file.
    
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
    
    # Configure the Gemini API
    genai.configure(api_key=api_key)

def list_available_models():
    """
    Fetches the list of available models and their supported methods.
    
    Returns:
        list: A list of model names.
    """
    initialize_genai_client()
    models = genai.list_models()
    return [model.name for model in models]

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
    initialize_genai_client()
    
    # Use the gemini-2.0-flash model
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=GenerationConfig(
            max_output_tokens=max_output_tokens,
            temperature=temperature
        )
    )
    
    # Generate the response
    response = model.generate_content(prompt)
    
    # Check if the response generation was blocked
    if response.prompt_feedback.block_reason:
        raise ValueError(f"Response was blocked: {response.prompt_feedback.block_reason}")
    
    return response.text

# Example usage
if __name__ == "__main__":    
    try:
        prompt = "What is the capital of France?"
        generated_content = generate_content(prompt)
        print("Generated Content:", generated_content)
    except ValueError as e:
        print("Error:", e)
