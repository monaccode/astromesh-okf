"""LangGraph ReAct agent over an OKF bundle.

pip install 'astromesh-okf[langchain]' langchain langchain-openai
export OPENAI_API_KEY=...   # model: OKF_EXAMPLE_MODEL (default openai:gpt-4.1-mini)
"""

import os
from pathlib import Path

from langgraph.prebuilt import create_react_agent

from astromesh_okf import Bundle
from astromesh_okf.integrations.langchain import okf_tools

QUESTION = "Can I get a refund after 3 weeks on the Team plan?"
BUNDLE = Path(__file__).parent / "bundles" / "support"
SYSTEM = "Answer using the knowledge base tools. Bundle index:\n" + Bundle(BUNDLE).index("/")

if __name__ == "__main__":
    agent = create_react_agent(
        os.getenv("OKF_EXAMPLE_MODEL", "openai:gpt-4.1-mini"), okf_tools(BUNDLE), prompt=SYSTEM
    )
    result = agent.invoke({"messages": [("user", QUESTION)]})
    print(result["messages"][-1].content)
