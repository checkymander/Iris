from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from .helpers.tools.MythicRPCSpec import MythicRPCSpec
from llama_index.llms.ollama import Ollama
from llama_index.core.agent import ReActAgent
from llama_index.core import PromptTemplate

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

        react_system_header_str = """\

You are designed to help with a variety of tasks, from answering questions \
    to providing summaries to other types of analyses.

## Tools
You have access to a wide variety of tools. You are responsible for using
the tools in any sequence you deem appropriate to complete the task at hand.
This may require breaking the task into subtasks and using different tools
to complete each subtask.

You have access to the following tools:
{tool_desc}

## Output Format
To answer the question, please use the following format.

```
Thought: I need to use a tool to help me answer the question.
Action: tool name (one of {tool_names}) if using a tool.
Action Input: the input to the tool, in a JSON format representing the kwargs (e.g. {{"input": "hello world", "num_beams": 5}})
```

Please ALWAYS start with a Thought.

Please use a valid JSON format for the Action Input. Do NOT do this {{'input': 'hello world', 'num_beams': 5}}.

If this format is used, the user will respond in the following format:

```
Observation: tool response
```

You should run the minimum number of tools until you have enough information to answer the question or an error is 
thrown by a tool you need to use. At that point, you MUST respond in the one of the following two formats:

```
Thought: I can answer without using any more tools.
Answer: [your answer here]
```

```
Thought: I cannot answer the question with the provided tools.
Answer: [The toolname that errored and the error message]
```

## Additional Rules
- The answer MUST contain a sequence of bullet points that explain how you arrived at the answer. This can include aspects of the previous conversation history.
- You MUST obey the function signature of each tool. Do NOT pass in no arguments if the function expects arguments.
- Do not get task output or file contents unless specifically requested by the human
- Stop running tools on an error and let the user know
- All Agent ID's should be in a UUID format provided by either the user or mapped via map_callback_number_to_agent_callback_id
- Callback and Agent can be used interchangeably and refers to agent_callback_id

## Current Conversation
Below is the current conversation consisting of interleaving human and assistant messages.

"""
        react_system_prompt = PromptTemplate(react_system_header_str)
        mythic_spec = MythicRPCSpec(scope=taskData.Callback.AgentCallbackID, operation_id=taskData.Callback.OperationID,debug=debug_output)
        agent = ReActAgent.from_tools(mythic_spec.to_tool_list(), llm=llama, verbose=True)
        agent.update_prompts({"agent_worker:system_prompt": react_system_prompt})
        agent.reset()
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
