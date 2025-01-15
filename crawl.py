import asyncio
from crawl4ai import *
import autogen
from autogen import AssistantAgent, config_list_from_json
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from chromadb.utils import embedding_functions
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer


config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

llm_config = {
    "temperature": 0,
    "config_list": config_list,
}

#Data source to load LLM -> Beginnings of Rag
url = "https://awscli.amazonaws.com/v2/documentation/api/latest/index.html"

assistant = AssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant.",
    llm_config=llm_config,
)

ragproxyagent = RetrieveUserProxyAgent(
    name="ragproxyagent",
    retrieve_config={
        "task": "qa",
        "docs_path": [
           "https://awscli.amazonaws.com/v2/documentation/api/latest/index.html" 
        ],
        "custom_text_split_function": recur_spliter.split_text,
        "custom_text_types": ["non-existent-type"],
        "chunk_token_size": 2000,
        "model": config_list[0]["model"],
        "vector_db": "mongodb",
        "collection_name": "aws",
        "db_config": {
            "connection_string": ""
            "database_name": "mongodb",
            "index_name": "vector_index",
            "wait_until_index_ready": 120.0,  # Setting to wait 120 seconds or until index is constructed before querying
            "wait_until_document_ready": 120.0,  # Setting to wait 120 seconds or until document is properly indexed after insertion/update
        },
        "get_or_create": True,
        "overwrite": True,
    },
)

#assistant.reset()
ragproxyagent.initiate_chat(assistant, message=ragproxyagent.message_generator, problem="What is the AWS CLI?")
# userproxyagent = autogen.UserProxyAgent(name="userproxyagent")
# userproxyagent.initiate_chat(assistant, message="What is the AWS CLI?")



