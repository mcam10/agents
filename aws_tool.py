import os
import subprocess
from autogen import AssistantAgent, UserProxyAgent, ConversableAgent, config_list_from_json,register_function
from autogen.coding import LocalCommandLineCodeExecutor

from typing_extensions import Annotated

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

def list_objects_in_account():
    command = subprocess.run(["ls"], shell=True,capture_output=True)
    return command.stdout


executor = LocalCommandLineCodeExecutor(
    timeout=10,  # Timeout for each code execution in seconds.
    functions = [list_objects_in_account],
)


llm_config = {
    "temperature": 0,
    "config_list": config_list,
}

engineer = AssistantAgent(
    name="Engineer",
    llm_config=llm_config,
    code_execution_config ={"executor":executor},
)

user_proxy = ConversableAgent(
    name="Admin",
    human_input_mode="ALWAYS",
    code_execution_config=False,
    is_termination_msg=lambda x: x.get("content", "") is not None and "terminate" in x["content"].lower(),
    default_auto_reply="Please continue if not finished, otherwise return 'TERMINATE'.",
)

#### prepare appropiate functions

#Register the function with the agents

engineer.register_for_llm(name="list_objects_in_account",description="List buckets")(list_objects_in_account)

user_proxy.register_for_execution(name="list_objects_in_account")(list_objects_in_account)
engineer.register_for_execution(name="list_objects_in_account")(list_objects_in_account)

chat_result = user_proxy.initiate_chat(engineer, message="List AWS S3 buckets")
