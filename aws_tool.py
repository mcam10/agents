import os
import subprocess
from autogen import AssistantAgent, UserProxyAgent, ConversableAgent, config_list_from_json,register_function
from autogen.coding import LocalCommandLineCodeExecutor

from typing_extensions import Annotated

from pathlib import Path

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

file_path = Path("~/.aws/")

# Set the KUBECONFIG environment variable
# if the kubeconfig file is not in the default location(~/.kube/config).
os.environ["AWS_PROFILE"] = "sandbox-pmc"
os.environ["BUCKET"] = "vip-bucket-sandbox-test"

llm_config = {
    "temperature": 0,
    "config_list": config_list,
}

if file_path.exists():
    print("AWS folder existd!")
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
    system_message="You are a helpful AI assistant"
    "Return 'TERMINATE' when the task is done.",
)

@engineer.register_for_execution()
@assistant.register_for_llm(description="Getting credential Information for current AWS User")
def get_credential_info () -> any:
    result = subprocess.run(["aws", "sts", "get-caller-identity"], capture_output=True, text=True)
    return result.stdout

@engineer.register_for_execution()
@assistant.register_for_llm(description="Get AWS Account configuration")
def get_configuration() -> any:
    result = subprocess.run(["aws", "configure", "get", "sandbox-pmc.aws_access_key_id"], capture_output=True, text=True)
    return result.stdout

@engineer.register_for_execution()
@assistant.register_for_llm(description="List all s3 buckets")
def list_objects_in_account():
    result = subprocess.run(["aws", "s3api", "list-buckets", "|", "jq", "-r", ".'Buckets[].Name'"], capture_output=True, text=True)
    return result.stdout

@engineer.register_for_execution()
@assistant.register_for_llm(description="Check if versioning is enabled for specified Bucket")
def versioning_enabled(
    bucket: Annotated[str, "Bucket Name"],
)    -> any:
    result = subprocess.run(["aws", "s3api", "get-bucket-versioning","--bucket", bucket], capture_output=True, text=True)
    return result.stdout

@engineer.register_for_execution()
@assistant.register_for_llm(description="List Cloudtrail events")
def get_aws_cloudtrail_events(description="Get the last 10 cloudtrail events") -> any:
    result = subprocess.run(["aws","cloudtrail", "lookup-events" "--max-items", "10"], capture_output=True, text=True)
    return result.stdout

@engineer.register_for_execution()
@assistant.register_for_llm(description="Get running EC2 instances")
def get_running_ec2_instances() -> any:
    result = subprocess.run(["aws","ec2", "describe-instances" "--filters", "Name=tag-key, Values=Name", "--query", "'Reservations[*].Instances[*].{Instance:InstanceId,AZ:Placement.AvailabilityZone,Name:Tags[?Key==`Name`]|[0].Value}'", "--output", "table" ], capture_output=True, text=True)
    return result.stdout


function_map={
        "list_objects_in_account": list_objects_in_account,
        "get_credential_info": get_credential_info,
        "get_configuration":  get_configuration,
}

chat_result = engineer.initiate_chat(assistant, message="What is my AWS credential info?")
