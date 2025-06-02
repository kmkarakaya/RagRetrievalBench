# Setup Instructions

## Environment Setup

1. Create and activate a new conda environment:
```bash
conda create -n ragbenchmark python=3.10
conda activate ragbenchmark
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## API Key Configuration

1. Create a `.env` file in the project root directory
2. Add your Gemini API key:
```
GEMINI_API_KEY=your_key_here
```

## Verify Installation

1. Check if ChromaDB is working:
```python
from utils.chromadb_utils import create_chroma_collection
collection = create_chroma_collection("test", "all-MiniLM-L6-v2", [], from_scratch=True)
```

2. Test PDF loading:
```python
from utils.document_loader import load_document
# Replace with path to your PDF
doc = load_document("path/to/test.pdf")
```

3. Verify Gemini API connection:
```python
from utils.llm import generate_content
response = generate_content("Hello, world!")
print(response)
```

## Common Issues

1. If you get a ModuleNotFoundError, ensure you have activated the conda environment:
```bash
conda activate ragbenchmark
```

2. If ChromaDB fails to initialize, check if the chromadb_collections directory exists in utils/

3. If Gemini API calls fail, verify your API key in the .env file

## Development Setup

For development work, consider:

1. Setting up VS Code with Python extension
2. Installing development dependencies:
```bash
pip install pytest black isort
```

3. Configure git to ignore sensitive files:
```bash
echo ".env" >> .gitignore
echo "utils/chromadb_collections/" >> .gitignore
```
