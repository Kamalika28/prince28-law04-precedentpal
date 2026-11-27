"""Extract metadata from parsed documents.

Examples:
    uv run python scripts/extract_metadata.py --limit 5
    uv run python scripts/extract_metadata.py
    uv run python scripts/extract_metadata.py --retry-failed
    uv run python scripts/extract_metadata.py --schema
"""

import argparse
import asyncio
import re

from precedentpal.config import get_settings
from precedentpal.db.llm_calls import make_recorder
from precedentpal.db.session import make_engine, make_sessionmaker
from precedentpal.llm.doc_meta import DocMeta
from precedentpal.llm.extract import run
from precedentpal.llm.gateway import build_gateway
from precedentpal.llm.prompts import read_prompt


def latest_extract_version(prompts_dir) -> str:
    """Find the highest numbered extract_vN.md prompt."""
    candidates = []

    for path in prompts_dir.glob("extract_v*.md"):
        match = re.fullmatch(r"extract_v(\d+)", path.stem)
        if match:
            candidates.append((int(match.group(1)), path.stem))

    if not candidates:
        raise SystemExit(f"No extract_v*.md prompt found in {prompts_dir}")

    return max(candidates)[1]


async def main_async(args: argparse.Namespace) -> int:
    settings = get_settings()
    version = latest_extract_version(settings.prompts_dir)
    prompt = read_prompt(settings.prompts_dir, version)

    if "TODO" in prompt:
        raise SystemExit(f"{version} still contains TODO")

    engine = make_engine(settings)

    try:
        sessionmaker = make_sessionmaker(engine)
        gateway = build_gateway(settings, make_recorder(sessionmaker))

        if not gateway.providers:
            raise SystemExit("No LLM provider is configured")

        print(f"Prompt: {version}")
        print(f"Limit: {args.limit or 'all pending documents'}")
        print(f"Rate: {args.rpm:g} documents/minute")

        counts = await run(
            sessionmaker,
            gateway,
            DocMeta,
            prompt,
            version,
            limit=args.limit,
            rpm=args.rpm,
            chars=args.chars,
            retry_failed=args.retry_failed,
            native=args.schema,
        )

        print("\nExtraction summary")
        for key, value in counts.items():
            print(f"{key}: {value}")

        cost = counts["micro_inr"] / 1_000_000
        print(f"Total model cost: INR {cost:.6f}")

        return 1 if counts["failed"] or counts["stopped"] else 0

    finally:
        await engine.dispose()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--rpm", type=float, default=12)
    parser.add_argument("--chars", type=int, default=6000)
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument("--schema", action="store_true")
    args = parser.parse_args()

    if args.limit < 0 or args.rpm <= 0 or args.chars <= 0:
        parser.error("--limit must be >= 0; --rpm and --chars must be > 0")

    return asyncio.run(main_async(args))


if __name__ == "__main__":
    raise SystemExit(main())
