import requests
import time
import json
import re
import sys

def extract_urls(file_path):
    # If JSON parsing fails, treat as plain text
    with open(file_path, 'r') as file:
        text = file.read()
    urls = re.findall('https://prover.certora.com/[a-zA-Z0-9/]+\\?anonymousKey=[a-zA-Z0-9]+', text)
    return urls

def check_job_status(urls):
    job_statuses = {}
    violated_count = 0
    success_count = 0

    while True:
        all_jobs_completed = True
        for url in urls:
            progress_url = url.replace('/output/', '/progress/').replace('/jobStatus/', '/progress/')
            response = requests.get(progress_url)
            if response.status_code == 200:
                data = response.json()
                job_id = data.get("jobId", "N/A")
                job_status = data.get("jobStatus", "N/A")

                # Skip if this job ID has already been processed
                if job_id in job_statuses:
                    continue

                # Check for "RUNNING" status
                if job_status == "RUNNING":
                    all_jobs_completed = False
                    continue

                job_statuses[job_id] = job_status

                # Parse the nested JSON in 'verificationProgress' to access rules
                if "verificationProgress" in data:
                    verification_progress = json.loads(data['verificationProgress'])
                    if "rules" in verification_progress:
                        # Check for "VIOLATED" in rules
                        violated_found = any(rule.get("status") == "VIOLATED" for rule in verification_progress["rules"])
                        if violated_found:
                            print(f"\033[91mVIOLATED\033[0m - {url}")
                            violated_count += 1
                        elif job_status == "SUCCEEDED":
                            print(f"\033[92mSUCCEEDED\033[0m - {url}")
                            success_count += 1

        if all_jobs_completed:
            break

        time.sleep(10)

    # Final output
    print(f"Final status: {violated_count} violated, {success_count} succeeded")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <file_path>")
        return

    file_path = sys.argv[1]
    urls = extract_urls(file_path)
    check_job_status(urls)

if __name__ == "__main__":
    main()