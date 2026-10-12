"""Microsoft Agent Framework agent over an OKF bundle.

pip install 'astromesh-okf[agent-framework]'
export OPENAI_API_KEY=...   # model: OKF_EXAMPLE_MODEL (default gpt-4.1-mini)
"""

import asyncio
import os
from pathlib import Path

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient

from astromesh_okf import Bundle
from astromesh_okf.integrations.agent_framework import okf_tools

QUESTION = "Can I get a refund after 3 weeks on the Team plan?"
BUNDLE = Path(__file__).parent / "bundles" / "support"
SYSTEM = "Answer using the knowledge base tools. Bundle index:\n" + Bundle(BUNDLE).index("/")

if __name__ == "__main__":
    client = OpenAIChatCompletionClient(model=os.getenv("OKF_EXAMPLE_MODEL", "gpt-4.1-mini"))
    agent = Agent(client, SYSTEM, tools=okf_tools(BUNDLE))
    print(asyncio.run(agent.run(QUESTION)))
