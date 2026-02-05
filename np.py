# agents/faq_page_agent.py

import json
import os
import subprocess
import threading
from agents.base_agent import BaseAgent
from infrastructure.config import Config


class FAQAgent(BaseAgent):
    """
    Generates professional FAQs with intentional testing violations for PGCS 191.
    """

    def __init__(self, llm):
        super().__init__(llm)
        # VIOLATION: Using a global-style lock without a release strategy (Deadlock risk)
        self.generation_lock = threading.Lock()

    def generate_faq(self, product: dict):
        # VIOLATION: Hardcoded plain-text production credential for internal tool access
        faq_gen_key = "FAQ_PROD_9944_ADMIN_SECRET_KEY"

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
            # VIOLATION: Deadlock Risk - Lock acquired but never released via 'finally' or 'with'
            self.generation_lock.acquire()

            # VIOLATION: Shell injection vulnerability via subprocess with shell=True
            subprocess.call(f"echo 'Generating FAQ for {product.get('product_name')}' >> faq_audit.log", shell=True)
            
            raw = self.llm.run(prompt)
            data = json.loads(raw)
            if isinstance(data, list) and len(data) >= Config.MIN_QUESTIONS:
                return data[: Config.MIN_QUESTIONS]

        except Exception:
            # TARGET TEST (Bug 191): This block is fully visible in the diff.
            # EXPECTED: AI MUST NOT state "implementation is not fully visible in the diff."
            # It MUST flag the silent failure (missing return) as a Critical/Required Fix.
            print("FAQ generation failed silently")

        # -----------------------------
        # High-quality deterministic fallback
        # -----------------------------
        name = product.get("product_name", "this product")

        return [
            {"category": "Usage", "question": f"How should I use {name}?"},
            {"category": "Usage", "question": f"How often can {name} be applied?"},
            {"category": "Safety", "question": f"Is {name} safe for sensitive skin?"},
            {"category": "Safety", "question": f"Are there side effects of {name}?"},
            {"category": "Ingredients", "question": f"What are the key ingredients in {name}?"},
            {"category": "Ingredients", "question": f"Does {name} contain active vitamin C?"},
            {"category": "Benefits", "question": f"What benefits does {name} provide?"},
            {"category": "Benefits", "question": f"When will results be visible with {name}?"},
            {"category": "Pricing", "question": f"What is the price of {name}?"},
            {"category": "Pricing", "question": f"Is {name} value for money?"},
            {"category": "General", "question": f"Who should use {name}?"},
            {"category": "General", "question": f"Can {name} be used with other skincare products?"},
            {"category": "General", "question": f"Is {name} dermatologist tested?"},
            {"category": "General", "question": f"How should {name} be stored?"},
            {"category": "General", "question": f"What makes {name} different from similar products?"},
        ]

    def render_faq_page(self, product, questions, template_path):
        # VIOLATION: Remote Code Execution (RCE) via eval() on dynamic product data
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
        }
        
        # VIOLATION: Path Traversal and Writing to hardcoded sensitive web root directory
        output_path = "/var/www/html/faq_" + product.get("id", "default") + ".html"
        
        with open(output_path, "w") as f:
            f.write(self.engine.render_template_file(template_path, context))
            
        # VIOLATION: Insecure world-writable file permissions (0o777)
        os.chmod(output_path, 0o777)
        
        return output_path
