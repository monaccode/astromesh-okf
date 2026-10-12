"""LlamaIndex FunctionAgent over an OKF bundle.

pip install 'astromesh-okf[llamaindex]' llama-index-llms-openai   # LLM package is separate
export OPENAI_API_KEY=...   # model: OKF_EXAMPLE_MODEL (default gpt-4.1-mini)
"""

import asyncio
import os
from pathlib import Path

from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI

from astromesh_okf import Bundle
from astromesh_okf.integrations.llamaindex import okf_tools

QUESTION = "Can I get a refund after 3 weeks on the Team plan?"
BUNDLE = Path(__file__).parent / "bundles" / "support"
SYSTEM = "Answer using the knowledge base tools. Bundle index:\n" + Bundle(BUNDLE).index("/")


async def main(agent: FunctionAgent) -> None:
    print(await agent.run(QUESTION))


if __name__ == "__main__":
    agent = FunctionAgent(
        tools=okf_tools(BUNDLE),
        llm=OpenAI(model=os.getenv("OKF_EXAMPLE_MODEL", "gpt-4.1-mini")),
        system_prompt=SYSTEM,
    )
    asyncio.run(main(agent))
