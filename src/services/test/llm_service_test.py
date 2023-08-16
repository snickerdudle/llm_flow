"""Test for the LLM Service"""

import unittest
from unittest.mock import patch, MagicMock

from src.services.llm_service import LLMService, LLMPromptFormatter


class LLMPromptFormatterTest(unittest.TestCase):
    """Test for the LLM Service"""

    def setUp(self) -> None:
        self.api_key = "sample_api_key"
        self.llm_formatter = LLMPromptFormatter(self.api_key)

    def test_api_key(self):
        self.assertEqual(self.llm_formatter.api_key, self.api_key)

    def test_formatLLMPrompt(self):
        """Test the formatLLMPrompt function"""
        self.assertEqual(self.llm_formatter.formatLLMPrompt("test"), "test")

        self.assertEqual(
            self.llm_formatter.formatLLMPrompt(
                "Say {name}!", {"name": "hello"}
            ),
            "Say hello!",
        )

        self.assertRaises(
            KeyError,
            self.llm_formatter.formatLLMPrompt,
            "Say {name}!",
            {"name": "hello", "test": "test"},
        )

    @patch("src.services.llm_service.OpenAI")
    def test_getLLMResponse(self, MockOpenAI):
        """Test the getLLMResponse function"""
        expected_return = "Hello there!"

        instance = MockOpenAI.return_value
        instance.return_value = expected_return

        llm_formatter = LLMPromptFormatter(self.api_key)

        self.assertEqual(
            llm_formatter.getLLMResponse("How are you?"), expected_return
        )


class LLMServiceTest(unittest.TestCase):
    @patch("src.services.llm_service.os.environ.get")
    @patch("src.services.llm_service.OpenAI")
    def test_end_to_end_functionality(self, MockOpenAI, environ_get_method):
        """Test the end to end functionality of the LLM Service"""
        name = "General Kenobi"
        prompt = "Say hello there, {name}"
        expected_response = f"Hello there, {name}!"

        instance = MockOpenAI.return_value
        instance.return_value = expected_response

        environ_get_method.return_value = "sample_api_key"

        llm_service = LLMService()

        result = llm_service.get_llm_response(prompt, {"name": name})

        self.assertEqual(result, expected_response)
