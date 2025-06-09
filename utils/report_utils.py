def convert_md_to_pdf(md_file_path, output_dir="reports"):
    """Convert markdown report to PDF using pandoc"""
    import subprocess
    import os
    
    # Get the base filename without extension
    base_name = os.path.splitext(os.path.basename(md_file_path))[0]
    
    # Since this utils file is in utils/ folder and reports/ is at root level,
    # we need to go up one directory from the md_file_path location
    if os.path.isabs(output_dir):
        # If output_dir is absolute path, use it directly
        pdf_file_path = os.path.join(output_dir, f"{base_name}.pdf")
    else:
        # If output_dir is relative, it's relative to the project root
        # Go up from utils/ to project root, then into reports/
        project_root = os.path.dirname(os.path.dirname(__file__))  # Go up two levels from utils/report_utils.py
        pdf_file_path = os.path.join(project_root, output_dir, f"{base_name}.pdf")
    
    try:
        # Try with basic pandoc options that work on most systems
        basic_cmd = [
            "pandoc", 
            md_file_path, 
            "-o", pdf_file_path,
            "--standalone"
        ]
        
        print(f"Converting {md_file_path} to PDF using pandoc...")
        result = subprocess.run(basic_cmd, check=True, capture_output=True, text=True)
        
        print(f"PDF report generated successfully: {pdf_file_path}")
        return pdf_file_path
        
    except FileNotFoundError:
        print("Error: Pandoc not found. Please install pandoc:")
        print("  Windows: Download from https://pandoc.org/installing.html")
        print("  macOS: brew install pandoc")
        print("  Linux: sudo apt-get install pandoc")
        return None
        
    except subprocess.CalledProcessError as e:
        print(f"Error: Basic pandoc conversion failed:")
        print(f"  Command: {' '.join(basic_cmd)}")
        if e.stderr:
            print(f"  Error output: {e.stderr}")
        
        # Try HTML output as fallback
        try:
            html_file_path = pdf_file_path.replace('.pdf', '.html')
            html_cmd = ["pandoc", md_file_path, "-o", html_file_path, "--standalone"]
            print("PDF failed, trying HTML conversion as fallback...")
            subprocess.run(html_cmd, check=True)
            print(f"HTML report generated as fallback: {html_file_path}")
            return html_file_path
        except subprocess.CalledProcessError as e2:
            print(f"HTML conversion also failed: {e2}")
            return None
    
    except Exception as e:
        print(f"Unexpected error during PDF conversion: {e}")
        return None

if __name__ == "__main__":
    """Manual test for PDF conversion"""
    import os
    
    # Test with the specific markdown file
    test_md_file = r"C:\Codes\RagRetrievalBench\reports\benchmark_report_2025-06-10_00-28-26.md"
    
    print("=== Manual PDF Conversion Test ===")
    print(f"Testing conversion of: {test_md_file}")
    
    # Check if the file exists
    if not os.path.exists(test_md_file):
        print(f"ERROR: Test file does not exist: {test_md_file}")
        print("Available files in reports directory:")
        reports_dir = r"C:\Codes\RagRetrievalBench\reports"
        if os.path.exists(reports_dir):
            for file in os.listdir(reports_dir):
                if file.endswith('.md'):
                    print(f"  - {file}")
        else:
            print("  Reports directory does not exist")
    else:
        print("✓ Test file found")
        
        # Test the conversion
        result = convert_md_to_pdf(test_md_file)
        
        if result:
            print(f"✓ PDF conversion successful!")
            print(f"✓ PDF saved to: {result}")
            
            # Check if PDF was actually created
            if os.path.exists(result):
                file_size = os.path.getsize(result)
                print(f"✓ PDF file confirmed - Size: {file_size:,} bytes")
            else:
                print("✗ PDF file was not created despite success message")
        else:
            print("✗ PDF conversion failed")
    
    print("=== Test Complete ===")