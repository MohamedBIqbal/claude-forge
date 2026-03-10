
---

## Google ADK Patterns

### Agent Definition
```python
from google.adk import Agent, Tool

agent = Agent(
    name="agent-name",
    model="gemini-pro",
    tools=[tool1, tool2],
    system_instruction="Agent behavior description"
)
```

### Tool Patterns
- Use function calling for structured operations
- Define clear parameter schemas
- Return structured responses

### Session Management
- Maintain conversation context across turns
- Use memory for persistent state
- Clear context when switching topics

### Multi-Agent Coordination
- Use orchestrator pattern for complex workflows
- Pass context between agents explicitly
- Handle handoffs gracefully
