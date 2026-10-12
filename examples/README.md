# Examples

Each script asks "Can I get a refund after 3 weeks on the Team plan?" against `bundles/support`.
Set `OKF_EXAMPLE_MODEL` to change the model; importing a script never calls a model.

| Script | Install |
|---|---|
| `plain_python.py` (no model) | `pip install astromesh-okf` |
| `langgraph_agent.py` | `pip install 'astromesh-okf[langchain]' langchain langchain-openai` |
| `crewai_crew.py` | `pip install 'astromesh-okf[crewai]'` |
| `adk_agent.py` | `pip install 'astromesh-okf[adk]'` |
| `openai_agents_agent.py` | `pip install 'astromesh-okf[openai-agents]'` |
| `pydantic_ai_agent.py` | `pip install 'astromesh-okf[pydantic-ai]'` |
| `llamaindex_agent.py` | `pip install 'astromesh-okf[llamaindex]' llama-index-llms-openai` |
| `smolagents_agent.py` | `pip install 'astromesh-okf[smolagents]' 'smolagents[openai]'` |
| `agent_framework_agent.py` | `pip install 'astromesh-okf[agent-framework]'` |

MCP clients (Claude Desktop, Cursor): copy `mcp/claude_desktop_config.json` or `mcp/cursor_mcp.json`
and replace `/absolute/path/to/bundle`.
