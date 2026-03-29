#!/usr/bin/env python3
"""Fetch a full ClinicalTrials.gov registry snapshot with a narrow field set."""

from __future__ import annotations

import argparse
import gzip
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
CTGOV_API = "https://clinicaltrials.gov/api/v2/studies"
USER_AGENT = "ctgov-hiddenness-atlas/0.1"

FIELD_PATHS = [
    "protocolSection.identificationModule.nctId",
    "protocolSection.identificationModule.briefTitle",
    "protocolSection.identificationModule.officialTitle",
    "protocolSection.statusModule.overallStatus",
    "protocolSection.statusModule.whyStopped",
    "protocolSection.statusModule.studyFirstSubmitDate",
    "protocolSection.statusModule.startDateStruct.date",
    "protocolSection.statusModule.startDateStruct.type",
    "protocolSection.statusModule.primaryCompletionDateStruct.date",
    "protocolSection.statusModule.primaryCompletionDateStruct.type",
    "protocolSection.statusModule.completionDateStruct.date",
    "protocolSection.statusModule.completionDateStruct.type",
    "protocolSection.statusModule.resultsFirstPostDateStruct.date",
    "protocolSection.sponsorCollaboratorsModule.leadSponsor.name",
    "protocolSection.sponsorCollaboratorsModule.leadSponsor.class",
    "protocolSection.designModule.studyType",
    "protocolSection.designModule.phases",
    "protocolSection.designModule.designInfo.allocation",
    "protocolSection.designModule.designInfo.primaryPurpose",
    "protocolSection.designModule.enrollmentInfo.count",
    "protocolSection.designModule.enrollmentInfo.type",
    "protocolSection.conditionsModule.conditions",
    "protocolSection.armsInterventionsModule.armGroups.label",
    "protocolSection.armsInterventionsModule.interventions.type",
    "protocolSection.contactsLocationsModule.locations.country",
    "protocolSection.contactsLocationsModule.locations.facility",
    "protocolSection.outcomesModule.primaryOutcomes.measure",
    "protocolSection.outcomesModule.primaryOutcomes.description",
    "protocolSection.outcomesModule.secondaryOutcomes.measure",
    "protocolSection.outcomesModule.secondaryOutcomes.description",
    "protocolSection.referencesModule.references.type",
    "protocolSection.referencesModule.references.pmid",
    "protocolSection.descriptionModule.briefSummary",
    "protocolSection.descriptionModule.detailedDescription",
    "protocolSection.ipdSharingStatementModule.ipdSharing",
    "protocolSection.ipdSharingStatementModule.description",
    "hasResults",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page-size", type=int, default=1000)
    parser.add_argument("--sleep-seconds", type=float, default=0.1)
    parser.add_argument("--max-pages", type=int, default=0)
    parser.add_argument("--query-term", default="")
    parser.add_argument(
        "--output-stem",
        default="ctgov_registry_minimal",
        help="Base filename under data/raw without extension",
    )
    return parser.parse_args()


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})
    return session


def fetch_page(session: requests.Session, params: dict[str, Any]) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(5):
        try:
            response = session.get(CTGOV_API, params=params, timeout=120)
            response.raise_for_status()
            return response.json()
        except Exception as exc:  # pragma: no cover
            last_error = exc
            wait_seconds = 2**attempt
            print(f"Request failed on attempt {attempt + 1}/5; retrying in {wait_seconds}s")
            time.sleep(wait_seconds)
    raise RuntimeError(f"Failed after repeated retries: {last_error}") from last_error


def main() -> None:
    args = parse_args()
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    output_path = RAW_DIR / f"{args.output_stem}.jsonl.gz"
    metadata_path = RAW_DIR / f"{args.output_stem}_metadata.json"

    session = get_session()
    params: dict[str, Any] = {
        "pageSize": args.page_size,
        "countTotal": "true",
        "fields": ",".join(FIELD_PATHS),
    }
    if args.query_term:
        params["query.term"] = args.query_term

    fetched_records = 0
    pages = 0
    total_count = None
    started_at = datetime.now(UTC)
    next_token = None

    with gzip.open(output_path, "wt", encoding="utf-8") as handle:
        while True:
            if next_token:
                params["pageToken"] = next_token
            else:
                params.pop("pageToken", None)

            payload = fetch_page(session, params)
            batch = payload.get("studies", [])
            pages += 1

            if total_count is None:
                total_count = payload.get("totalCount", 0)
                print(f"API totalCount: {total_count}")

            for study in batch:
                handle.write(json.dumps(study, separators=(",", ":")))
                handle.write("\n")

            fetched_records += len(batch)
            next_token = payload.get("nextPageToken")
            if pages == 1 or pages % 10 == 0 or not next_token:
                print(
                    f"page={pages} batch={len(batch)} fetched={fetched_records}"
                    + (f" total={total_count}" if total_count is not None else "")
                )

            if not next_token:
                break
            if args.max_pages and pages >= args.max_pages:
                break

            params.pop("countTotal", None)
            if args.sleep_seconds > 0:
                time.sleep(args.sleep_seconds)

    finished_at = datetime.now(UTC)
    metadata = {
        "fetched_at": finished_at.isoformat(),
        "started_at": started_at.isoformat(),
        "api_url": CTGOV_API,
        "query_term": args.query_term,
        "page_size": args.page_size,
        "pages_fetched": pages,
        "records_fetched": fetched_records,
        "total_count": total_count,
        "fields": FIELD_PATHS,
        "output_file": str(output_path),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Raw snapshot written to {output_path}")
    print(f"Metadata written to {metadata_path}")


if __name__ == "__main__":
    main()
