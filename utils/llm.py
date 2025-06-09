from google import genai
from google.genai import types

import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import benchmark_config as cfg


def initialize_genai_client():
    import os.path
    from dotenv import load_dotenv
    # Check if .env file exists
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        print("Warning: .env file not found at", env_path)
        exit(1)
    
    # Get API key from environment variables
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("Error: No API key found in environment variables")
            exit(1)
    
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found. Please either:\n"
            "1. Create a .env file in the project root with GEMINI_API_KEY=your_key or\n"
            "2. Set GEMINI_API_KEY as an environment variable"
        )
    
    # Configure the Gemini API
    
    client = genai.Client(api_key=api_key)
    if not client:
        raise ValueError("Failed to initialize Gemini API client")

    return client


def generate_content(system_prompt, user_prompt) -> str:
    """
    Generate content using the Gemini API.

    """
    client = initialize_genai_client()
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=cfg.temperature
    )

    # Use the model
    response = client.models.generate_content(
        model=cfg.llm_model,
        config=config,
        contents=user_prompt
    )
    
 
    return response.text

# Example usage
if __name__ == "__main__":    
    try:
        prompt = "The capital of France is Paris"
        generated_content = generate_content(cfg.generate_query_system_instruction,prompt)
        print("Generated Content:", generated_content)
    except ValueError as e:
        print("Error:", e)
