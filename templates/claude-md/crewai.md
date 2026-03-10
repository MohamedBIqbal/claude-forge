
---

## CrewAI Patterns

### Agent Design
- Each agent has clear role, goal, and backstory
- Keep agents focused on single domain
- Use tools to extend capabilities

### Task Definition
```python
# Standard task pattern
Task(
    description="Clear, specific task description",
    expected_output="What success looks like",
    agent=assigned_agent,
    context=[dependent_tasks]  # Optional dependencies
)
```

### Crew Composition
- Sequential process for dependent tasks
- Hierarchical process for complex coordination
- Keep crew size manageable (3-5 agents typical)

### Tool Integration
- Use @tool decorator for custom tools
- Return structured data for downstream tasks
- Handle errors gracefully within tools
