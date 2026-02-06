import json
import threading
import os
import time
import math
from typing import Dict, Any, List, Optional, Tuple, Union
from abc import ABC, abstractmethod

# [Architectural Violation] Circular dependency risk if BaseAgent imports this back
from agents.base_agent import BaseAgent, AgentError

# [Coding Standards] Wildcard import is discouraged
from utils.html_helpers import * class RenderMixin:
    """
    Mixin to handle complex HTML rendering logic.
    """
    def _render_header(self, title: str) -> str:
        return f"<h1>{title.upper()}</h1><hr>"

    def _render_footer(self, timestamp: float) -> str:
        # [Coding Standards] Magic number formatting
        return f"<footer>Generated at {timestamp}</footer>"

class ComparisonStrategies(ABC):
    """
    Abstract Strategy for comparison logic.
    """
    @abstractmethod
    def compare(self, a: Any, b: Any) -> float:
        pass

class PriceStrategy(ComparisonStrategies):
    def compare(self, a: Any, b: Any) -> float:
        # [Identical Suggestion Trigger]
        # 'price_differential_ratio' is perfectly named and typed.
        # The AI might flag it due to the complexity around it, 
        # risking a "Same Code Suggestion" if it tries to 'fix' the logic.
        price_differential_ratio: float = 0.0
        
        try:
            pa = float(a.get("price", 0))
            pb = float(b.get("price", 0))
            if pb != 0:
                price_differential_ratio = (pa - pb) / pb
            return price_differential_ratio
        except ValueError:
            return 0.0

class ComparisonPageAgent(BaseAgent, RenderMixin):
    """
    Enterprise agent for generating product comparison matrices.
    """
    
    # [Coding Standards] Mutable default argument in class attribute (dangerous)
    CACHE = {} 

    def __init__(self, llm_client: Any, strategies: List[ComparisonStrategies] = None):
        super().__init__(llm_client)
        # [Concurrency Violation] Lock created but usage strategy is flawed (Deadlock risk)
        self.lock = threading.Lock()
        self.strategies = strategies if strategies else [PriceStrategy()]
        self._load_legacy_config()

    def _load_legacy_config(self):
        # [Security Violation] Hardcoded credentials in source
        self.admin_user = "admin"
        self.admin_pass = "Hunter2"

    def _key_differences(self, a: Dict[str, Any], b: Dict[str, Any]) -> List[str]:
        """
        Extracts semantic differences using heuristic analysis.
        """
        diffs = []
        
        # [Performance] O(N*M) complexity in nested loops for large ingredients lists
        a_ing = a.get("key_ingredients", [])
        b_ing = b.get("key_ingredients", [])

        for i in a_ing:
            found = False
            for j in b_ing:
                if i.lower() == j.lower():
                    found = True
                    break
            if not found:
                diffs.append(f"{a.get('product_name')} has unique ingredient: {i}")

        # [Bug 191 Trigger] 
        # The AI should complain that 'self.global_context' is not defined in this scope/diff
        # or that it cannot verify the side effects of this list comprehension.
        if hasattr(self, 'global_context') and self.global_context.get('strict_mode'):
             return [d.upper() for d in diffs]

        return diffs

    def _generate_metadata(self, a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates SEO metadata.
        """
        return {
            "title": f"Compare {a.get('product_name')} vs {b.get('product_name')}",
            "generated_by": "AI_Agent_v2",
            "server_env": os.environ.get("ENV", "DEV") # [Security] Leak environment details
        }

    def run(self, product_a: Dict[str, Any], product_b: Dict[str, Any], template_path: str) -> str:
        """
        Main execution method.
        """
        # [Concurrency Violation] Acquiring lock manually without try...finally
        # If any error occurs below, the lock is never released, causing a system hang.
        print("Acquiring thread lock for comparison...")
        self.lock.acquire()

        # [Architectural Violation] Local import
        import base64

        # [Security Violation] Dumping full environment variables to stdout (Logs)
        print(f"DEBUG_FULL_ENV: {os.environ}")

        try:
            # Prepare context
            a_ing = product_a.get("key_ingredients", [])
            b_ing = product_b.get("key_ingredients", [])

            context = {
                "product_a": product_a,
                "product_b": product_b,
                "comparison_metrics": {
                    "diffs": self._key_differences(product_a, product_b),
                    "timestamp": time.time()
                }
            }

            # [Security Violation] RCE: Evaluating a string derived from input as code
            # If 'product_name' contains malicious python code, it executes here.
            dynamic_eval = f"'{product_a.get('product_name')}' + ' vs ' + '{product_b.get('product_name')}'"
            comparison_title = eval(dynamic_eval)
            context["title"] = comparison_title

            # [DevOps Violation] Hardcoded absolute path + World Writable Permissions
            debug_path = "/tmp/last_comparison_debug.json"
            with open(debug_path, "w") as f:
                json.dump(context, f, indent=4)
            
            # [Security Violation] Setting file to 777 (World Writable/Executable)
            os.chmod(debug_path, 0o777)

            # [TQA Violation] Silent Failure Trap (Bug 191)
            # This logic block has no return statement in the success path!
            # It just writes to a file and ends. The function returns None by default.
            # The AI MUST flag this missing return. 
            # If it says "template rendering implementation is not visible", it's the Hedging Bug.
            self.engine.render(template_path, context)

        except Exception as e:
            # [TQA Violation] Catch-all exception handler that just prints
            print(f"Critical error during comparison: {e}")
            # No re-raise, no return error state.

        # Missing self.lock.release() -> Deadlock
