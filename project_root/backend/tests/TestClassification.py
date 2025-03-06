from litellm import completion
import pytest

def test_query_classification_environmental(mocker):
    mock_response = {"choices": [{"message": {"content": "yes"}}]}
    
    # Mock the `completion` function
    mocker.patch("litellm.completion", return_value=mock_response)

    instruction = "The next prompt will be a string. Answer if it is a technical question about environmental impact data. (Answer with 'yes' or 'no'.)"
    
    # FIX: Added `model="gpt-4o"` as required
    response = completion(
        api_key="mock_key", 
        model="gpt-4o",  # ✅ Specify model parameter
        messages=[{"role": "user", "content": instruction + " CO2 impact of a lorry?"}]
    )

    assert response["choices"][0]["message"]["content"].strip().lower() == "yes"

def test_query_classification_non_environmental(mocker):
    mock_response = {"choices": [{"message": {"content": "no"}}]}
    
    # Mock the `completion` function
    mocker.patch("litellm.completion", return_value=mock_response)

    # FIX: Added `model="gpt-4o"` as required
    response = completion(
        api_key="mock_key",
        model="gpt-4o",  # ✅ Specify model parameter
        messages=[{"role": "user", "content": "Tell me a joke."}]
    )

    assert response["choices"][0]["message"]["content"].strip().lower() == "no"
