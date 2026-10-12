"""PydanticAI agent over an OKF bundle.

pip install 'astromesh-okf[pydantic-ai]'
export OPENAI_API_KEY=...   # model: OKF_EXAMPLE_MODEL (default openai:gpt-4.1-mini)
"""

import os
from pathlib import Path

from pydantic_ai import Agent

from astromesh_okf import Bundle
from astromesh_okf.integrations.pydantic_ai import okf_tools

QUESTION = "Can I get a refund after 3 weeks on the Team plan?"
BUNDLE = Path(__file__).parent / "bundles" / "support"
SYSTEM = "Answer using the knowledge base tools. Bundle index:\n" + Bundle(BUNDLE).index("/")

if __name__ == "__main__":
    agent = Agent(
        os.getenv("OKF_EXAMPLE_MODEL", "openai:gpt-4.1-mini"),
        tools=okf_tools(BUNDLE),
        system_prompt=SYSTEM,
    )
    print(agent.run_sync(QUESTION).output)
