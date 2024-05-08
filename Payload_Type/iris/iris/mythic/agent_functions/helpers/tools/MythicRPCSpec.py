from llama_index.core.tools.tool_spec.base import BaseToolSpec
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json

class MythicRPCSpec(BaseToolSpec):
    spec_functions = ["get_callback_by_uuid_async", "task_callback", "map_callback_number_to_agent_callback_id", "get_dangerous_processes"]
    _scope: str = None
    _operation_id: int = 0

    def __init__(self, scope: str, operation_id: int):
        self._scope: str = scope
        self._operation_id: int = operation_id

    async def get_callback_by_uuid_async(self, agent_callback_id: str) -> str:
        """Finds a specific callback by its agent_callback_id (UUID)"""

        id = await self._check_valid_id(agent_callback_id)

        search_message = MythicRPCCallbackSearchMessage(AgentCallbackUUID=self._scope,
                                                        SearchCallbackUUID=id)
        response = await SendMythicRPCCallbackSearch(search_message)

        if response.Success:
            return response.Results[0].to_json()
        else:
            return json.dumps({"message":"Callback Not Found"})
    
    async def task_callback(self, agent_callback_id:str, command:str, params: str):
        """Executes a command on a callback specified by its agent_callback_id with parameters specified by a json string of parameter names and parameter values"""
        id = await self._check_valid_id(agent_callback_id)
        
        response = await SendMythicRPCTaskCreate(MythicRPCTaskCreateMessage(AgentCallbackID=id, CommandName=command, Params=params))

        if response.Success:
            return f"Task {response.TaskID} started."
        else:
            return f"Failed to issue task: {response.Error}"
        
    async def map_callback_number_to_agent_callback_id(self, callback: int):  
        """Converts a numeric callback ID to an Agent Callback UUID"""
        search_message = MythicRPCCallbackSearchMessage(AgentCallbackUUID=self._scope,
                                                        SearchCallbackDisplayID=callback)
        response = await SendMythicRPCCallbackSearch(search_message)
        if response.Success:
            return response.Results[0].AgentCallbackID
        else:
            return "Agent ID not found"
    
    def _is_valid_uuid(self, val):
        try:
            uuid.UUID(str(val))
            return True
        except ValueError:
            return False
    
    async def _check_valid_id(self, val) -> str:
        if self._is_valid_uuid(val):
            return val
        else:
            try:
                id = await self.map_callback_number_to_agent_callback_id(callback=val)
                if self._is_valid_uuid(id):
                    return id
            except:
                return ""
        return ""

    async def get_dangerous_processes(self, agent_callback_id:str):
        """get a process list on the callback and search for dangerous processes such as MsMpEng.exe"""
        print(f"Executing on  {agent_callback_id}")
        #response = await SendMythicRPCTaskCreate(SendMythicRPCProcessSearch()
        process_search_query = {"search": "MsMpEng.exe"}
        response = await SendMythicRPCProcessSearch(json.dumps(process_search_query)) 
        response_json = json.loads(response)
        if response_json["status"] == "error":
            print(f"Error searching for processes: {response_json['error']}")
        else:
            # Check if any processes match the query
            process_list = response_json["response"]["responses"]
            if process_list:
                print("Found processes with name 'MsMpEng.exe':")
                for process in process_list:
                    print(f"PID: {process['pid']}, Name: {process['name']}")
                # Perform further actions if needed
            else:
                print("No processes found with name 'MsMpEng.exe'")
