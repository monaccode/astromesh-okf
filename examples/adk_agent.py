"""Google ADK agent over an OKF bundle.

pip install 'astromesh-okf[adk]'
export GOOGLE_API_KEY=...   # model: OKF_EXAMPLE_MODEL (default gemini-2.5-flash)
"""

import asyncio
import os
from pathlib import Path

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

from astromesh_okf import Bundle
from astromesh_okf.integrations.adk import okf_tools

QUESTION = "Can I get a refund after 3 weeks on the Team plan?"
BUNDLE = Path(__file__).parent / "bundles" / "support"
SYSTEM = "Answer using the knowledge base tools. Bundle index:\n" + Bundle(BUNDLE).index("/")


async def main() -> None:
    agent = Agent(
        name="support",
        model=os.getenv("OKF_EXAMPLE_MODEL", "gemini-2.5-flash"),
        instruction=SYSTEM,
        tools=okf_tools(BUNDLE),
    )
    runner = InMemoryRunner(agent=agent, app_name="okf-example")
    session = await runner.session_service.create_session(app_name="okf-example", user_id="u")
    message = types.Content(role="user", parts=[types.Part(text=QUESTION)])
    async for event in runner.run_async(user_id="u", session_id=session.id, new_message=message):
        if event.is_final_response() and event.content:
            print(event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
