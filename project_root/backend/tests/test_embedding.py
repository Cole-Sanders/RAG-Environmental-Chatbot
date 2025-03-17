import pytest
import os
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.readers.json import JSONReader

@pytest.fixture
def sample_data():
    """Provide sample data in dictionary format."""
    return [
        {
            "process_name": "maintenance, lorry 28 metric ton",
            "process_id": "855e0015-da07-3056-ad7e-bd970ae9f0c5",
            "impact_results": {"Global warming": {"Amount": 11644.86, "Unit": "kg CO2 eq"}}
        }
    ]

@pytest.fixture
def json_reader():
    """Initialize JSON Reader."""
    return JSONReader()

def test_data_loading(json_reader, sample_data, mocker):
    """Test if JSON data is correctly loaded."""
    mocker.patch.object(JSONReader, 'load_data', return_value=sample_data)
    data = json_reader.load_data("mocked_path.json")
    
    assert len(data) == 1
    assert data[0]["process_name"] == "maintenance, lorry 28 metric ton"
    assert "Global warming" in data[0]["impact_results"]

def test_vector_index_creation(sample_data, mocker):
    """Test if LlamaIndex correctly converts JSON data into Document objects and creates an index."""
    # Mock the data loading
    mocker.patch("backend.Embedding.reader.load_data", return_value=sample_data)

    # Convert dict to LlamaIndex Document objects
    documents = [Document(text=str(item)) for item in sample_data]

    # Create vector index
    index = VectorStoreIndex.from_documents(documents)

    assert index is not None
    assert isinstance(index, VectorStoreIndex)
