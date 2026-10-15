"""Integrity checks for ClinicalTrials.gov v2 paginated registry snapshots.

A complete export exhausts the paginated *query*; it is not an atomic
snapshot of the live database (studies can change during a long export).
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

NCT_ID = re.compile(r"^NCT\d{8}$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class SnapshotAudit:
    """Fail a registry export rather than certify a duplicated or truncated scan."""

    def __init__(self) -> None:
        self.expected_token: str | None = None
        self.seen_tokens: set[str] = set()
        self.seen_ids: set[str] = set()
        self.total_count: int | None = None
        self.pages_fetched = 0
        self.records_fetched = 0

    def register_page(self, payload: dict[str, Any], request_token: str | None) -> tuple[list[dict[str, Any]], str | None]:
        if not isinstance(payload, dict):
            raise ValueError("CT.gov returned a non-object page")
        if request_token != self.expected_token:
            raise ValueError("Unexpected pagination cursor (page skipped or replayed)")
        if self.pages_fetched == 0:
            total = payload.get("totalCount")
            if type(total) is not int or total < 0:
                raise ValueError("First page must contain a non-negative integer totalCount")
            self.total_count = total
        studies = payload.get("studies")
        if not isinstance(studies, list):
            raise ValueError("CT.gov page is missing its studies list")
        token = payload.get("nextPageToken")
        if token is not None and (not isinstance(token, str) or not token):
            raise ValueError("Invalid nextPageToken")
        if token and (token == request_token or token in self.seen_tokens):
            raise ValueError("Repeated pagination cursor detected")
        if not studies and token:
            raise ValueError("Empty CT.gov page still advertises more results")
        for study in studies:
            if not isinstance(study, dict):
                raise ValueError("CT.gov study is not an object")
            nct_id = study.get("protocolSection", {}).get("identificationModule", {}).get("nctId")
            if not isinstance(nct_id, str) or not NCT_ID.fullmatch(nct_id):
                raise ValueError("Study missing a valid NCT identifier")
            if nct_id in self.seen_ids:
                raise ValueError("Duplicate registry NCT identifier: " + nct_id)
            self.seen_ids.add(nct_id)
        self.records_fetched += len(studies)
        self.pages_fetched += 1
        if self.records_fetched > self.total_count:
            raise ValueError("Fetched records exceed API totalCount")
        if token:
            self.seen_tokens.add(token)
        self.expected_token = token
        return studies, token

    def finish(self, *, complete: bool) -> dict[str, Any]:
        if complete and self.records_fetched != self.total_count:
            raise ValueError(
                f"Pagination ended at {self.records_fetched}/{self.total_count} studies; "
                "cannot mark this registry export complete"
            )
        return {
            "coverage": "complete" if complete else "partial",
            "scope_complete": complete,
            "records_fetched": self.records_fetched,
            "unique_nct_ids": len(self.seen_ids),
            "pages_fetched": self.pages_fetched,
            "total_count": self.total_count,
        }


def validate_snapshot_metadata(metadata: dict[str, Any], snapshot_path: Path, *, allow_partial: bool = False) -> None:
    if not snapshot_path.is_file():
        raise FileNotFoundError(f"Registry snapshot missing: {snapshot_path}")
    fetched = metadata.get("records_fetched")
    total = metadata.get("total_count")
    if type(fetched) is not int or fetched <= 0:
        raise ValueError("Snapshot metadata has no valid record count")
    if type(total) is not int or total < 0:
        raise ValueError("Snapshot metadata lacks a valid API totalCount")
    if metadata.get("unique_nct_ids", fetched) != fetched:
        raise ValueError("Snapshot contains duplicate NCT identifiers")
    complete = metadata.get("scope_complete", metadata.get("coverage") == "complete")
    # Older manifests did not have coverage fields; their counts still matter.
    if "scope_complete" not in metadata and "coverage" not in metadata:
        complete = fetched == total
    if not complete and not allow_partial:
        raise ValueError("Snapshot is partial: refuse full-registry conclusions (use --allow-partial explicitly)")
    if complete and fetched != total:
        raise ValueError("Snapshot is labelled complete but does not match the API totalCount")
    sha = metadata.get("file_sha256")
    if sha and sha256_file(snapshot_path) != sha:
        raise ValueError("Snapshot SHA-256 does not match its metadata")
