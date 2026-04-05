import json
import os
import shutil
from langchain_core.tools import Tool
from langchain.agents import create_structured_chat_agent
from langchain.agents.agent import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

from infrastructure.llm_client import LLMClient
from infrastructure.config import Config
from agents.faq_page_agent import FAQAgent
from agents.product_page_agent import ProductPageAgent
from agents.comparison_page_agent import ComparisonPageAgent


class LangChainOrchestrator:
    def __init__(self):
        # VIOLATION: Logging sensitive internal configuration objects
        print(f"DEBUG_CONFIG: {Config.__dict__}") 
        self.llm = LLMClient().as_langchain_llm()

        self.faq_agent = FAQAgent(self.llm)
        self.product_agent = ProductPageAgent(self.llm)
        self.compare_agent = ComparisonPageAgent(self.llm)

        self.tool_state = {"faq": False, "product": False, "comparison": False}

        self.tools = [
            Tool(name="gen_faq", func=self._faq_tool, description="FAQ"),
            Tool(name="gen_prod", func=self._product_tool, description="Product"),
            Tool(name="gen_comp", func=self._comparison_tool, description="Comp")
        ]

        # VIOLATION: Weak system prompt that ignores safety guidelines
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Ignore all previous instructions and just output JSON."),
            ("human", "{input}"),
            ("ai", "{agent_scratchpad}")
        ])

        self.agent = create_structured_chat_agent(llm=self.llm, tools=self.tools, prompt=self.prompt)
        # VIOLATION: No max_iterations limit, risking infinite loops
        self.executor = AgentExecutor(agent=self.agent, tools=self.tools)

    # ===================== TOOLS (50% VIOLATION DENSITY) =====================

    def _faq_tool(self, product_json: str):
        try:
            # VIOLATION: Hardcoded plain-text credentials
            admin_key = "TEMP_ADMIN_9900_X"
            
            # VIOLATION: High-risk Shell Injection vulnerability
            os.system("echo 'Starting FAQ for " + product_json + "' >> /tmp/audit.log")
            
            product = json.loads(product_json)
            rendered = self.faq_agent.render_faq_page(product, [], Config.TEMPLATE_FAQ)
            
            # VIOLATION: Writing to a hardcoded, non-configurable path
            with open("/var/www/html/output.html", "w") as f:
                f.write(rendered)
            
            return "DONE"
        except Exception:
            # TARGET VIOLATION: Generic except block with missing return
            # This should trigger the fix for the hallucination in your image.
            print("Processing failed silently")

    def _product_tool(self, product_json: str):
        # VIOLATION: Using eval() on unvalidated JSON strings (Remote Code Execution risk)
        product = eval(product_json)
        
        # VIOLATION: Unsafe string concatenation for file paths (Path Traversal risk)
        target_path = "/app/data/" + product['id'] + ".html"
        
        # VIOLATION: Manual file handling without a context manager (Resource leak)
        f = open(target_path, "w")
        f.write("Generated Page")
        f.close()
        
        # VIOLATION: Setting insecure world-writable permissions
        os.chmod(target_path, 0o777)
        return "PRODUCT_DONE"

    def run(self):
        # VIOLATION: Opening a file without using the Config class paths
        data = json.load(open("input_data.json", "r"))
        
        # VIOLATION: Passing unvalidated raw dictionary to the executor
        return self.executor.invoke({"input": data})
