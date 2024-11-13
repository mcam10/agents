import os
import subprocess
from autogen import AssistantAgent, UserProxyAgent, ConversableAgent, config_list_from_json,register_function
from autogen.coding import LocalCommandLineCodeExecutor

from typing_extensions import Annotated

from pathlib import Path

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

file_path = Path("~/.aws")

if file_path.exists():
    print("AWS folder existd!")
else:
    print("AWS folder does not exist.")


def get_credential_info():
    result = subprocess.run(["aws", "sts", "get-caller-identity"], capture_output=True, text=True)
    return result.stdout

def list_objects_in_account():
    result = subprocess.run(["aws", "s3", "ls"], capture_output=True, text=True)
    return result.stdout

def versioning_enabled(BUCKET:str) -> any:
    result = subprocess.run(["aws", "s3api", "get-bucket-versioning","--bucket",BUCKET], capture_output=True, text=True)
    return result.stdout

llm_config = {
    "temperature": 0,
    "config_list": config_list,
}

function_map={
        "list_objects_in_account": list_objects_in_account,
        "get_credential_info": get_credential_info,
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
    llm_config=llm_config ,
    system_message="You are a helpful AI assistant"
    "Return 'TERMINATE' when the task is done.",
)

register_function(
    list_objects_in_account,
    caller=assistant,  # The assistant agent can suggest calls to the S3 account lister.
    executor=engineer,  # The engineer agent can execute the s3 calls.
    description="AWS Actions Agent",  # A description of the tool.
)

register_function(
    get_credential_info,
    caller=assistant,  # The assistant agent can suggest calls to the S3 account lister.
    executor=engineer,  # The engineer agent can execute the s3 calls.
    description="AWS credential info",  # A description of the tool.
)

chat_result = engineer.initiate_chat(assistant, message="Get credential info")
#chat_result = engineer.initiate_chat(assistant, message="List S3 buckets in Account")
