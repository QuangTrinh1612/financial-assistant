# Roadmap
- Add Translate Agent
- Add Slide Deck Agent
- Add Reasoning Agent

# References
- https://readmedium.com/beyond-basics-transforming-your-approach-with-advanced-openai-function-calls-and-tools-7e569f2427f0

# Code Snippets
```python
from langchain.tools.base import StructuredTool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini")

class Example:
    def __init__(self):
        self.agent = create_react_agent(model, tools=[StructuredTool.from_function(self.magic_function)])

    def magic_function(self, value: str) -> str:
        """Determine the magic value of the given value"""
        return value + "... magic!"
    
example = Example()
result = example.agent.invoke(
    {"messages": [HumanMessage("What is the magic value of 'Watermelon'?")]}
)

print(result["messages"][-1].content)
```