import pytest
from utils.llm import initialize_genai_client, generate_content
import os
from unittest.mock import patch, MagicMock
# Note: Your implementation uses google.genai, not google.generativeai

def test_initialize_genai_client_no_key():
    # Mock os.environ to ensure no key is present
    with patch.dict(os.environ, clear=True), \
         patch('dotenv.load_dotenv', return_value=None), \
         patch('os.path.exists', return_value=True):  # Pretend .env exists
        with pytest.raises(ValueError, match="GEMINI_API_KEY not found"):
            initialize_genai_client()

def test_initialize_genai_client_with_env():
    test_key = "test_api_key"
    mock_client = MagicMock()
    
    with patch.dict(os.environ, {"GEMINI_API_KEY": test_key}), \
         patch('dotenv.load_dotenv', return_value=None), \
         patch('os.path.exists', return_value=True), \
         patch('google.genai.Client', return_value=mock_client) as mock_genai_client:
        result = initialize_genai_client()
        mock_genai_client.assert_called_once_with(api_key=test_key)
        assert result == mock_client

@pytest.mark.integration
def test_generate_content():
    # Skip if no API key available
    if "GEMINI_API_KEY" not in os.environ:
        pytest.skip("GEMINI_API_KEY not found in environment")
    
    # Your function signature is: generate_content(system_prompt, user_prompt)
    response = generate_content("You are a helpful assistant.", "Hello world")
    assert isinstance(response, str)
    assert len(response) > 0

def test_generate_content_params():
    test_key = "test_api_key"
    test_response = "Test response"
    
    # Create mocks for the full chain: client -> models -> generate_content
    mock_response = MagicMock()
    mock_response.text = test_response
    
    mock_models = MagicMock()
    mock_models.generate_content.return_value = mock_response
    
    mock_client = MagicMock()
    mock_client.models = mock_models
    
    with patch.dict(os.environ, {"GEMINI_API_KEY": test_key}), \
         patch('dotenv.load_dotenv', return_value=None), \
         patch('os.path.exists', return_value=True), \
         patch('google.genai.Client', return_value=mock_client):
        
        response = generate_content("System prompt", "User prompt")
        
        assert response == test_response
        # Verify the client was created
        assert mock_client.models.generate_content.called

def test_generate_content_basic():
    """Basic test for generate_content with proper mocking"""
    test_key = "test_api_key" 
    test_response = "Mocked response"
    
    # Create mocks for the full chain
    mock_response = MagicMock()
    mock_response.text = test_response
    
    mock_models = MagicMock()
    mock_models.generate_content.return_value = mock_response
    
    mock_client = MagicMock()
    mock_client.models = mock_models
    
    with patch.dict(os.environ, {"GEMINI_API_KEY": test_key}), \
         patch('dotenv.load_dotenv', return_value=None), \
         patch('os.path.exists', return_value=True), \
         patch('google.genai.Client', return_value=mock_client):
        
        # Test with correct function signature
        response = generate_content("System instruction", "User prompt")
        
        assert response == test_response