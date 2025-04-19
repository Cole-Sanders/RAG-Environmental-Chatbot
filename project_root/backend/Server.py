from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from Embedding import data_query_engine  # Import the query engine from index_builder
from Embedding import name_query_engine  # Import the query engine from index_builder

# Initialize FastAPI
app = FastAPI()

# Define the request format
class QueryRequest(BaseModel):
    query: str

# API endpoint to query the vectorized index
@app.post("/namequery")
async def query_index(request: QueryRequest):
    response = name_query_engine.query(request.query)
    result = "Processes:\n"
    for node in response.source_nodes:
        result += str(node.node.text) + "\n"
    return {"response": result}

@app.post("/locationquery")
async def query_index(request: QueryRequest):
    response = name_query_engine.query(request.query)
    return {"response": str(response)}

# Run the FastAPI server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)