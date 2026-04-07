"""Tests for LLM-based claim extraction (mocked)."""
import json
import pytest
from unittest.mock import patch
from contrachecker.models import Chunk
from contrachecker.extractors.llm_extractor import LLMExtractor


@pytest.fixture
def mock_openai_response():
    return {
        "claims": [
            {"subject": "metformin", "relation": "is", "object": "first-line treatment for type 2 diabetes"},
            {"subject": "metformin", "relation": "reduces", "object": "blood glucose levels"},
        ]
    }


class TestLLMExtractor:
    def test_extract_parses_llm_response(self, mock_openai_response):
        with patch("contrachecker.extractors.llm_extractor._call_llm") as mock_call:
            mock_call.return_value = json.dumps(mock_openai_response)
            extractor = LLMExtractor(api_key="test-key")
            chunk = Chunk(id="c1", text="Metformin is the first-line treatment for type 2 diabetes.")
            claims = extractor.extract(chunk)
            assert len(claims) == 2
            assert claims[0].subject == "metformin"
            assert claims[0].source_chunk_id == "c1"

    def test_extract_many_batches(self, mock_openai_response):
        with patch("contrachecker.extractors.llm_extractor._call_llm") as mock_call:
            mock_call.return_value = json.dumps(mock_openai_response)
            extractor = LLMExtractor(api_key="test-key")
            chunks = [
                Chunk(id="c1", text="Text one."),
                Chunk(id="c2", text="Text two."),
            ]
            claims = extractor.extract_many(chunks)
            assert len(claims) == 4
            assert mock_call.call_count == 2

    def test_handles_malformed_response(self):
        with patch("contrachecker.extractors.llm_extractor._call_llm") as mock_call:
            mock_call.return_value = "not valid json {"
            extractor = LLMExtractor(api_key="test-key")
            chunk = Chunk(id="c1", text="Some text.")
            claims = extractor.extract(chunk)
            assert claims == []

    def test_handles_empty_claims_list(self):
        with patch("contrachecker.extractors.llm_extractor._call_llm") as mock_call:
            mock_call.return_value = json.dumps({"claims": []})
            extractor = LLMExtractor(api_key="test-key")
            chunk = Chunk(id="c1", text="Some text.")
            claims = extractor.extract(chunk)
            assert claims == []

    def test_custom_model(self, mock_openai_response):
        with patch("contrachecker.extractors.llm_extractor._call_llm") as mock_call:
            mock_call.return_value = json.dumps(mock_openai_response)
            extractor = LLMExtractor(api_key="test-key", model="gpt-4o-mini")
            chunk = Chunk(id="c1", text="Text.")
            extractor.extract(chunk)
            call_kwargs = mock_call.call_args
            assert "gpt-4o-mini" in str(call_kwargs)

    def test_prompt_contains_chunk_text(self, mock_openai_response):
        with patch("contrachecker.extractors.llm_extractor._call_llm") as mock_call:
            mock_call.return_value = json.dumps(mock_openai_response)
            extractor = LLMExtractor(api_key="test-key")
            chunk = Chunk(id="c1", text="Aspirin prevents heart attacks.")
            extractor.extract(chunk)
            prompt_sent = str(mock_call.call_args)
            assert "Aspirin prevents heart attacks" in prompt_sent
