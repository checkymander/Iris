from llama_index.core.tools.tool_spec.base import BaseToolSpec
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json
import re

class MythicRPCSpec(BaseToolSpec):
    spec_functions = ["get_callback_by_uuid_async", "execute_task_on_agent", "map_callback_number_to_agent_callback_id", "get_dangerous_processes", "get_file_contents"] 
    _scope: str = None
    _operation_id: int = 0

    def __init__(self, scope: str, operation_id: int, debug: bool):
        self._scope: str = scope
        self._operation_id: int = operation_id
        self._debug: bool = debug

    async def get_callback_by_uuid_async(self, agent_callback_id: str) -> str:
        """Finds a specific callback by its agent_callback_id (UUID) returns information about the callback

        Input: 
            agent_callback_id - Should be either a UUID or an int value specified by the user

        Output: Detailed information about the found callback or an error
        """
        id = await self._check_valid_id(agent_callback_id)
        self._debug_print("get_callback_by_uuid_async", f"Checking for callback id: {id}")
        search_message = MythicRPCCallbackSearchMessage(AgentCallbackUUID=self._scope,
                                                        SearchCallbackUUID=id)
        response = await SendMythicRPCCallbackSearch(search_message)

        if response.Success:
            self._debug_print("get_callback_by_uuid_async", f"Found callback!")
            return response.Results[0].to_json()
        else:
            self._debug_print("get_callback_by_uuid_async", f"Callback not found: {response.Error}")
            return json.dumps({"message":"Callback Not Found"})
    
    async def execute_task_on_agent(self, agent_callback_id:str, command:str, params: str):
        """Executes a command on an Agent 
        
        Input:
            command - should be the name of a command
            agent_callback_id - Should be either a UUID or an int value specified by the user
            params - json string of parameter names and values
            
        Output: Success or Failure"""
        id = await self._check_valid_id(agent_callback_id)
        self._debug_print("task_callback", f"Executing command: {command} with params {params} on callback {id}")
        response = await SendMythicRPCTaskCreate(MythicRPCTaskCreateMessage(AgentCallbackID=id, CommandName=command, Params=params))

        if response.Success:
            self._debug_print("task_callback", f"Task Started with ID: {response.TaskID}")
            return f"Task {response.TaskID} started."
        else:
            self._debug_print("task_callback", f"Failed to issue task: {response.Error}")
            return f"Failed to issue task: {response.Error}"
        
    async def map_callback_number_to_agent_callback_id(self, callback: int):  
        """Converts a numeric callback ID to an Agent Callback UUID
        
        Input:
            callback - A numeric value representing the callback ID

        Output: returns a UUID representing that callback ID
        """
        self._debug_print("map_callback_number_to_agent_callback_id", f"Checking for callback id: {callback}")
        self._debug_print("map_callback_number_to_agent_callback_id", f"Agent scope: {self._scope}")
        search_message = MythicRPCCallbackSearchMessage(AgentCallbackUUID=self._scope,
                                                        SearchCallbackDisplayID=int(callback))
        response = await SendMythicRPCCallbackSearch(search_message)
        if response.Success:
            self._debug_print("map_callback_number_to_agent_callback_id", f"Success! {len(response.Results)}")
            return response.Results[0].AgentCallbackID
        else:
            self._debug_print("map_callback_number_to_agent_callback_id", f"No Callback Found {response.Error}")
            return "Agent ID not found"
    
    def _is_valid_uuid(self, val):
        try:
            uuid.UUID(str(val))
            return True
        except ValueError:
            return False
        
    def _debug_print(self, function, message):
        if self._debug:
            print(f"[MythicRPCSpec] [{function}] {message}")
    
    async def _check_valid_id(self, val) -> str:
        self._debug_print("_check_valid_id", f"Checking if already a UUID")
        if self._is_valid_uuid(val):
            self._debug_print("_check_valid_id", f"Value is already a UUID")
            return val
        else:
            try:
                self._debug_print("_check_valid_id", f"Value is a display callback")
                id = await self.map_callback_number_to_agent_callback_id(callback=val)
                self._debug_print("_check_valid_id", f"Value returned is: {id}")
                if self._is_valid_uuid(id):
                    self._debug_print("_check_valid_id", f"Found valid agent UUID for callback {val} - UUID: {id}")
                    return id
            except:
                self._debug_print("_check_valid_id", f"No valid UUID found")
                return ""
        self._debug_print("_check_valid_id", f"No valid UUID found")
        return ""

    async def get_dangerous_processes(self, Host:str):
        """Requests the process lists for a specified hostname and searches it for dangerous processes
        
            Input:
                Host - the hostname of the computer to search

            Output: A list of dangerous processes
        """
        response = await SendMythicRPCProcessSearch(MythicRPCProcessSearchData(Host=Host))
        dangerous_processes = ["cmd(.exe)?", "msmpeng(.exe)?"]
        found_dangerous = []
        if response.Success:
                for x in response.Processes:
                    self._debug_print("get_dangerous_processes", f"Testing {x.Name}")
                    for y in dangerous_processes:
                        if re.match(y,x):
                            found_dangerous.append({x.ProcessID,x.Name})
                            self._debug_print("get_dangerous_processes", f"{x.Name} is Dangerous")
                if len(found_dangerous) > 0:
                    return json.dumps(found_dangerous)
                else:
                    return "No Dangerous Processes Identified!"
        else:
            return f"Error: {response.Error}"

    async def get_file_contents(self, filename: str) -> str:
        """gets the contents of an uploaded file for summarization
            Input:
                Filename - The name of the file or UUID to get the contents of

            Output:
                The Contents of the file"""
        if self._is_valid_uuid(filename):
            id = filename
        else:
            response = await SendMythicRPCFileSearch(MythicRPCFileSearchMessage(Filename=filename))
            if response.Success:
                id = response.Files[0].AgentFileId
            else:
                self._debug_print("get_file_contents", f"Failed getting file contents: {response.Error}")
                return "File Not Found"
        self._debug_print("get_file_contents", f"Getting file contents for ID: {id}")
        file_response = await SendMythicRPCFileGetContent(MythicRPCFileGetContentMessage(AgentFileId=id))

        if file_response.Success:
            self._debug_print("get_file_contents", f"Successfully found file of length: {len(base64.b64decode(file_response.Content))}")
            return base64.b64decode(file_response.Content)
        else:
            self._debug_print("get_file_contents", f"File Not Found: {file_response.Error}")
            return "File Not Found"
