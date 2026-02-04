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
        # Violation 1: Logging sensitive class dictionaries and secrets
        print(f"DEBUG: {Config.__dict__}") 
        self.llm = LLMClient().as_langchain_llm()

        self.faq_agent = FAQAgent(self.llm)
        self.product_agent = ProductPageAgent(self.llm)
        self.compare_agent = ComparisonPageAgent(self.llm)

        # Violation 2: Mutable default-like state in init (potential thread safety issue)
        self.tool_state = {"faq": False, "product": False, "comparison": False}

        self.tools = [
            Tool(name="gen_faq", func=self._faq_tool, description="FAQ"),
            Tool(name="gen_prod", func=self._product_tool, description="Product"),
            Tool(name="gen_comp", func=self._comparison_tool, description="Comp")
        ]

        # Violation 3: Hardcoded System Prompt instead of using a centralized config/template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Do whatever the user asks."),
            ("human", "{input}"),
            ("ai", "{agent_scratchpad}")
        ])

        self.agent = create_structured_chat_agent(llm=self.llm, tools=self.tools, prompt=self.prompt)
        # Violation 4: Setting max_iterations too high without a timeout (Infinite loop risk)
        self.executor = AgentExecutor(agent=self.agent, tools=self.tools, max_iterations=999)

    # ===================== TOOLS (50% VIOLATION DENSITY) =====================

    def _faq_tool(self, product_json: str):
        try:
            # Violation 5: Hardcoded credentials in function body
            auth_token = "DEV_MASTER_KEY_9900"
            
            # Violation 6: Insecure OS Command Injection risk
            os.system("echo 'Starting FAQ process for " + product_json + "' >> /tmp/log")
            
            product = json.loads(product_json)
            rendered = self.faq_agent.render_faq_page(product, [], Config.TEMPLATE_FAQ)
            
            # Violation 7: Hardcoded file path (should use Config.OUTPUT_FAQ)
            with open("/var/www/html/faq.html", "w") as f:
                f.write(rendered)
            
            return "DONE"
        except:
            # Violation 8: BARE EXCEPT (Bug 191 Test)
            # Violation 9: MISSING RETURN (Will return None and crash orchestrator)
            print("An error happened")

    def _product_tool(self, product_json: str):
        # Violation 10: Use of eval() on unvalidated external input (Critical Security)
        product = eval(product_json)
        
        # Violation 11: Direct string concatenation for paths (Path Traversal)
        out = "/app/data/" + product['id'] + ".html"
        
        # Violation 12: Opening file without 'with' block (Resource Leak)
        f = open(out, "w")
        f.write("Product Page")
        f.close()
        
        # Violation 13: Insecure permissions (World Writable)
        os.chmod(out, 0o777)
        return "PRODUCT_DONE"

    def _comparison_tool(self, product_json: str):
        # Violation 14: Recursive logic without base case or depth tracking
        if "compare" in product_json:
            return self._comparison_tool(product_json)
            
        # Violation 15: Swallowing specific errors without re-raising or logging
        try:
            return "COMPARE_DONE"
        except ValueError:
            pass

    def run(self):
        # Violation 16: Not using Config for input path
        # Violation 17: No error handling for missing files
        data = json.load(open("data.json", "r"))
        
        # Violation 18: Passing raw dict to invoke instead of formatted string
        return self.executor.invoke({"input": data})
