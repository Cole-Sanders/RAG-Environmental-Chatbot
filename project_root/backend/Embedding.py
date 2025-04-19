from dotenv import load_dotenv
load_dotenv()
from llama_index.core import Document
from llama_index.core import VectorStoreIndex, Settings, StorageContext, load_index_from_storage
import os
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


name_documents = []
with open("project_root/backend/NameData.txt", "r") as f:
    for line in f:
        line = line.strip()
        if line:
            doc = Document(text=line)
            name_documents.append(doc)



name_index_path = "project_root/backend/nameStorage"


if os.path.exists(name_index_path):  # Load existing index if present
    storage_context = StorageContext.from_defaults(persist_dir=name_index_path)
    name_index = load_index_from_storage(storage_context)
else:  # Create a new index and store it
    name_index = VectorStoreIndex.from_documents(name_documents, embed_model=Settings.embed_model)
    name_index.storage_context.persist(persist_dir=name_index_path)

name_query_engine = name_index.as_query_engine(return_source=True, similarity_top_k=10)


