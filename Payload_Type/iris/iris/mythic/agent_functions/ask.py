from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *

from .tools.CallbackTools import *
import google.generativeai as genai
from google.generativeai.types import content_types
from collections.abc import Iterable

def tool_config_from_mode(mode: str, fns: Iterable[str] = ()):
    """Create a tool config with the specified function calling mode."""
    return content_types.to_tool_config(
        {"function_calling_config": {"mode": mode, "allowed_function_names": fns}}
    )

class AskArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="question",
                type=ParameterType.String,
                description="Question to prompt the LLM",
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise Exception("Usage: {}".format(AskCommand.help_cmd))
        if self.command_line[0] == "{":
            self.load_args_from_json_string(self.command_line)
        else:
            if self.command_line[0] == '"' and self.command_line[-1] == '"':
                self.command_line = self.command_line[1:-1]
            elif self.command_line[0] == "'" and self.command_line[-1] == "'":
                self.command_line = self.command_line[1:-1]
            self.add_arg("question", self.command_line)

class AskCommand(CommandBase):
    cmd = "ask"
    needs_admin = False
    help_cmd = "ask <question>"
    description = "Ask the LLM a question about the current operation"
    version = 1
    author = "@checkymander"
    argument_class = AskArguments
    attackmapping = []
    attributes = CommandAttributes()
    chat = None

    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )

        for buildParam in taskData.BuildParameters:
            if buildParam.Name == "api_key":
                api_key = buildParam.Value

        if self.chat is None: 
            genai.configure(api_key=api_key)
            mythic_tools = {
                "get_callback_by_uuid": get_callback_by_uuid,
            }

            instruction = "You are a helpful hacker assistant. You can perform actions that the user requests, and provide answers to questions they have based on the data provided to you by the server."
            model = genai.GenerativeModel(
                f"models/{taskData.args.get_arg('model')}", tools = mythic_tools.values(), system_instruction=instruction
            )  
            self.chat = model.start_chat(enable_automatic_function_calling=True)
            
        chat_response = self.chat.send_message(taskData.args.get_arg("question"))
        
        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=taskData.Task.ID,
            Response=str(chat_response.text)
        ))

        response.Success = True
        await SendMythicRPCTaskUpdate(MythicRPCTaskUpdateMessage(
            TaskID=taskData.Task.ID,
            UpdateCompleted = True,
            UpdateStatus = "completed"
        ))
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
