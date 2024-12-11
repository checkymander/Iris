from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from langchain_community.embeddings import HuggingFaceEmbeddings
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from huggingface_hub import hf_hub_download
from llama_index.core import set_global_tokenizer
import torch


class Iris(PayloadType):
    name = "iris"
    file_extension = ""
    author = "@checkymander"
    supported_os = [
        SupportedOS("iris")
    ]
    wrapper = False
    wrapped_payloads = []
    note = """
    This payload allows you to ask questions about your current operation
    """
    supports_dynamic_loading = False
    mythic_encrypts = True
    translation_container = None
    agent_type = "service"
    agent_path = pathlib.Path(".") / "iris" / "mythic"
    agent_code_path = pathlib.Path(".") / "iris"  / "agent_code"
    agent_icon_path = agent_path / "agent_functions" / "iris.svg"
    build_steps = [
        BuildStep(step_name="Download LLM", step_description="Downloading LLM"),
        BuildStep(step_name="Download Embeddings", step_description="Downloading Embedding model"),
        BuildStep(step_name="Download Reranker", step_description="Downloading Reranker model"),
        BuildStep(step_name="Start Agent", step_description="Starting agent callback"),
    ]
    build_parameters = [
        BuildParameter(
            name="api_key",
            parameter_type=BuildParameterType.String,
            default_value="",
            description="Google Studio API Key"
        ),
        # BuildParameter(
        #     name="server",
        #     parameter_type=BuildParameterType.String,
        #     default_value="http://localhost:11434",
        #     description="OpenAI Compatible LLM Server"
        # ),
        # BuildParameter(
        #     name="verbose",
        #     parameter_type=BuildParameterType.Boolean,
        #     default_value=False,
        #     description="Enable verbose output in Docker container"
        # ),
        # BuildParameter(
        #     name="model",
        #     parameter_type=BuildParameterType.String,
        #     default_value="llama3:instruct",
        #     description="The model to use"
        # )
    ]
    c2_profiles = []
    async def build(self) -> BuildResponse:
        # this function gets called to create an instance of your payload
        resp = BuildResponse(status=BuildStatus.Success)
        ip = "127.0.0.1"
        create_callback = await SendMythicRPCCallbackCreate(MythicRPCCallbackCreateMessage(
            PayloadUUID=self.uuid,
            C2ProfileName="",
            User="iris",
            Host="iris",
            Ip=ip,
            IntegrityLevel=3,
        ))
        if not create_callback.Success:
            await SendMythicRPCPayloadUpdatebuildStep(MythicRPCPayloadUpdateBuildStepMessage(
                PayloadUUID=self.uuid,
                StepName="Start",
                StepStdout=f"Failed to start Agent: {create_callback.Error}",
                StepSuccess=False
            )) 
            logger.info(create_callback.Error)
        else:
            await SendMythicRPCPayloadUpdatebuildStep(MythicRPCPayloadUpdateBuildStepMessage(
                PayloadUUID=self.uuid,
                StepName="Start Agent",
                StepStdout="Agent started!",
                StepSuccess=True
            )) 
            logger.info(create_callback.CallbackUUID)
        return resp