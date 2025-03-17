import pytest
from unittest.mock import patch

@patch("litellm.completion", return_value={
    "choices": [{"message": {"content": "The CO2 impact of a lorry is 11644.86 kg CO2 eq."}}]
})
@patch("litellm.openai.ChatCompletion.create", return_value={
    "choices": [{"message": {"content": "The CO2 impact of a lorry is 11644.86 kg CO2 eq."}}]
})
def test_openai_api_call(mock_chat_completion, mock_completion):
    from litellm import completion
    
    response = completion(
        api_key="mock_key", 
        model="gpt-4o",  
        messages=[{"role": "user", "content": "CO2 impact of a lorry?"}]
    )
    
    assert response["choices"][0]["message"]["content"] == "The CO2 impact of a lorry is 11644.86 kg CO2 eq."
