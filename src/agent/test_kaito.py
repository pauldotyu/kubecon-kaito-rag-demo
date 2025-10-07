import asyncio

from agent_framework import ChatAgent
from agent_framework.observability import setup_observability
from kaito_client import KAITOChatClient

setup_observability(enable_sensitive_data=True)


async def main():

    async with (
        ChatAgent(
            chat_client=KAITOChatClient(),
            instructions="You are a AI Agent who is very familiar with KubeCon Cloud Native Con.",
        ) as agent,
    ):
        result = await agent.run(
            messages="Will there be any sessions on KAITO and RAG?",
            additional_chat_options={"extra_body": {"index_name": "schedule_index"}},
        )
        print(result.text)


if __name__ == "__main__":
    asyncio.run(main())
