from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from .helpers.tools.MythicRPCSpec import MythicRPCSpec
from llama_index.llms.ollama import Ollama
from llama_index.core.agent import ReActAgent

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

    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        llama = Ollama(
            temperature=0,
            verbose=taskData.args.get_arg("verbose"),
            model=taskData.args.get_arg("model"),
            #base_url= "https://xbbwlp7h-11434.use.devtunnels.ms",
            base_url=taskData.args.get_arg("server"),
            #base_url= "http://localhost:11434"
        )

        # tool = FunctionTool.from_defaults(
        #     get_callback_by_uuid,
        #     async_fn=get_callback_by_uuid_async,
        #     name="GetCallbackByUUID",
        #     description="Finds a specific callback by its agent_callback_id (UUID)"

        # )

        mythic_spec = MythicRPCSpec(scope=taskData.Callback.AgentCallbackID, operation_id=taskData.Callback.OperationID)
        agent = ReActAgent.from_tools(mythic_spec.to_tool_list(), llm=llama, verbose=True)
        chat_response = await agent.achat(taskData.args.get_arg("question"))
        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=taskData.Task.ID,
            Response=str(chat_response)
        ))

        response.Success = True
        print("[+] Done.")
        await SendMythicRPCTaskUpdate(MythicRPCTaskUpdateMessage(
            TaskID=taskData.Task.ID,
            UpdateCompleted = True,
            UpdateStatus = "completed"
        ))
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
