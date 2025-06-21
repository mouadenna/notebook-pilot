from langchain_openai import ChatOpenAI
import json
from azure.core.credentials import AzureKeyCredential

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

# Initialize LLM
llm = ChatOpenAI(
    api_key=config['apiKey'],
    model=config['model'],
    base_url=config['baseURL'],
    temperature=0.1
)



