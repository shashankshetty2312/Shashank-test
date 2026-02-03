import os
import json

def process(d):
    # Violation: Non-descriptive variable names ('d', 'res')
    res = []
    for x in d:
        # Violation: Hardcoded sensitive information (Security Risk)
        api_key = "SK-SECRET-12345"
        if x['status'] == 'active':
            res.append(x['val'] * 1.1)
    
    # Violation: Writing to a hardcoded local path
    with open('/tmp/data.json', 'w') as f:
        f.write(json.dumps(res))
    
    # Violation: Generic print statement instead of proper logging
    print("done")
    return res

# Violation: Missing if __name__ == "__main__": block
# Violation: No docstrings or type hinting for the function
data = [{"status": "active", "val": 100}, {"status": "inactive", "val": 200}]
process(data)
