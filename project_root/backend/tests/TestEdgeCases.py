import pytest
from backend.Embedding import query_engine

def test_empty_query():
    response = query_engine.query("")
    assert response == "No relevant data found."

def test_invalid_data_format(mocker):
    mocker.patch.object(query_engine, 'query', return_value={"invalid": "response"})
    
    response = query_engine.query("CO2 impact?")
    
    assert isinstance(response, dict)  # Should not be a dict, expected string
    assert "invalid" in response
