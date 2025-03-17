from fastapi.testclient import TestClient
from backend.Server import app 
import os
import pytest
from backend.Embedding import reader

@pytest.fixture(scope="session", autouse=True)
def set_test_data_path():
    """ Ensure the test environment resolves the correct path for Data.json """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Current test directory
    TEST_DATA_PATH = os.path.join(BASE_DIR, "..", "Data.json")  # Adjust path
    reader.load_data(input_file=TEST_DATA_PATH, extra_info={})  # Force load with correct path


client = TestClient(app)

def test_api_query_success(mocker):
    mock_response = {"response": "The CO2 impact is 11644.86 kg CO2 eq."}
    mocker.patch("backend.Embedding.query_engine.query", return_value=mock_response["response"])
    
    response = client.post("/query", json={"query": "CO2 impact of 28-ton lorry?"})
    
    assert response.status_code == 200
    assert response.json() == mock_response

def test_api_query_failure():
    response = client.post("/query", json={})  # Missing query field
    assert response.status_code == 422  # Unprocessable Entity
