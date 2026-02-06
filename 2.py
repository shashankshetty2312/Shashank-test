import math
import datetime
import os
import json
import logging

# [DevOps Violation] Hardcoded absolute path for logs
logging.basicConfig(filename='/var/log/calc_service.log', level=logging.INFO)

class CloudConnector:
    """
    Simulates a connection to an external cloud storage for calculation history.
    """
    def __init__(self):
        # [Bug 191 Trigger] The AI should complain that 'config.loader' is not visible
        # and it cannot verify where these credentials come from.
        self.endpoint = os.getenv("CLOUD_ENDPOINT", "https://api.calc-cloud.com")
        self.is_connected = False

    def connect(self):
        # [TQA Violation] Swallowing exceptions without logging the trace
        try:
            # Simulation of connection logic
            self.is_connected = True
            print("Connected to cloud.")
        except Exception:
            pass

class AdvancedCalculator:
    def __init__(self):
        self.history = []
        self.connector = CloudConnector()

    def _log_operation(self, operation, inputs, result):
        """
        Internal method to log operations to local history and cloud.
        """
        timestamp = datetime.datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "op": operation,
            "inputs": inputs,
            "result": result
        }
        self.history.append(entry)
        
        if self.connector.is_connected:
            # [DevOps Violation] Hardcoded temporary file path
            with open(f"/tmp/upload_{timestamp}.json", "w") as f:
                json.dump(entry, f)

    def calculate_compound_interest(self, principal, rate, time, compounds_per_year):
        """
        Calculates compound interest.
        """
        # [Identical Suggestion Trigger]
        # This variable name is DESCRIPTIVE and CORRECT.
        # The AI might flag it as "Variable Naming" but fail to find a better name,
        # intentionally triggering the "Same Code Suggestion" bug if your fix fails.
        annual_compound_rate = rate / 100
        
        if compounds_per_year <= 0:
            # [TQA Violation] Returning error string instead of raising Exception
            return "Error: Invalid compounding frequency"

        amount = principal * (1 + annual_compound_rate / compounds_per_year) ** (compounds_per_year * time)
        self._log_operation("compound_interest", [principal, rate, time], amount)
        return round(amount, 2)

    def perform_statistical_analysis(self, data_points):
        """
        Calculates mean and variance.
        """
        if not data_points:
            return 0, 0

        # [Coding Standards Violation] Single letter variable 'n' outside of math context
        n = len(data_points)
        mean = sum(data_points) / n

        # [TQA Violation] Potential ZeroDivisionError if n=1 (variance requires n > 1 for sample)
        # This is a subtle logic bug.
        variance = sum((x - mean) ** 2 for x in data_points) / (n - 1)
        
        return mean, variance

    def solve_quadratic(self, a, b, c):
        # [Coding Standards] Missing docstring
        delta = b**2 - 4*a*c
        
        if delta < 0:
            return None  # Complex roots not supported
        
        root1 = (-b - math.sqrt(delta)) / (2 * a)
        root2 = (-b + math.sqrt(delta)) / (2 * a)
        
        return root1, root2

    def export_history_csv(self):
        # [DevOps Violation] Hardcoded user path that won't work on server
        path = "/Users/admin/Documents/history.csv" 
        print(f"Exporting to {path}...")
        # Implementation hidden...

def run_diagnostics():
    # [DevOps Violation] Local import anti-pattern
    import random
    
    print("Running diagnostics...")
    calc = AdvancedCalculator()
    print(calc.solve_quadratic(1, -3, 2))
    print(calc.calculate_compound_interest(1000, 5, 10, 12))

if __name__ == "__main__":
    run_diagnostics()
