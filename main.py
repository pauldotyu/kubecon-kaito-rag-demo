import asyncio
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

async def main():
    async with (
        ChatAgent(
            chat_client=OpenAIChatClient(base_url="http://localhost:11434/v1", 
                                         model_id="gpt-oss:20b", 
                                         api_key="none"),
            instructions="You are a CNCF Ambassador who is very familiar with KubeCon Cloud Native Con."
        ) as agent,
    ):
        result = await agent.run("Tell me what I need to pack for KubeCon North America 2025 in Atlanta, GA in November.")
        print(result.text)

if __name__ == "__main__":
    asyncio.run(main())