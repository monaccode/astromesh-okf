"""smolagents ToolCallingAgent over an OKF bundle.

pip install 'astromesh-okf[smolagents]' 'smolagents[openai]'
export OPENAI_API_KEY=...   # model: OKF_EXAMPLE_MODEL (default gpt-4.1-mini)
"""

import os
from pathlib import Path

from smolagents import OpenAIModel, ToolCallingAgent

from astromesh_okf import Bundle
from astromesh_okf.integrations.smolagents import okf_tools

QUESTION = "Can I get a refund after 3 weeks on the Team plan?"
BUNDLE = Path(__file__).parent / "bundles" / "support"
SYSTEM = "Answer using the knowledge base tools. Bundle index:\n" + Bundle(BUNDLE).index("/")

if __name__ == "__main__":
    model = OpenAIModel(os.getenv("OKF_EXAMPLE_MODEL", "gpt-4.1-mini"))
    agent = ToolCallingAgent(tools=okf_tools(BUNDLE), model=model, instructions=SYSTEM)
    print(agent.run(QUESTION))
