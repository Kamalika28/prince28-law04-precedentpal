import json
from pathlib import Path


def load_manifest(path: Path) -> list[dict]:
    """Return the latest downloaded record per URL."""
    if not path.is_file():
        return []

    latest: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("url"):
            latest[record["url"]] = record

    return [
        record
        for record in latest.values()
        if record.get("status") == "downloaded"
        and record.get("path")
        and Path(record["path"]).is_file()
    ]
