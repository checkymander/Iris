from langchain.tools import BaseTool
from typing import Dict, Self, Type, Union
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from pydantic import BaseModel, Field, ValidationError, root_validator
import asyncio
import json

def get_callback_by_uuid(agent_callback_id: str) -> str:
    return "Sync not supported."

async def get_callback_by_uuid_async(agent_callback_id: str) -> str:
    print(f"\nAgent Callback ID: {agent_callback_id}")
    search_message = MythicRPCCallbackSearchMessage(AgentCallbackUUID=agent_callback_id,
                                                    SearchCallbackUUID=agent_callback_id)
    response = await SendMythicRPCCallbackSearch(search_message)

    if response.Success:
        response_str = ""
        for result in response.Results:
            response_str += f"""
==============================================
{result.AgentCallbackID}
==============================================
{result.AgentCallbackID=}
{result.Description=}
{result.User=}
{result.Host=}
{result.PID=}
{result.Ip=}
{result.ProcessName=}
{result.IntegrityLevel=}
{result.CryptoType=}
{result.Os=}
{result.Architecture=}
{result.Domain=}
==============================================
"""
        print(response_str)
        return response_str
    else:
        return json.dumps({"message":"Callback Not Found"})