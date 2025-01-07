import os
import subprocess
from autogen import AssistantAgent, UserProxyAgent, ConversableAgent, config_list_from_json,register_function
from autogen.coding import LocalCommandLineCodeExecutor

from typing_extensions import Annotated

from pathlib import Path

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

file_path = Path("/Users/mcameron/.aws/")

AWS_PROFILE = os.environ.get('AWS_PROFILE', 'default')

aws_admin_tasks = ["""Develop a summary using the tools and information provided."""]

llm_config = {
    "temperature": 0,
    "config_list": config_list,
}

if os.path.exists(file_path):
    print("AWS folder exists!")
else:
    print("AWS folder does not exist.")

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
    system_message="""
        You are a Assistant Agent using the information and tools
        provided to summarize what is happening in the enviornment you run in
        Return 'TERMINATE' when the task is done.
        """,
)

## This should probably be captain agent -> My AI right hand man.
config_agent = AssistantAgent(
    name="Config Agent",
    llm_config=llm_config,
    system_message="""Config Agent. You hold all the configuration data. You hold information regarding the current credentials and their access. You don't write code.""",
)

## This will summarize the account and pass this to a captain agent to manage the agents
@assistant.register_for_llm(description="Getting credential Information for current AWS User")
def summarize_account() -> any:
    result = subprocess.run(["aws", "sts", "get-caller-identity"], capture_output=True, text=True)
    pass

@engineer.register_for_execution()
@assistant.register_for_llm(description="Getting EC2 instance information for current AWS User")
def describe_ec2_instances () -> any:
    result = subprocess.run(["aws", "ec2", "describe-instances"], capture_output=True, text=True)
    return result.stdout

@engineer.register_for_execution()
@assistant.register_for_llm(description="Listing all s3 buckets")
def list_buckets_in_account() -> any:
    result = subprocess.run(["aws", "s3", "ls", "--output=json"], capture_output=True, text=True)
    return result.stdout

@engineer.register_for_execution()
@assistant.register_for_llm(description="Check if versioning is enabled for specified Bucket")
def versioning_enabled(
    bucket: Annotated[str, "Bucket Name"],
)    -> any:
    result = subprocess.run(["aws", "s3api", "get-bucket-versioning","--bucket", bucket], capture_output=True, text=True)
    return result.stdout

@engineer.register_for_execution()
@assistant.register_for_llm(description="Spin up a EC2 instance of type g6e.xlarge with a text file script")
## Dont know if this works yet. havent tested the formatting
## This should spin an instance and report some 200 if success, if not why not.. param failure or lack of perms
def get_aws_cloudtrail_events(description="Get the last 10 cloudtrail events") -> any:
    result = subprocess.run(["aws ec2 run-instances --image-id ami-0cdc56cf41c025c96
    --count 1 --instance-type g6e.xlarge \
    --key-name malik --subnet-id subnet-068b74a790daabba1 --security-group-ids sg-06c6b3178aacfd4bd \
    --user-data file://my_script.txt"
    ], capture_output=True, text=True)
    return result.stdout

@engineer.register_for_execution()
@assistant.register_for_llm(description="Get running EC2 instances")
def get_running_ec2_instances() -> any:
    result = subprocess.run(["aws","ec2", "describe-instances" "--filters", "Name=tag-key, Values=Name", "--query", "'Reservations[*].Instances[*].{Instance:InstanceId,AZ:Placement.AvailabilityZone,Name:Tags[?Key==`Name`]|[0].Value}'", "--output", "table" ], capture_output=True, text=True)
    return result.stdout


## lets initiate another chat to get a ending review or summary of the accounts after the agents take action
'''
chat_result = engineer.initiate_chats(
    [

     {
             "recipient": assistant, 
             "message": "List all the s3 buckets",
             "summary_method": "reflection_with_llm",
    },
    {
             "recipient": assistant, 
             "message":  "Summarize this AWS Account",
             "summary_method": "last_msg",
    },
  ]
)
'''
## Good to verify in a workflow of the types of permissions one has access to do
print(assistant.llm_config['tools'])


