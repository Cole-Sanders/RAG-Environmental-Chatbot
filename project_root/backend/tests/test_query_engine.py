import pytest
from backend.Embedding import query_engine
import os
import pytest
from backend.Embedding import reader

@pytest.fixture(scope="session", autouse=True)
def set_test_data_path():
    """ Ensure the test environment resolves the correct path for Data.json """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Current test directory
    TEST_DATA_PATH = os.path.join(BASE_DIR, "..", "Data.json")  # Adjust path
    reader.load_data(input_file=TEST_DATA_PATH, extra_info={})  # Force load with correct path


def test_query_engine_valid_query(mocker):
    mocker.patch.object(query_engine, 'query', return_value="The CO2 impact is 11644.86 kg CO2 eq.")
    
    response = query_engine.query("What is the CO2 impact of a 28-ton lorry?")
    
    assert response == "The CO2 impact is 11644.86 kg CO2 eq."

def test_query_engine_invalid_query(mocker):
    mocker.patch.object(query_engine, 'query', return_value="No relevant data found.")
    
    response = query_engine.query("What is the CO2 impact of a spaceship?")
    
    assert response == "No relevant data found."
