"""Test metadata extraction storage using a real PostgreSQL database."""

import pytest

from precedentpal.config import Settings
from precedentpal.db.models import Document, ParseFailure
from precedentpal.db.session import make_engine, make_sessionmaker
from precedentpal.llm.doc_meta import DocMeta
from precedentpal.llm.extract import Extraction, pending, save


@pytest.fixture
async def session(database_url):
    engine = make_engine(
        Settings(
            app_env="ci",
            database_url=database_url,
            _env_file=None,
        )
    )
    async with make_sessionmaker(engine)() as db:
        await db.execute(Document.__table__.delete())
        await db.execute(ParseFailure.__table__.delete())
        await db.commit()
        yield db
    await engine.dispose()


async def test_metadata_is_saved_and_not_selected_again(session):
    document = Document(
        external_id="test-document",
        title="Example constitutional judgment",
        source_url="https://example.org/judgment.pdf",
        licence="CC BY 4.0",
        doc_type="pdf",
        sha256="ab" * 32,
        metadata_={"pages": 2},
    )
    session.add(document)
    await session.commit()

    record = DocMeta(
        doc_kind="judgment",
        year=2024,
        language="en",
        summary="The court considered a constitutional law question.",
        topics=["constitutional law"],
    )

    result = Extraction(
        record=record,
        attempts=1,
        model="fake-model",
    )

    await save(session, document, result, "extract_v1")
    await session.refresh(document)

    assert document.metadata_["year"] == 2024
    assert document.metadata_["doc_kind"] == "judgment"
    assert document.metadata_["pages"] == 2
    assert document.metadata_["extract"]["prompt"] == "extract_v1"
    assert document.metadata_["extract"]["attempts"] == 1

    assert await pending(session, "extract_v1") == []
    assert len(await pending(session, "extract_v2")) == 1
