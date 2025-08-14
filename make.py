#!/usr/bin/env python
import subprocess
import sys
import os
import shutil
from pathlib import Path

def run_command(command, description):
    print(f"\n=== {description} ===")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Error: {description} failed")
        sys.exit(result.returncode)

def format():
    """Format code using black and isort"""
    run_command("black .", "Formatting code with black")
    run_command("isort .", "Sorting imports with isort")

def lint():
    """Run code quality checks"""
    run_command("black --check .", "Checking code formatting")
    run_command("isort --check-only .", "Checking import sorting")

def test(args=""):
    """Run tests with optional arguments"""
    run_command(f"pytest {args}", "Running tests")

def test_cov(args=""):
    """Run tests with coverage report"""
    run_command(f"pytest --cov=utils --cov-report=html --cov-report=term {args}", "Running tests with coverage")

def clean():
    """Clean up cached files, report outputs, and ChromaDB collections"""
    patterns = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        ".pytest_cache",
        "htmlcov",
        ".coverage",
        "**/.coverage*"
    ]
    
    # Clean pattern-based files and directories
    for pattern in patterns:
        # Use pathlib for cross-platform compatibility
        for path in Path('.').glob(pattern):
            if path.exists():
                if path.is_file():
                    print(f"Removing file: {path}")
                    path.unlink()
                elif path.is_dir():
                    print(f"Removing directory: {path}")
                    shutil.rmtree(path)
    
    # Clean reports folder contents
    reports_dir = Path('reports')
    if reports_dir.exists() and reports_dir.is_dir():
        print(f"\nCleaning reports directory: {reports_dir}")
        for item in reports_dir.iterdir():
            if item.is_file():
                print(f"Removing report file: {item}")
                item.unlink()
            elif item.is_dir():
                print(f"Removing report subdirectory: {item}")
                shutil.rmtree(item)
        print("Reports directory cleaned (kept the directory itself)")
    else:
        print("No reports directory found to clean")
    
    # Clean ChromaDB collections folder contents
    chromadb_dir = Path('utils/chromadb_collections')
    if chromadb_dir.exists() and chromadb_dir.is_dir():
        print(f"\nCleaning ChromaDB collections directory: {chromadb_dir}")
        for item in chromadb_dir.iterdir():
            if item.is_file():
                print(f"Removing ChromaDB file: {item}")
                item.unlink()
            elif item.is_dir():
                print(f"Removing ChromaDB collection: {item}")
                shutil.rmtree(item)
        print("ChromaDB collections directory cleaned (kept the directory itself)")
    else:
        print("No ChromaDB collections directory found to clean")
    
    print("\n✅ Cleanup complete!")

def benchmark():
    """Run the benchmark pipeline"""
    run_command("python simple_rag_benchmark_pipeline.py --help", "Showing benchmark options")

def help():
    """Show this help message"""
    print("\nAvailable commands:")
    print("  python make.py format       Format code using black and isort")
    print("  python make.py lint         Check code quality without modifying")
    print("  python make.py test         Run all tests")
    print("  python make.py test-cov     Run tests with coverage report")
    print("  python make.py clean        Clean up cached files")
    print("  python make.py benchmark    Show benchmark pipeline options")
    print("  python make.py help         Show this help message")
    print("\nTest options:")
    print("  python make.py test -v                     Verbose output")
    print("  python make.py test -m integration         Run integration tests only")
    print("  python make.py test -m 'not integration'   Run unit tests only")
    print("  python make.py test tests/test_llm.py     Run specific test file")
    print("\nCoverage options:")
    print("  python make.py test-cov                    Generate HTML coverage report")
    print("  python make.py test-cov -v                Coverage with verbose output")

if __name__ == "__main__":
    commands = {
        "format": format,
        "lint": lint,
        "test": test,
        "test-cov": test_cov,
        "clean": clean,
        "benchmark": benchmark,
        "help": help
    }

    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        help()
        sys.exit(1)

    command = commands[sys.argv[1]]
    args = " ".join(sys.argv[2:])
    
    if command in [help]:
        command()
    else:
        command(args) if args else command()