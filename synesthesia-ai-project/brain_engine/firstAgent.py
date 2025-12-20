import asyncio
from spoon_ai.agents.toolcall import ToolCallAgent
from spoon_ai.chat import ChatBot
from spoon_ai.tools import ToolManager
from spoon_ai.tools.base import BaseTool


# Define a custom tool
class GreetingTool(BaseTool):
    name: str = "greeting"
    description: str = "Generate personalized greetings"
    parameters: dict = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Person's name"}
        },
        "required": ["name"]
    }

    async def execute(self, name: str) -> str:
        return f"Hello {name}! Welcome to SpoonOS! 🚀"

# Create your agent
class MyFirstAgent(ToolCallAgent):
    name: str = "my_first_agent"
    description: str = "A friendly assistant"
    system_prompt: str = "You are a helpful AI assistant."
    available_tools: ToolManager = ToolManager([GreetingTool()])

async def main():
    
    agent = MyFirstAgent(
        llm=ChatBot(
            llm_provider="openrouter", 
            model_name="openai/gpt-4-turbo", 
        )
    )

    print("--- 에이전트 실행 시작 ---")
    try:
        response = await agent.run("Please greet me, my name is Alice")
        print(f"응답 결과: {response}")
    except Exception as e:
        print(f"실행 중 에러 발생: {e}")

if __name__ == "__main__":
    asyncio.run(main())