"""Clean file I/O operations supporting JSON and CSV data persistence."""

import csv
import json
from pathlib import Path
from typing import List

from ledger_engine.exceptions import DataPersistenceError, ValidationError
from ledger_engine.models import Account


CSV_FIELDNAMES = [
    "account_id",
    "account_type",
    "owner_name",
    "balance",
    "interest_rate",
    "overdraft_limit",
]


def save_to_json(accounts: List[Account], filepath: Path) -> None:
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        payload = {"accounts": [acc.to_dict() for acc in accounts]}
        filepath.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    except OSError as exc:
        raise DataPersistenceError(f"Failed to write JSON file {filepath}: {exc}") from exc


def load_from_json(filepath: Path) -> List[Account]:
    if not filepath.exists() or not filepath.is_file():
        raise DataPersistenceError(f"JSON file not found: {filepath}")
    try:
        raw = json.loads(filepath.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DataPersistenceError(f"Invalid or unreadable JSON in {filepath}: {exc}") from exc

    if not isinstance(raw, dict) or "accounts" not in raw or not isinstance(raw["accounts"], list):
        raise DataPersistenceError(f"Invalid JSON schema in {filepath}: expected root 'accounts' list.")

    try:
        return [Account.from_dict(item) for item in raw["accounts"]]
    except ValidationError as exc:
        raise DataPersistenceError(f"Invalid account record in JSON {filepath}: {exc}") from exc


def save_to_csv(accounts: List[Account], filepath: Path) -> None:
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with filepath.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
            writer.writeheader()
            for acc in accounts:
                writer.writerow(acc.to_dict())
    except OSError as exc:
        raise DataPersistenceError(f"Failed to write CSV file {filepath}: {exc}") from exc


def load_from_csv(filepath: Path) -> List[Account]:
    if not filepath.exists() or not filepath.is_file():
        raise DataPersistenceError(f"CSV file not found: {filepath}")
    try:
        with filepath.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or not {"account_id", "account_type", "owner_name", "balance"}.issubset(
                set(reader.fieldnames)
            ):
                raise DataPersistenceError(f"Invalid CSV headers in {filepath}.")
            accounts: List[Account] = []
            for row in reader:
                accounts.append(Account.from_dict(row))
            return accounts
    except (OSError, csv.Error, ValidationError) as exc:
        raise DataPersistenceError(f"Failed to load CSV {filepath}: {exc}") from exc
