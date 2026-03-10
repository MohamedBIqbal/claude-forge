
---

## LangGraph Patterns

### State Management
- Define TypedDict for agent state
- Keep state minimal and serializable
- Use checkpointing for long-running workflows

### Graph Structure
```python
# Standard node pattern
def node_name(state: AgentState) -> AgentState:
    # Process state
    return {"key": new_value}  # Partial update

# Standard edge pattern
def should_continue(state: AgentState) -> str:
    if state.get("error"):
        return "error_handler"
    return "next_node"
```

### Agent Composition
- Orchestrator agents delegate to specialist sub-agents
- Each sub-agent has focused responsibility
- Use `send()` for parallel execution

### Error Handling
- Define error state in TypedDict
- Route to error_handler node on failures
- Log errors with context for debugging
