import os
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager,config_list_from_json
from typing_extensions import Annotated

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

default_path = "/Users/mcameron/pmc-infra/chart-api/"

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
)

## setup groupchat

groupchat = GroupChat(
    agents=[engineer, user_proxy],
    messages=[],
    max_round=500,
    speaker_selection_method="round_robin",
    enable_clear_history=True,
)

manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

#### prepare appropiate functions

@user_proxy.register_for_execution()
@engineer.register_for_llm(description="List files in choosen directory.")
def list_dir(directory: Annotated[str, "Directory to check."]):
    files = os.listdir(default_path + directory)
    return 0, files

@user_proxy.register_for_execution()
@engineer.register_for_llm(description="Check the contents of a chosen file.")
def see_file(filename: Annotated[str, "Name and path of file to check."]):
    with open(default_path + filename, "r") as file:
        lines = file.readlines()
    formatted_lines = [f"{i+1}:{line}" for i, line in enumerate(lines)]
    file_contents = "".join(formatted_lines)

    return 0, file_contents

@user_proxy.register_for_execution()
@engineer.register_for_llm(description="Replace old piece of code with new one. Proper indentation is important.")
def modify_code(
    filename: Annotated[str, "Name and path of file to change."],
    start_line: Annotated[int, "Start line number to replace with new code."],
    end_line: Annotated[int, "End line number to replace with new code."],
    new_code: Annotated[str, "New piece of code to replace old code with. Remember about providing indents."],
):
    with open(default_path + filename, "r+") as file:
        file_contents = file.readlines()
        file_contents[start_line - 1 : end_line] = [new_code + "\n"]
        file.seek(0)
        file.truncate()
        file.write("".join(file_contents))
    return 0, "Code modified"


@user_proxy.register_for_execution()
@engineer.register_for_llm(description="Create a new file with code.")
def create_file_with_code(
    filename: Annotated[str, "Name and path of file to create."], code: Annotated[str, "Code to write in the file."]
):
    with open(default_path + filename, "w") as file:
        file.write(code)
    return 0, "File created successfully"


chat_result = user_proxy.initiate_chat(
    manager,
    message="""
You will need to improve app in Github Actions. For now, check out all the application files, try to understand it and wait for next instructions.
""",
)
