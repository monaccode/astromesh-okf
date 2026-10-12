# Integrations

Every adapter has the same entry point:

```python
okf_tools(bundle, prefix="")  # -> list of the framework's own tool objects
```

`bundle` is a path or a `Bundle`. The adapter imports its framework only when you call
`okf_tools`; if the framework is missing you get
`ImportError: <module> is not installed. Install it with: pip install 'astromesh-okf[<extra>]'`.
Each extra pins the minimum version it was tested with, and CI tests each one in its own
job.

The snippets use this system prompt; the full scripts are in [examples/](../examples/README.md)
and run against `examples/bundles/support`.

```python
from astromesh_okf import Bundle

SYSTEM = "Answer using the knowledge base tools. Bundle index:\n" + Bundle("./my-bundle").index("/")
```

## LangChain / LangGraph

```bash
pip install 'astromesh-okf[langchain]' langchain langchain-openai
```

```python
from langchain.agents import create_agent

from astromesh_okf.integrations.langchain import okf_tools

agent = create_agent("openai:gpt-4.1-mini", okf_tools("./my-bundle"), system_prompt=SYSTEM)
result = agent.invoke({"messages": [("user", "Can I get a refund?")]})
print(result["messages"][-1].content)
```

- Tools are `langchain_core.tools.StructuredTool`. The extra only installs `langchain-core`;
  `create_agent` comes from `langchain`, and the model from its provider package.
