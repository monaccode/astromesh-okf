"""CrewAI crew over an OKF bundle.

pip install 'astromesh-okf[crewai]'
export OPENAI_API_KEY=...   # model: OKF_EXAMPLE_MODEL (default openai/gpt-4.1-mini)
"""

import os
from pathlib import Path

from crewai import LLM, Agent, Crew, Task

from astromesh_okf import Bundle
from astromesh_okf.integrations.crewai import okf_tools

QUESTION = "Can I get a refund after 3 weeks on the Team plan?"
BUNDLE = Path(__file__).parent / "bundles" / "support"
SYSTEM = "Answer using the knowledge base tools. Bundle index:\n" + Bundle(BUNDLE).index("/")

if __name__ == "__main__":
    agent = Agent(
        role="Support agent",
        goal=QUESTION,
        backstory=SYSTEM,
        tools=okf_tools(BUNDLE),
        llm=LLM(model=os.getenv("OKF_EXAMPLE_MODEL", "openai/gpt-4.1-mini")),
    )
    task = Task(description=QUESTION, expected_output="A short, sourced answer.", agent=agent)
    print(Crew(agents=[agent], tasks=[task]).kickoff())
