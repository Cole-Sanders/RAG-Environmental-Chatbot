from dotenv import load_dotenv

load_dotenv()
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings, StorageContext, load_index_from_storage
from llama_index.llms.openai import OpenAI
from llama_index.core.readers.json import JSONReader
import os
from llama_index.core.tools import QueryEngineTool
from llama_index.core.agent import ReActAgent

from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
from llama_index.llms.litellm import LiteLLM

# changing the global default
Settings.embed_model = OpenAIEmbedding(model="text-embedding-ada-002",
                                       api_key=os.getenv("API_KEY"),
                                       api_base="http://18.216.253.243:4000/")
Settings.llm = LiteLLM(model="gpt-3.5-turbo",
                                       api_key=os.getenv("API_KEY"),
                                       api_base="http://18.216.253.243:4000/")

# Initialize JSONReader
reader = JSONReader()

# Load data from JSON file
documents = reader.load_data(input_file="project_root/backend/data/Data.json", extra_info={})

# Create or Load the Index
index_path = "project_root/backend/storage"

if os.path.exists(index_path):  # Load existing index if present
    storage_context = StorageContext.from_defaults(persist_dir=index_path)
    index = load_index_from_storage(storage_context)
else:  # Create a new index and store it
    index = VectorStoreIndex.from_documents(documents, embed_model=Settings.embed_model)
    index.storage_context.persist(persist_dir=index_path)

query_engine = index.as_query_engine()

response = query_engine.query(
    "What was acidification of electricty?"
)
print(response)