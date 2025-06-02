#!/usr/bin/env python
import subprocess
import sys
import os

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

def test(args=""):
    """Run tests with optional arguments"""
    run_command(f"pytest {args}", "Running tests")

def clean():
    """Clean up cached files"""
    patterns = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        ".pytest_cache",
        "**/.coverage"
    ]
    for pattern in patterns:
        files = subprocess.run(f'dir /s /b {pattern}', shell=True, capture_output=True, text=True)
        if files.stdout:
            for file in files.stdout.splitlines():
                if os.path.exists(file):
                    if os.path.isfile(file):
                        os.remove(file)
                    else:
                        os.rmdir(file)

def help():
    """Show this help message"""
    print("\nAvailable commands:")
    print("  python make.py format    Format code using black and isort")
    print("  python make.py test      Run all tests")
    print("  python make.py clean     Clean up cached files")
    print("  python make.py help      Show this help message")
    print("\nTest options:")
    print("  python make.py test -v                     Verbose output")
    print("  python make.py test -m integration         Run integration tests only")
    print("  python make.py test -m 'not integration'   Run unit tests only")
    print("  python make.py test tests/test_llm.py     Run specific test file")

if __name__ == "__main__":
    commands = {
        "format": format,
        "test": test,
        "clean": clean,
        "help": help
    }

    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        help()
        sys.exit(1)

    command = commands[sys.argv[1]]
    args = " ".join(sys.argv[2:])
    command(args) if command != help else command()