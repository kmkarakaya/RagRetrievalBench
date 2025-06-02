import pytest
from utils.llm import initialize_genai_client, generate_content, get_client
import os
from unittest.mock import patch, MagicMock
from google import genai
from google.genai import types

def test_initialize_genai_client_no_key():
    # Mock os.environ and dotenv.load_dotenv to ensure no key is present
    with patch.dict(os.environ, clear=True), \
         patch('dotenv.load_dotenv', return_value=None):
        with pytest.raises(ValueError, match="GEMINI_API_KEY not found"):
            initialize_genai_client()

def test_initialize_genai_client_with_env():
    test_key = "test_api_key"
    with patch.dict(os.environ, {"GEMINI_API_KEY": test_key}), \
         patch('google.genai.Client') as mock_client:
        initialize_genai_client()
        mock_client.assert_called_once_with(api_key=test_key)

@pytest.mark.integration
def test_generate_content():
    # Skip if no API key available
    if "GEMINI_API_KEY" not in os.environ:
        pytest.skip("GEMINI_API_KEY not found in environment")
    
    response = generate_content("Hello world", max_output_tokens=10)
    assert isinstance(response, str)
    assert len(response) > 0

def test_generate_content_params():
    test_key = "test_api_key"
    test_response = "Test response"
    
    # Create a mock response
    mock_response = MagicMock()
    mock_response.text = test_response
    
    # Create a mock client
    mock_client = MagicMock()
    mock_client.generate_content.return_value = mock_response
    
    with patch.dict(os.environ, {"GEMINI_API_KEY": test_key}), \
         patch('google.genai.Client', return_value=mock_client), \
         patch('utils.llm._client', None):  # Reset the cached client
        
        response = generate_content(
            "Test prompt",
            max_output_tokens=100,
            temperature=0.5
        )
        
        assert response == test_response
        mock_client.generate_content.assert_called_once_with(
            "Test prompt",
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=100,
                temperature=0.5
            )
        )