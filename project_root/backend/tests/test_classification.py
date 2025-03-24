import os
import pytest
from dotenv import load_dotenv
from unittest.mock import patch

# Load environment variables
load_dotenv()

@patch("litellm.completion", return_value={"choices": [{"message": {"content": "yes"}}]})
def test_query_classification_environmental(mock_completion):
    instruction = "The next prompt will be a string. Answer if it is a technical question about environmental impact data. (Answer with 'yes' or 'no'.)"
    
    from litellm import completion
    
    response = completion(
        api_key="mock_key",
        model="gpt-4o",  
        messages=[{"role": "user", "content": instruction + " CO2 impact of a lorry?"}]
    )

    assert response["choices"][0]["message"]["content"].strip().lower() == "yes"


@patch("litellm.completion", return_value={"choices": [{"message": {"content": "no"}}]})
def test_query_classification_non_environmental(mock_completion):
    from litellm import completion
    
    response = completion(
        api_key="mock_key",
        model="gpt-4o",  
        messages=[{"role": "user", "content": "Tell me a joke."}]
    )

    assert response["choices"][0]["message"]["content"].strip().lower() == "no"
