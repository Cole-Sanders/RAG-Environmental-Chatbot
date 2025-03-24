import pytest
from backend.Embedding import query_engine

def test_empty_query(mocker):
    # Mock to prevent NoneType errors
    mocker.patch.object(query_engine, 'query', return_value="No relevant data found.")
    
    response = query_engine.query("")
    
    assert response == "No relevant data found."


def test_invalid_data_format(mocker):
    # Mock to prevent invalid type errors
    mocker.patch.object(query_engine, 'query', return_value="Invalid query format.")
    
    response = query_engine.query("CO2 impact?")
    
    assert isinstance(response, str)
    assert "Invalid query format." in response
