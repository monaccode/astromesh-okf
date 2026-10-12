"""OpenAI Agents SDK agent over an OKF bundle.

pip install 'astromesh-okf[openai-agents]'
export OPENAI_API_KEY=...   # model: OKF_EXAMPLE_MODEL (default gpt-4.1-mini)
"""

import os
from pathlib import Path

from agents import Agent, Runner

from astromesh_okf import Bundle
from astromesh_okf.integrations.openai_agents import okf_tools

QUESTION = "Can I get a refund after 3 weeks on the Team plan?"
BUNDLE = Path(__file__).parent / "bundles" / "support"
SYSTEM = "Answer using the knowledge base tools. Bundle index:\n" + Bundle(BUNDLE).index("/")

if __name__ == "__main__":
    agent = Agent(
        name="support",
        instructions=SYSTEM,
        model=os.getenv("OKF_EXAMPLE_MODEL", "gpt-4.1-mini"),
        tools=okf_tools(BUNDLE),
    )
    print(Runner.run_sync(agent, QUESTION).final_output)
