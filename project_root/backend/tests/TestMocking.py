import pytest
from litellm import completion

def test_openai_api_call(mocker):
    mock_response = {
        "choices": [{"message": {"content": "The CO2 impact of a lorry is 11644.86 kg CO2 eq."}}]
    }
    mocker.patch("litellm.completion", return_value=mock_response)

    response = completion(api_key="mock_key", messages=[{"role": "user", "content": "CO2 impact of a lorry?"}])
    
    assert response["choices"][0]["message"]["content"] == "The CO2 impact of a lorry is 11644.86 kg CO2 eq."
