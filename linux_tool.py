import os
import subprocess
from autogen import AssistantAgent, UserProxyAgent, ConversableAgent, config_list_from_json,register_function 
from autogen.coding import LocalCommandLineCodeExecutor
from typing_extensions import Annotated

from pathlib import Path

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

llm_config = {
    "temperature": 0,
    "config_list": config_list,
}

engineer = ConversableAgent(
    name="Engineer",
    llm_config=False,
    is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
    human_input_mode="NEVER",
)

assistant = ConversableAgent(
    name="Assistant",
    code_execution_config=False,
    llm_config=llm_config,
    system_message="You are a helpful AI assistant"
    "Return 'TERMINATE' when the task is done.",
)

@engineer.register_for_execution()
@assistant.register_for_llm(description="Listing directy contents no additional args")
def list_directory_contents() -> any:
    result = subprocess.run(["ls"], capture_output=True, text=True)
    return result.stdout

chat_result = engineer.initiate_chat(assistant, message="List current directory contents ")
