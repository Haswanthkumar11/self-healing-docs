from unittest.mock import MagicMock, patch

import pytest

from src.ai.llm_client import GeminiClient


@patch("src.ai.llm_client.genai.Client")
def test_gemini_can_explain_a_python_function(mock_client_class):
    # Simulate the Gemini client without calling the real API.
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    mock_response = MagicMock()
    mock_response.text = (
        "The multiply function takes two arguments and returns their product."
    )

    mock_client.models.generate_content.return_value = mock_response

    client = GeminiClient()
    response = client.generate("Explain the multiply function.")

    assert "multiply" in response.lower()
    assert "product" in response.lower()

    mock_client.models.generate_content.assert_called_once_with(
        model=client.model,
        contents="Explain the multiply function.",
    )


def test_empty_prompt_is_rejected():
    with patch("src.ai.llm_client.genai.Client"):
        client = GeminiClient()

    with pytest.raises(ValueError, match="Prompt must not be empty"):
        client.generate("   ")