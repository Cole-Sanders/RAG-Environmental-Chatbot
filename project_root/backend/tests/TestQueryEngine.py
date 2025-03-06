import pytest
from backend.Embedding import query_engine

def test_query_engine_valid_query(mocker):
    mocker.patch.object(query_engine, 'query', return_value="The CO2 impact is 11644.86 kg CO2 eq.")
    
    response = query_engine.query("What is the CO2 impact of a 28-ton lorry?")
    
    assert response == "The CO2 impact is 11644.86 kg CO2 eq."

def test_query_engine_invalid_query(mocker):
    mocker.patch.object(query_engine, 'query', return_value="No relevant data found.")
    
    response = query_engine.query("What is the CO2 impact of a spaceship?")
    
    assert response == "No relevant data found."
