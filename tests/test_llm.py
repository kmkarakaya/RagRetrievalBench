import pytest
from utils.llm import initialize_genai_client, generate_content
import os
from unittest.mock import patch, MagicMock
import google.generativeai as genai

def test_initialize_genai_client_no_key():
    # Mock os.environ and dotenv.load_dotenv to ensure no key is present
    with patch.dict(os.environ, clear=True), \
         patch('dotenv.load_dotenv', return_value=None):
        with pytest.raises(ValueError, match="GEMINI_API_KEY not found"):
            initialize_genai_client()

def test_initialize_genai_client_with_env():
    test_key = "test_api_key"
    with patch.dict(os.environ, {"GEMINI_API_KEY": test_key}), \
         patch('google.generativeai.configure') as mock_configure:
        initialize_genai_client()
        mock_configure.assert_called_once_with(api_key=test_key)

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
    mock_response.prompt_feedback = MagicMock()
    mock_response.prompt_feedback.block_reason = None
    
    # Create a mock model
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    
    with patch.dict(os.environ, {"GEMINI_API_KEY": test_key}), \
         patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel', return_value=mock_model):
        
        response = generate_content(
            "Test prompt",
            max_output_tokens=100,
            temperature=0.5
        )
        
        assert response == test_response
        mock_configure.assert_called_once_with(api_key=test_key)
        mock_model.generate_content.assert_called_once_with("Test prompt")

def test_generate_content_blocked():
    test_key = "test_api_key"
    
    # Create a mock response with blocked content
    mock_response = MagicMock()
    mock_response.prompt_feedback = MagicMock()
    mock_response.prompt_feedback.block_reason = "SAFETY"
    
    # Create a mock model
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    
    with patch.dict(os.environ, {"GEMINI_API_KEY": test_key}), \
         patch('google.generativeai.configure'), \
         patch('google.generativeai.GenerativeModel', return_value=mock_model):
        
        with pytest.raises(ValueError, match="Response was blocked: SAFETY"):
            generate_content("Test prompt")