import json
from pathlib import Path


REQUIRED_SUBMISSION_FILES = ("config.json", "paper.md", "protocol.md", "index.html")
REQUIRED_ASSET_FILES = ("dashboard.html", "industry.html", "sponsor-classes.html", "phases.html")


def test_repository_smoke():
    root = Path(__file__).resolve().parents[1]
    submission = root / "e156-submission"
    assets = submission / "assets"

    for name in REQUIRED_SUBMISSION_FILES:
        assert (submission / name).exists(), name

    for name in REQUIRED_ASSET_FILES:
        assert (assets / name).exists(), name

    config = json.loads((submission / "config.json").read_text(encoding="utf-8"))
    assert len(config.get("body", "").split()) == 156

    sentences = config.get("sentences", [])
    assert len(sentences) == 7
    assert all((entry.get("text") if isinstance(entry, dict) else str(entry)).strip() for entry in sentences)
    assert config.get("notes", {}).get("code")

