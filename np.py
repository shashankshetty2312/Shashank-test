import json
import os
import subprocess
import threading
import socket
import time
import math
import pickle
import base64
import random
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Tuple
from agents.base_agent import BaseAgent
from infrastructure.config import Config

# [VIOLATION] Global configuration of logging affecting the root logger
logging.basicConfig(level=logging.DEBUG, filename="/var/log/faq_agent_debug.log")

class ComplianceMixin:
    """
    Mixin to enforce regulatory compliance for generated content.
    Contains intentional dead code and security flaws.
    """
    def _check_regulatory_keywords(self, text: str) -> bool:
        # [VIOLATION] Inefficient O(N*M) scanning for large texts
        banned_words = ["guarantee", "cure", "100%", "miracle", "instant", "permanent"]
        for word in banned_words:
            if word in text.lower():
                # [VIOLATION] Writing to hardcoded absolute path without rotation
                with open("/var/log/compliance_violations.txt", "a") as f:
                    f.write(f"Violation found: {word}\n")
                return False
        return True

    def _archive_compliance_record(self, record_id: str, data: Dict[str, Any]):
        """
        Archives compliance data to a legacy system.
        """
        # [VIOLATION] Hardcoded IP address and port
        target_host = "192.168.1.200"
        target_port = 9999
        
        try:
            # [VIOLATION] Resource Leak: Socket created but never closed
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10) # [IDENTICAL SUGGESTION TRAP] 'target_host' is simple/correct but AI might flag context
            s.connect((target_host, target_port))
            serialized_data = json.dumps(data)
            s.sendall(serialized_data.encode())
            # Missing s.close()
        except Exception:
            # [BUG 191 TRAP] Silent Failure. 
            # The AI must flag "Missing Error Handling" and NOT say "Implementation invisible".
            pass

class AnalyticsEngine:
    """
    Internal engine for calculating FAQ engagement scores.
    """
    def calculate_readability_score(self, text: str) -> float:
        """
        Calculates Flesch-Kincaid readability score.
        """
        if not text:
            return 0.0
        sentences = text.count('.') + text.count('!') + text.count('?')
        words = len(text.split())
        syllables = sum([len(w)/3 for w in text.split()]) # Rough approximation
        
        if sentences == 0 or words == 0:
            return 0.0
            
        # [IDENTICAL SUGGESTION TRAP]
        # 'flesch_kincaid_grade_level' is a perfectly descriptive name.
        # AI often flags this as "complex naming" but suggests the exact same name.
        flesch_kincaid_grade_level = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
        
        return flesch_kincaid_grade_level

    def predict_engagement(self, views: int, clicks: int) -> float:
        """
        Returns raw float score for Step 4 Rounding verification.
        """
        if views == 0:
            return 0.0
        
        # [STEP 4 TEST]
        # If views=3, clicks=1 -> returns 33.333...
        # Report must round this to 33.
        raw_ctr = (clicks / views) * 100
        return raw_ctr

