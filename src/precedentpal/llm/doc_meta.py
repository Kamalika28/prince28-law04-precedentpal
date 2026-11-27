"""Validated metadata contract for Supreme Court documents."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

Short = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=80),
]

OpinionType = Literal["majority", "dissent", "concurring", "unknown"]


class DocMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc_kind: Literal["judgment", "order", "other"]
    year: int | None = Field(default=None, ge=1950, le=2027)
    language: Literal["en", "ta", "hi", "other"]
    summary: str = Field(min_length=20, max_length=300)
    topics: list[Short] = Field(min_length=1, max_length=6)

    case_name: list[Short] = Field(default_factory=list, max_length=8)
    citation: list[Short] = Field(default_factory=list, max_length=8)
    date: list[Short] = Field(default_factory=list, max_length=8)
    judges: list[Short] = Field(default_factory=list, max_length=8)
    opinion_type: list[OpinionType] = Field(default_factory=list, max_length=8)

    @field_validator("topics")
    @classmethod
    def tidy_topics(cls, value: list[str]) -> list[str]:
        return list(dict.fromkeys(topic.lower() for topic in value))
