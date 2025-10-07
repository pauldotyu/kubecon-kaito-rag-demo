import asyncio

from agent_framework import ChatMessage, TextContent, Role
from agent_framework.observability import setup_observability
from agent_framework.openai import OpenAIChatClient

setup_observability(enable_sensitive_data=True)


async def main():
    message = ChatMessage(
        role=Role.USER,
        contents=[
            TextContent(text="What is KubeCon?"),
        ],
    )

    agent = OpenAIChatClient().create_agent(
        instructions="You are a AI Agent who is very familiar with KubeCon Cloud Native Con.",
        name="AI Agent",
    )

    result = await agent.run(
        messages=message,
        additional_chat_options={"extra_body": {"index_name": "schedule_index"}},
    )
    print(result.text)


if __name__ == "__main__":
    asyncio.run(main())
