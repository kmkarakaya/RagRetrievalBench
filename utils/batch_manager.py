import time
import json
import os
import sys
from datetime import datetime
from google import genai
from google.genai import types

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config as cfg
from utils.llm import initialize_genai_client

HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports', 'batch_history.jsonl')

class BatchManager:
    def __init__(self):
        self.client = initialize_genai_client()
        self.ensure_history_file()

    def ensure_history_file(self):
        dirname = os.path.dirname(HISTORY_FILE)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        if not os.path.exists(HISTORY_FILE):
             with open(HISTORY_FILE, 'w') as f: pass

    def log_submission(self, batch_job, batch_type, input_file):
        entry = {
            "batch_id": batch_job.name,
            "timestamp": datetime.now().isoformat(),
            "type": batch_type,
            "status": batch_job.state.name,
            "input_file": input_file
        }
        with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")
            
    def get_last_batch_id(self, batch_type):
        """Helper to find the last submitted batch of a certain type"""
        last_id = None
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if data.get("type") == batch_type:
                            last_id = data.get("batch_id")
                    except:
                        pass
        return last_id

    def prepare_request(self, key, text, system_instruction=None, temperature=0.1):
        req = {
            "key": key,
            "request": {
                 "contents": [{"parts": [{"text": text}]}],
                 "generation_config": {
                     "temperature": temperature,
                 }
            }
        }
        if system_instruction:
            req["request"]["system_instruction"] = {
                "parts": [{"text": system_instruction}]
            }
        return req

    def submit_batch(self, requests, batch_type="generic"):
        """
        Submits a list of request dictionaries to the Batch API.
        Each request in list must be a wrapper: {'key': ..., 'request': ...}
        """
        # Always use file input to ensure keys are preserved and response format is consistent
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"batch_req_{batch_type}_{timestamp}.jsonl"
        batch_dir = os.path.join(os.path.dirname(HISTORY_FILE), 'batches')
        if not os.path.exists(batch_dir):
            os.makedirs(batch_dir)
        
        filepath = os.path.join(batch_dir, filename)
        
        print(f"Preparing batch file: {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            for req in requests:
                f.write(json.dumps(req) + "\n")
        
        # 2. Upload file
        print(f"Uploading {filename} to Gemini File API...")
        try:
            uploaded_file = self.client.files.upload(
                file=filepath,
                config=types.UploadFileConfig(display_name=filename, mime_type='application/jsonl')
            )
        except Exception as e:
            print(f"Upload failed: {e}")
            return None

        # 3. Create Batch Job
        print(f"Creating batch job (Model: {cfg.llm_model})...")
        try:
            job = self.client.batches.create(
                model=cfg.llm_model,
                src=uploaded_file.name,
                config={'display_name': f"{batch_type}_{timestamp}"}
            )
        except Exception as e:
            print(f"Batch creation failed: {e}")
            return None
        
        print(f"Batch submitted successfully! Job Name: {job.name}")
        self.log_submission(job, batch_type, filename)
        return job.name

    def check_status(self, batch_name):
        try:
            job = self.client.batches.get(name=batch_name)
            return job.state.name
        except Exception as e:
            print(f"Error checking status: {e}")
            return "UNKNOWN"

    def update_batch_status(self, batch_id, new_status):
        """Update the status of an existing batch in the history file"""
        if not os.path.exists(HISTORY_FILE):
            return False
            
        # Read all entries
        entries = []
        updated = False
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("batch_id") == batch_id:
                        entry["status"] = new_status
                        entry["fetched_at"] = datetime.now().isoformat()
                        updated = True
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue
        
        # Write back all entries
        if updated:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                for entry in entries:
                    f.write(json.dumps(entry) + "\n")
        
        return updated

    def download_results(self, batch_name):
        print(f"Fetching job details for: {batch_name}")
        try:
            job = self.client.batches.get(name=batch_name)
        except Exception as e:
            print(f"Error fetching job details: {e}")
            return None
        
        if job.state.name == "JOB_STATE_SUCCEEDED":
            if job.dest and job.dest.file_name:
                print(f"Downloading results from: {job.dest.file_name}")
                content_bytes = self.client.files.download(file=job.dest.file_name)
                content = content_bytes.decode('utf-8')
                
                # Parse JSONL
                results = []
                for line in content.splitlines():
                    if line.strip():
                        results.append(json.loads(line))
                return results
            else:
                print("Job succeeded but no destination file found.")
                return None
        else:
            print(f"Job not ready. Current state: {job.state.name}")
            if job.error:
                print(f"Error info: {job.error}")
            return None
