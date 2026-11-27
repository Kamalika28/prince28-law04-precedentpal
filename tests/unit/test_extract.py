"""Test metadata validation and extraction without a real model or database."""

import pytest
from pydantic import ValidationError

from precedentpal.llm.doc_meta import DocMeta
from precedentpal.llm.extract import extract, parse_json, run
from precedentpal.llm.gateway import FakeLLM, LLMGateway

VALID = {
    "doc_kind": "judgment",
    "year": 2024,
    "language": "en",
    "summary": "The court considered a constitutional law question.",
    "topics": ["Constitutional Law"],
    "case_name": ["Example v. State"],
    "citation": [],
    "date": [],
    "judges": [],
    "opinion_type": [],
}


def test_valid_metadata():
    record = DocMeta.model_validate(VALID)
    assert record.year == 2024
    assert record.topics == ["constitutional law"]


def test_invalid_metadata_is_rejected():
    with pytest.raises(ValidationError):
        DocMeta.model_validate({**VALID, "year": 1800})

    with pytest.raises(ValidationError):
        DocMeta.model_validate({**VALID, "unexpected": "field"})


def test_parse_json_rejects_missing_object():
    with pytest.raises(ValueError):
        parse_json("No JSON here")


async def test_extract_repairs_invalid_reply():
    llm = FakeLLM(
        script=[
            "not JSON",
            __import__("json").dumps(VALID),
        ]
    )
    gateway = LLMGateway([llm])

    result = await extract(
        gateway,
        DocMeta,
        "Extract metadata.",
        "extract_v1",
        "Example v. State",
        "The court considered constitutional law.",
    )

    assert result.record is not None
    assert result.attempts == 2
    assert len(result.errors) == 1
    assert result.record.year == 2024
    assert llm.seen[0]["temperature"] == 0
    assert llm.seen[1]["messages"][-1]["role"] == "user"


async def test_extract_records_failure_after_three_invalid_replies():
    llm = FakeLLM(script=["bad", "still bad", "also bad"])
    gateway = LLMGateway([llm])

    result = await extract(
        gateway,
        DocMeta,
        "Extract metadata.",
        "extract_v1",
        "Example",
        "Document text",
    )

    assert result.record is None
    assert result.attempts == 3
    assert len(result.errors) == 3


async def test_reserved_fields_are_rejected_before_database_access():
    from pydantic import BaseModel

    class BadSchema(BaseModel):
        source: str

    with pytest.raises(ValueError, match="reserved"):
        await run(
            None,
            LLMGateway([FakeLLM()]),
            BadSchema,
            "Extract.",
            "extract_v1",
        )
