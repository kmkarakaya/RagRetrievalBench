import pytest
from utils.llm import initialize_genai_client, generate_content
import os
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

def test_api_key_not_found_anywhere():
    """Test behavior when API key is not found in either .env file or system environment"""
    with patch.dict(os.environ, clear=True), \
         patch('dotenv.load_dotenv', return_value=None), \
         patch('os.path.exists', return_value=False):  # No .env file
        with pytest.raises(ValueError, match="GEMINI_API_KEY not found"):
            initialize_genai_client()

def test_api_key_found_in_env_file():
    """Test client initialization when API key exists in .env file but not in system environment"""
    test_key = "test_api_key_from_env_file"
    mock_client = MagicMock()
    
    def mock_load_dotenv(*args, **kwargs):
        os.environ['GEMINI_API_KEY'] = test_key
        return True
    
    with patch.dict(os.environ, clear=True), \
         patch('dotenv.load_dotenv', side_effect=mock_load_dotenv), \
         patch('os.path.exists', return_value=True), \
         patch('google.genai.Client', return_value=mock_client) as mock_genai_client:
        result = initialize_genai_client()
        mock_genai_client.assert_called_once_with(api_key=test_key)
        assert result == mock_client
        # Verify it came from .env file
        assert os.environ.get('GEMINI_API_KEY') == test_key

def test_api_key_found_in_system_env():
    """Test client initialization when API key exists in system environment but not in .env file"""
    test_key = "test_api_key_from_system"
    mock_client = MagicMock()
    
    with patch.dict(os.environ, {"GEMINI_API_KEY": test_key}, clear=True), \
         patch('dotenv.load_dotenv', return_value=None), \
         patch('os.path.exists', return_value=False), \
         patch('google.genai.Client', return_value=mock_client) as mock_genai_client:
        result = initialize_genai_client()
        mock_genai_client.assert_called_once_with(api_key=test_key)
        assert result == mock_client

def test_api_key_env_file_priority_over_system():
    """Test that API key from .env file is used even when a different key exists in system environment"""
    system_key = "system_api_key"
    env_file_key = "env_file_api_key"
    mock_client = MagicMock()
    
    def mock_load_dotenv(*args, **kwargs):
        os.environ['GEMINI_API_KEY'] = env_file_key
        return True
    
    with patch.dict(os.environ, {"GEMINI_API_KEY": system_key}), \
         patch('dotenv.load_dotenv', side_effect=mock_load_dotenv), \
         patch('os.path.exists', return_value=True), \
         patch('google.genai.Client', return_value=mock_client) as mock_genai_client:
        result = initialize_genai_client()
        # Should use the key from .env file
        mock_genai_client.assert_called_once_with(api_key=env_file_key)
        assert result == mock_client

@pytest.mark.integration
def test_integration_generate_content_with_env_file_key():
    """Integration test: Generate content using API key from .env file, ensuring system env is not used"""
    # Clear any existing environment variable
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
    
    # Force reload of .env file
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if not os.path.exists(env_path):
        pytest.skip(".env file not found")
    
    # Load .env file fresh
    load_dotenv(env_path, override=True)
    
    try:
        response = generate_content("You are a helpful assistant.", "Hello world")
        assert isinstance(response, str)
        assert len(response) > 0
        assert not response.startswith("Error")
    except Exception as e:
        pytest.fail(f"API call failed with .env file key: {str(e)}")

@pytest.mark.integration
def test_integration_generate_content_with_system_env_key():
    """Integration test: Generate content using API key from system environment, when no .env file exists"""
    import subprocess
    
    # Check if the key exists in system environment using a separate Python process
    result = subprocess.run(
        ['python', '-c', "import os; print('GEMINI_API_KEY' in os.environ)"],
        capture_output=True,
        text=True
    )
    
    has_system_key = result.stdout.strip() == 'True'
    if not has_system_key:
        pytest.skip("No GEMINI_API_KEY in system environment (verified via subprocess)")
    
    # For debugging
    print(f"\nSystem environment check:")
    print(f"Direct check: {'GEMINI_API_KEY' in os.environ}")
    print(f"Subprocess check: {has_system_key}")
    
    # Get the key value
    key_value = os.environ.get('GEMINI_API_KEY')
    print(f"Key exists: {bool(key_value)}")
    
    # Temporarily clear other environment sources
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        os.rename(env_path, f"{env_path}.backup")
    
    try:
        response = generate_content("You are a helpful assistant.", "Hello world")
        assert isinstance(response, str)
        assert len(response) > 0
        assert not response.startswith("Error")
    except Exception as e:
        pytest.fail(f"API call failed with system environment key: {str(e)}")
    finally:
        if os.path.exists(f"{env_path}.backup"):
            os.rename(f"{env_path}.backup", env_path)

def test_api_error_with_invalid_key():
    """Test error handling when trying to generate content with an invalid API key"""
    test_key = "invalid_api_key"
    
    with patch.dict(os.environ, {"GEMINI_API_KEY": test_key}), \
         patch('dotenv.load_dotenv', return_value=None), \
         patch('os.path.exists', return_value=True), \
         patch('google.genai.Client', side_effect=Exception("Invalid API key")):
        
        with pytest.raises(ValueError, match="API call failed"):
            generate_content("System prompt", "User prompt")

def test_generate_content_successful_response():
    """Test content generation succeeds with valid API response (using mocked client)"""
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
        
        response = generate_content("System instruction", "User prompt")
        assert response == test_response
        mock_client.models.generate_content.assert_called_once()