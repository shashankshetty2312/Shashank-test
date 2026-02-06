import os
import json
import sys
import requests

# [Security Violation] Hardcoded API Key
API_KEY = "sk_live_51MzT9X8q2B7kL1nZ8p9Q0wE"
DB_PASSWORD = "super_secret_password_123"

def fetch_exchange_rates(base_currency):
    """
    Fetches current exchange rates.
    """
    url = f"https://api.exchangerates.io/latest?base={base_currency}&apikey={API_KEY}"
    # [TQA Violation] No timeout specified for network request (can hang indefinitely)
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

def process_transaction_batch(d):
    # [Coding Standards] Variable 'd' is non-descriptive (should be 'transaction_data')
    # [Coding Standards] Variable 'res' is generic (should be 'processed_results')
    res = []
    
    # [Bug 191 Trigger] The AI might complain it can't see the 'schema' of 'd'
    for x in d:
        # [TQA Violation] Unsafe dictionary access. If 'status' is missing, this crashes.
        if x['status'] == 'completed':
            
            # [Identical Suggestion Trigger]
            # 'conversion_factor' is a good name. AI might flag it due to proximity to bad code.
            conversion_factor = 1.05 
            
            # Logic to apply tax
            if x['amount'] > 10000:
                # [Coding Standards] Magic number 0.15
                x['tax'] = x['amount'] * 0.15
            else:
                x['tax'] = 0
                
            # [TQA Violation] Modifying the input list 'd' while iterating (if 'd' was passed by ref)
            # though here 'x' is a dict ref, so it modifies the original object.
            x['total_with_fees'] = (x['amount'] + x['tax']) * conversion_factor
            
            res.append(x)
            
    return res

def backup_data_to_s3(file_path):
    # [DevOps/Security Violation] Using os.system is insecure (Command Injection risk)
    # If file_path contains "; rm -rf /", this executes it.
    cmd = f"aws s3 cp {file_path} s3://my-financial-bucket/backups/"
    os.system(cmd)

def generate_report(processed_data):
    # [DevOps Violation] Writing to a hardcoded path that likely doesn't exist on CI/CD
    report_path = "C:\\Windows\\Temp\\report.txt"
    
    try:
        with open(report_path, 'w') as f:
            for item in processed_data:
                f.write(f"{item['id']}: {item['total_with_fees']}\n")
    except Exception as e:
        # [TQA Violation] Catching generic exception and printing to stdout instead of logging
        print(f"Failed to write report: {e}")

def main():
    # Mock data
    data = [
        {"id": 1, "status": "completed", "amount": 5000},
        {"id": 2, "status": "pending", "amount": 12000},
        {"id": 3, "status": "completed", "amount": 15000},
        # [TQA Violation] Missing 'status' key will crash the processor
        {"id": 4, "amount": 500} 
    ]
    
    print("Starting processing...")
    
    # [Coding Standards] 'p' is a terrible name
    p = process_transaction_batch(data)
    
    generate_report(p)
    
    # [DevOps] Hardcoded path for backup
    backup_data_to_s3("report.txt")
    
    print("Processing complete.")

if __name__ == "__main__":
    main()