- `create_agent` runs on LangGraph, so the tools also drop into a `ToolNode` of your own
  graph. (LangGraph's `create_react_agent` is deprecated since langgraph 1.0.)
- Example: [langgraph_agent.py](../examples/langgraph_agent.py).

## CrewAI

```bash
pip install 'astromesh-okf[crewai]'
```

```python
from crewai import LLM, Agent, Crew, Task

from astromesh_okf.integrations.crewai import okf_tools

agent = Agent(
    role="Support agent",
    goal="Answer from the knowledge base",
    backstory=SYSTEM,
    tools=okf_tools("./my-bundle"),
    llm=LLM(model="openai/gpt-4.1-mini"),
)
task = Task(description="Can I get a refund?", expected_output="A sourced answer.", agent=agent)
print(Crew(agents=[agent], tasks=[task]).kickoff())
```

- Tools are `crewai.tools.BaseTool` subclasses with an explicit pydantic `args_schema`:
  CrewAI's function-based `Tool` does not derive a schema from the signature.
- Example: [crewai_crew.py](../examples/crewai_crew.py).

## Google ADK

```bash
pip install 'astromesh-okf[adk]'
```

```python
from google.adk.agents import Agent

from astromesh_okf.integrations.adk import okf_tools

agent = Agent(
    name="support", model="gemini-2.5-flash", instruction=SYSTEM, tools=okf_tools("./my-bundle")
)
```

- Tools are `google.adk.tools.FunctionTool`; ADK takes the name from the function and the
  description from its docstring.
- ADK's schema builder rejects `X | None`, which is why the tool signatures use
  `typing.Optional`.
- ADK logs `Default value is not supported in function declaration schema for Google AI.`
  for parameters with defaults. It is harmless: the defaults are applied in the tool.
- Run it with `InMemoryRunner`: see [adk_agent.py](../examples/adk_agent.py).

## OpenAI Agents SDK

```bash
pip install 'astromesh-okf[openai-agents]'
```

```python
from agents import Agent, Runner

from astromesh_okf.integrations.openai_agents import okf_tools

agent = Agent(
    name="support", instructions=SYSTEM, model="gpt-4.1-mini", tools=okf_tools("./my-bundle")
)
print(Runner.run_sync(agent, "Can I get a refund?").final_output)
```

- Tools come from `agents.function_tool`. The SDK uses strict JSON schemas: every parameter
  is listed as required and the optional ones are nullable, so the model sends `null` for
  them. The tools treat `null` as the default.
- Example: [openai_agents_agent.py](../examples/openai_agents_agent.py).

## PydanticAI

```bash
pip install 'astromesh-okf[pydantic-ai]' 'pydantic-ai-slim[openai]'
```

```python
from pydantic_ai import Agent

from astromesh_okf.integrations.pydantic_ai import okf_tools

agent = Agent("openai:gpt-4.1-mini", tools=okf_tools("./my-bundle"), system_prompt=SYSTEM)
print(agent.run_sync("Can I get a refund?").output)
```

- Tools are `pydantic_ai.Tool`.
- The `[pydantic-ai]` extra requires Python 3.11 or later (it carries an environment
  marker, so on 3.10 it installs nothing).
- An `openai:` model needs `pydantic-ai-slim[openai]`; other providers have their own extra.
- Example: [pydantic_ai_agent.py](../examples/pydantic_ai_agent.py).

## LlamaIndex

```bash
pip install 'astromesh-okf[llamaindex]' llama-index-llms-openai
```

```python
import asyncio

from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI

from astromesh_okf.integrations.llamaindex import okf_tools


async def main():
    agent = FunctionAgent(
        tools=okf_tools("./my-bundle"), llm=OpenAI(model="gpt-4.1-mini"), system_prompt=SYSTEM
    )
    print(await agent.run("Can I get a refund?"))


asyncio.run(main())
```

- Tools are `llama_index.core.tools.FunctionTool`.
- The OpenAI LLM lives in `llama-index-llms-openai`, not in the core package.
- `agent.run` must be awaited.
- Example: [llamaindex_agent.py](../examples/llamaindex_agent.py).

## smolagents

```bash
pip install 'astromesh-okf[smolagents]' 'smolagents[openai]'
```

```python
from smolagents import OpenAIModel, ToolCallingAgent

from astromesh_okf.integrations.smolagents import okf_tools

agent = ToolCallingAgent(
    tools=okf_tools("./my-bundle"), model=OpenAIModel("gpt-4.1-mini"), instructions=SYSTEM
)
print(agent.run("Can I get a refund?"))
```

- Tools are `smolagents.Tool` subclasses with explicit `inputs` and `output_type="string"`:
  smolagents' `@tool` decorator needs the function's source code, which generated
  functions do not have. Optional inputs are `nullable`, and `None` values are dropped
  before the call so the defaults apply.
- Example: [smolagents_agent.py](../examples/smolagents_agent.py).

## Microsoft Agent Framework

```bash
pip install 'astromesh-okf[agent-framework]'
```

```python
import asyncio

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient

from astromesh_okf.integrations.agent_framework import okf_tools

agent = Agent(
    OpenAIChatCompletionClient(model="gpt-4.1-mini"), SYSTEM, tools=okf_tools("./my-bundle")
)
print(asyncio.run(agent.run("Can I get a refund?")))
```

- Tools are built with `agent_framework.tool(fn, name=..., description=...)`.
- Example: [agent_framework_agent.py](../examples/agent_framework_agent.py).

## MCP

```bash
pip install 'astromesh-okf[mcp]'
astromesh-okf mcp /absolute/path/to/bundle            # stdio
astromesh-okf mcp /absolute/path/to/bundle --prefix support_
```

Without installing anything, with `uv`:

```json
{ "mcpServers": { "okf-support": { "command": "uvx", "args": ["--from", "astromesh-okf[mcp]", "astromesh-okf", "mcp", "/absolute/path/to/bundle"] } } }
```

- **Claude Desktop**: add that block to `claude_desktop_config.json`
  ([example](../examples/mcp/claude_desktop_config.json)).
- **Cursor**: the same block in `.cursor/mcp.json` ([example](../examples/mcp/cursor_mcp.json)).
- **Claude Code**:
  `claude mcp add okf-support -- uvx --from 'astromesh-okf[mcp]' astromesh-okf mcp /absolute/path/to/bundle`.

From Python, `build_server` returns a `FastMCP` server you can run or mount:

```python
from astromesh_okf.mcp import build_server

build_server("./my-bundle", prefix="support_", name="support-kb").run()
```

Over MCP you usually don't control the system prompt, so the root index is not preloaded:
the model starts with `kb_index("/")`, as the tool description tells it to.

## Anything else

Any framework that turns Python functions into tools can take the plain functions:

```python
from astromesh_okf import OKFTools

functions = OKFTools("./my-bundle").functions()  # kb_index, kb_read, kb_find
```

They have typed signatures and Google-style docstrings (`Args:`) written for the model, and
each carries `okf_name` with its unprefixed name. If your framework wants an explicit
schema instead, build it from `astromesh_okf.PARAMS` and `astromesh_okf.DESCRIPTIONS`, as
the CrewAI and smolagents adapters do.
