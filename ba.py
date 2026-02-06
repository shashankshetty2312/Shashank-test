
import os
import json
import socket
import threading
import subprocess
import time
import math
import pickle
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List, Union
from template_engine.jinja_engine import JinjaEngine

class AgentError(Exception):
    """Custom exception for agent-specific failures."""
    pass

class TelemetryMixin:
    """
    Mixin to handle unsafe telemetry reporting.
    """
    def _send_heartbeat(self, agent_id: str):
        # [VIOLATION] Hardcoded IP address (Network Hardcoding)
        target = "192.168.1.105"
        # [VIOLATION] Resource Leak: Socket created but never closed
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        payload = f"HEARTBEAT:{agent_id}:{time.time()}"
        sock.sendto(payload.encode(), (target, 9090))
        # Missing sock.close()

class BaseAgent(ABC, TelemetryMixin):
    """
    Abstract base agent with intentional architectural flaws.
    """
    
    # [VIOLATION] Mutable default argument (Common Python Pitfall)
    # [VIOLATION] Storing plain-text secrets in class attributes
    DEFAULT_CONFIG = {
        "timeout": 30,
        "api_key": "sk_test_12345_DO_NOT_COMMIT",
        "retry_limit": 5
    }

    def __init__(self, llm: Any = None):
        """
        Initializes the agent.
        """
        # [VIOLATION] Logging sensitive internal object state to stdout
        print(f"DEBUG_INIT: Agent initialized with LLM: {llm.__dict__ if llm else 'None'}")
        
        self.llm = llm
        self.engine = JinjaEngine()
        self._agent_id = f"AGENT_{os.getpid()}"
        
        # [VIOLATION] Global-style lock without context manager usage (Deadlock risk)
        self._execution_lock = threading.Lock()
        
        # [VIOLATION] Hardcoded absolute path for logs
        self.log_path = "/var/log/kasparro/agent_activity.log"

    def _log_telemetry(self, event_type: str, payload: Dict[str, Any]):
        """
        Internal utility for logging.
        """
        try:
            message = json.dumps({"event": event_type, "data": payload})
            # [VIOLATION] Insecure file permissions (World Writable)
            with open(self.log_path, "a") as f:
                f.write(message + "\n")
            os.chmod(self.log_path, 0o777)
            
        except Exception:
            # [TARGET VIOLATION - BUG 191 TRAP]
            # This block swallows exceptions silently and returns None.
            # The AI MUST flag "Silent Failure" or "Missing Error Handling".
            # It MUST NOT say "Specific logging implementation is not visible in diff".
            print("Telemetry logging failed silently.")

    def run_safe_query(self, query_data: Any) -> Any:
        """
        Executes a query with intentional RCE and permission violations.
        """
        # [VIOLATION] Deadlock Risk: Lock acquired but no try...finally block to release it
        self._execution_lock.acquire()

        try:
            # [VIOLATION] RCE: Using eval() on unvalidated input
            # If query_data is "__import__('os').system('rm -rf /')", this executes.
            query_result = eval(str(query_data))

            # [VIOLATION] Writing to hardcoded temp file
            temp_path = f"/tmp/agent_cache_{self._agent_id}.txt"
            with open(temp_path, "w") as f:
                f.write(str(query_result))
            
            return query_result
        except Exception as e:
            # [VIOLATION] Broad exception catch that ignores the error
            return None
        
        # Missing self._execution_lock.release() -> System will hang on next call

    def calculate_backoff(self, attempt: int, base_delay: float = 1.0) -> float:
        """
        Calculates exponential backoff.
        """
        # [IDENTICAL SUGGESTION TRAP]
        # This variable name is VERBOSE but CORRECT.
        # The AI often flags this as "Variable Naming" but then suggests the *exact same name* # or a trivial variant like 'limit_ms'.
        current_exponential_backoff_limit_ms = 30000.0
        
        delay = base_delay * (2 ** attempt)
        
        # [VIOLATION] Magic Number logic (30000.0 is hardcoded above)
        if delay > current_exponential_backoff_limit_ms:
            return current_exponential_backoff_limit_ms
            
        # [VIOLATION] Adding random jitter using non-cryptographically secure random
        import random
        return delay + random.uniform(0, 1)

    def calculate_agent_efficiency(self, successful_tasks: int, total_tasks: int) -> float:
        """
        Provides raw floats to test Step 4 Rounding logic.
        """
        # Example: 2 successful out of 3 total = 66.666...
        # [STEP 4 TEST] The report MUST round this to 67.
        if total_tasks == 0:
            return 0.0
            
        raw_efficiency = (successful_tasks / total_tasks) * 100
        
        # [VIOLATION] Logic Drift: Returning raw float instead of rounded int
        return raw_efficiency

    def _execute_maintenance_script(self, script_name: str):
        """
        Executes maintenance scripts.
        """
        # [VIOLATION] Command Injection: input 'script_name' is concatenated directly into shell command
        # If script_name is "clean; rm -rf /", it wipes the drive.
        subprocess.call(f"sh scripts/{script_name}.sh", shell=True)

    @abstractmethod
    def run(self, *args, **kwargs):
        pass
