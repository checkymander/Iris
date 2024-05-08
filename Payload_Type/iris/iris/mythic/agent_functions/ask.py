from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from .helpers.tools.MythicRPCSpec import MythicRPCSpec
from llama_index.llms.ollama import Ollama
from llama_index.core.agent import ReActAgent
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core import ChatPromptTemplate

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

        for buildParam in taskData.BuildParameters:
            if buildParam.Name == "server":
                llm_server = buildParam.Value
            if buildParam.Name == "model":
                selected_model = buildParam.Value
            if buildParam.Name == "verbose":
                debug_output = buildParam.Value

        llama = Ollama(
            temperature=0,
            verbose=debug_output,
            model=selected_model,
            #base_url= "https://xbbwlp7h-11434.use.devtunnels.ms",
            base_url=llm_server,
            #base_url= "http://localhost:11434"
        )


        chat_text_qa_msgs = [
            ChatMessage(
                role=MessageRole.SYSTEM,
                content=(
                    "Your are a helpful AI assistant designed to help answer questions. Please be as thorough as possible, when possible format the output as a list"
                ),
            ),
            ChatMessage(role=MessageRole.USER, content=taskData.args.get_arg("question")),
        ]
        text_qa_template = ChatPromptTemplate(chat_text_qa_msgs)

        # tool = FunctionTool.from_defaults(
        #     get_callback_by_uuid,
        #     async_fn=get_callback_by_uuid_async,
        #     name="GetCallbackByUUID",
        #     description="Finds a specific callback by its agent_callback_id (UUID)"

        # )

        mythic_spec = MythicRPCSpec(scope=taskData.Callback.AgentCallbackID, operation_id=taskData.Callback.OperationID)
        agent = ReActAgent.from_tools(mythic_spec.to_tool_list(), llm=llama, verbose=True)
        #chat_response = await agent.achat(taskData.args.get_arg("question"))
        chat_response = await agent.aquery(text_qa_template)
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