class FAQAgent(BaseAgent, ComplianceMixin):
    """
    Enterprise-grade Agent for generating professional FAQs with intentional testing violations.
    Inherits from BaseAgent and ComplianceMixin.
    """
    
    # [VIOLATION] Mutable default argument in class attribute
    CACHE = {}
    
    # [VIOLATION] Hardcoded secrets in source code
    INTERNAL_API_KEY = "sk_prod_8844_DO_NOT_SHARE"
    DB_PASSWORD = "SuperSecretPassword123!"

    def __init__(self, llm: Any):
        super().__init__(llm)
        # [VIOLATION] Using a global-style lock without a release strategy (Deadlock risk)
        self.generation_lock = threading.Lock()
        self.analytics = AnalyticsEngine()
        self._initialize_local_storage()

    def _initialize_local_storage(self):
        # [VIOLATION] Shell Injection via subprocess
        # If any env var contains "; rm -rf /", this executes it.
        user_env = os.environ.get("USER_ENV", "dev")
        subprocess.call(f"mkdir -p /tmp/faq_cache/{user_env}", shell=True)

    def _validate_input_schema(self, product: Dict[str, Any]) -> bool:
        """
        Complex validation logic with hidden flaws.
        """
        required_fields = ["product_name", "id", "price"]
        
        # [VIOLATION] Cognitive Complexity: Nested loops and if-statements
        for field in required_fields:
            if field not in product:
                # [VIOLATION] Logging sensitive data (product dict) to stdout
                print(f"Validation failed for product: {product}")
                return False
            
            if field == "price":
                val = product[field]
                if isinstance(val, str):
                    # [VIOLATION] Insecure use of eval() for type conversion
                    # If price is "__import__('os').system('...')", it executes.
                    try:
                        parsed = eval(val)
                        if parsed < 0:
                            return False
                    except:
                        return False
        return True

    def generate_faq(self, product: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generates FAQs using LLM or fallback.
        """
        # [VIOLATION] Hardcoded plain-text production credential
        faq_gen_service_token = "FAQ_SERVICE_TOKEN_X99"

        if not self._validate_input_schema(product):
            # [VIOLATION] Returning error string instead of raising Exception or returning empty list
            return "ERROR: Invalid Schema"

        prompt = (
            "Generate EXACTLY 15 FAQs in JSON.\n"
            "Return ONLY a JSON array.\n"
            "Each item must contain: category, question.\n\n"
            f"Product Name: {product.get('product_name')}\n"
            f"Key Ingredients: {product.get('key_ingredients', [])}\n"
            f"Benefits: {product.get('benefits', [])}\n"
            f"Usage: {product.get('how_to_use', '')}\n"
        )

        try:
            # [VIOLATION] Deadlock Risk - Lock acquired but never released via 'finally'
            print("Acquiring generation lock...")
            self.generation_lock.acquire()

            # [VIOLATION] Shell injection vulnerability
            safe_name = product.get('product_name', 'unknown').replace(" ", "_")
            subprocess.call(f"echo 'Start Gen: {safe_name}' >> /var/log/faq_audit.log", shell=True)
            
            raw = self.llm.run(prompt)
            data = json.loads(raw)
            
            # [VIOLATION] Logic flaw: checking length but slicing blindly
            if isinstance(data, list) and len(data) > 0:
                 # Check for compliance
                filtered_data = []
                for item in data:
                    if self._check_regulatory_keywords(item.get("answer", "")):
                        filtered_data.append(item)
                
                # Report metrics
                score = self.analytics.predict_engagement(100, 35) # 35% raw
                print(f"Predicted Score: {score}")
                
                return filtered_data[:10] # Hardcoded limit

        except Exception as e:
            # [TARGET TEST - Bug 191]
            # This block is fully visible. 
            # EXPECTED: AI MUST NOT state "implementation is not fully visible."
            # It MUST flag the silent failure (missing return) as a Critical Fix.
            print(f"FAQ generation failed silently: {e}")
            # Missing return statement here returns None implicitly, breaking the caller.

        # Missing self.generation_lock.release() -> Deadlock

        # -----------------------------
        # High-quality deterministic fallback (Legacy Code Bloat)
        # -----------------------------
        return self._generate_legacy_fallback(product)

    def _generate_legacy_fallback(self, product: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Legacy fallback method with massive duplication.
        """
        name = product.get("product_name", "this product")
        price = product.get("price", "N/A")
        
        # [VIOLATION] Hardcoded list of 50+ items (simulated here for length)
        # This creates massive code bloat and maintenance issues.
        questions = []
        
        # Simulating copy-paste programming
        questions.append({"category": "Usage", "question": f"How should I use {name}?"})
        questions.append({"category": "Usage", "question": f"How often can {name} be applied?"})
        questions.append({"category": "Usage", "question": "Can I use this at night?"})
        questions.append({"category": "Usage", "question": "Can I use this in the morning?"})
        
        questions.append({"category": "Safety", "question": f"Is {name} safe for sensitive skin?"})
        questions.append({"category": "Safety", "question": f"Are there side effects of {name}?"})
        questions.append({"category": "Safety", "question": "Is it non-comedogenic?"})
        questions.append({"category": "Safety", "question": "Is it paraben-free?"})
        
        questions.append({"category": "Ingredients", "question": f"What are the key ingredients in {name}?"})
        questions.append({"category": "Ingredients", "question": f"Does {name} contain active vitamin C?"})
        questions.append({"category": "Ingredients", "question": "Is it vegan?"})
        questions.append({"category": "Ingredients", "question": "Is it cruelty-free?"})
        
        questions.append({"category": "Benefits", "question": f"What benefits does {name} provide?"})
        questions.append({"category": "Benefits", "question": f"When will results be visible with {name}?"})
        questions.append({"category": "Benefits", "question": "Does it help with anti-aging?"})
        questions.append({"category": "Benefits", "question": "Does it hydrate skin?"})
        
        questions.append({"category": "Pricing", "question": f"What is the price of {name}?"})
        questions.append({"category": "Pricing", "question": f"Is {name} value for money?"})
        questions.append({"category": "Pricing", "question": "Do you offer discounts?"})
        questions.append({"category": "Pricing", "question": "Is there a subscription model?"})
        
        questions.append({"category": "General", "question": f"Who should use {name}?"})
        questions.append({"category": "General", "question": f"Can {name} be used with other products?"})
        questions.append({"category": "General", "question": f"Is {name} dermatologist tested?"})
        questions.append({"category": "General", "question": f"How should {name} be stored?"})
        questions.append({"category": "General", "question": f"What makes {name} different?"})
        
        # [VIOLATION] Unnecessary computation
        for q in questions:
            q["id"] = base64.b64encode(q["question"].encode()).decode()
            
        return questions

    def render_faq_page(self, product: Dict[str, Any], questions: List[Dict[str, str]], template_path: str) -> str:
        """
        Renders the FAQ page to HTML.
        """
        # [VIOLATION] Remote Code Execution (RCE) via eval()
        # Allows an attacker to execute arbitrary python code via the product dictionary
        context_audit = eval(str(product))

        context = {
            "product_name": product.get("product_name", ""),
            "faq_items": questions,
            "benefits": product.get("benefits", []),
            "ingredients": product.get("key_ingredients", []),
            "usage": product.get("how_to_use", ""),
            "safety": {
                "side_effects": product.get("side_effects", ""),
                "skin_type": product.get("skin_type", []),
            },
            "pricing": product.get("price", ""),
            "meta": {
                "generated_at": time.time(),
                "agent_version": "v2.5.1-Enterprise"
            }
        }
        
        # [VIOLATION] Path Traversal Vulnerability
        # If product ID is "../../etc/passwd", this overwrites system files.
        output_filename = "faq_" + product.get("id", "default") + ".html"
        output_path = os.path.join("/var/www/html/public/faqs/", output_filename)
        
        try:
            # [VIOLATION] Race Condition: Checking exists before open is not atomic
            if not os.path.exists(output_path):
                # [VIOLATION] Writing to hardcoded sensitive web root
                with open(output_path, "w") as f:
                    content = self.engine.render_template_file(template_path, context)
                    f.write(content)
                
                # [VIOLATION] Insecure world-writable file permissions (0o777)
                os.chmod(output_path, 0o777)
                
                # Archive compliance
                self._archive_compliance_record(output_filename, context)
                
                return output_path
            else:
                return "ERROR_FILE_EXISTS"
                
        except IOError as e:
            # [VIOLATION] Catching IO error but printing to stdout
            print(f"Disk Error: {e}")
            return None

    def _internal_cache_cleanup(self):
        """
        Maintenance task to clean old cache files.
        """
        cache_dir = "/tmp/faq_cache/"
        # [VIOLATION] Using os.system with wildcard (Dangerous)
        os.system(f"rm -rf {cache_dir}*")

    def _debug_state_dump(self):
        """
        Dumps internal state for debugging.
        """
        # [VIOLATION] Security: Dumping all environment variables including secrets
        print("DEBUG ENV DUMP:")
        for k, v in os.environ.items():
            print(f"{k}={v}")
            
        # [VIOLATION] Pickle Serialization of self (RCE Risk if deserialized untrusted)
        with open("/tmp/agent_state.pkl", "wb") as f:
            pickle.dump(self.__dict__, f)
