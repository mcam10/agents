import os
import subprocess
from autogen import AssistantAgent, UserProxyAgent,config_list_from_json,register_function

from typing_extensions import Annotated

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")


llm_config = {
    "temperature": 0,
    "config_list": config_list,
}

engineer = AssistantAgent(
    name="Engineer",
    llm_config=llm_config,
    system_message="""
    I'm Engineer. I'm expert in bash programming. I'm executing code tasks required by Admin.
    """,
)

user_proxy = UserProxyAgent(
    name="Admin",
    human_input_mode="ALWAYS",
    code_execution_config=False,
    is_termination_msg=lambda x: x.get("content", "") is not None and "terminate" in x["content"].lower(),
    default_auto_reply="Please continue if not finished, otherwise return 'TERMINATE'.",
)

#### prepare appropiate functions

def list_objects_in_account(directory: Annotated[str, "AWS Account to check"]):
    subprocess.run(["aws","s3","ls"], shell=True)

#Register the function with the agents

engineer.register_for_llm(name="list_objects_in_account",description="List buckets",(list_objects_in_account)
user_proxy_agent.register_for_execution(name="list_objects_in_account",description="List buckets",(list_objects_in_account)

chat_result = user_proxy.initiate_chat(engineer, message="List AWS S3 buckets")
