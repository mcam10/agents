import os
import subprocess
from autogen import AssistantAgent, UserProxyAgent, ConversableAgent, config_list_from_json,register_function
from autogen.coding import LocalCommandLineCodeExecutor

from typing_extensions import Annotated

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

def list_objects_in_account():
    command = subprocess.run(["ls"])
    return command

executor = LocalCommandLineCodeExecutor(
    timeout=10,  # Timeout for each code execution in seconds.
    functions=[list_objects_in_account],  # Use the temporary directory to store the code files.
)


llm_config = {
    "temperature": 0,
    "config_list": config_list,
}

engineer = ConversableAgent(
    name="Engineer",
    llm_config=False,
    code_execution_config ={"executor":executor},
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

#### prepare appropiate functions

#Register the function with the agents

#assistant.register_for_llm(name="list_objects_in_account",description="List buckets")(list_objects_in_account)

#user_proxy.register_for_execution(name="list_objects_in_account")(list_objects_in_account)
#engineer.register_for_execution(name="list_objects_in_account")(list_objects_in_account)

register_function(
    list_objects_in_account,
    caller=assistant,  # The assistant agent can suggest calls to the calculator.
    executor=engineer,  # The engineer agent can execute the calculator calls.
    name="list_objects_in_account",  # By default, the function name is used as the tool name.
    description="Listerr",  # A description of the tool.
)

chat_result = engineer.initiate_chat(assistant, message="List AWS S3 buckets")
