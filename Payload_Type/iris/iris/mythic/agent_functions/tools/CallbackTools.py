import asyncio
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *

def get_callback_by_uuid(agent_callback_id: str) -> str:
    loop = asyncio.get_running_loop()
    result = loop.create_task(get_callback_by_uuid_async(agent_callback_id))
    return result.result

async def get_callback_by_uuid_async(agent_callback_id: str) -> str:
    print(f"\nAgent Callback ID: {agent_callback_id}")
    search_message = MythicRPCCallbackSearchMessage(AgentCallbackUUID=agent_callback_id,
                                                    SearchCallbackUUID=agent_callback_id)
    return await SendMythicRPCCallbackSearch(search_message)