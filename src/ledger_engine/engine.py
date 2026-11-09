"""High-level Data Management Engine integrating OOP models, core algorithms, and I/O persistence."""

from pathlib import Path
from typing import Dict, List

from ledger_engine.algorithms import binary_search_account_by_id, merge_sort_accounts
from ledger_engine.exceptions import (
    AccountNotFoundError,
    DuplicateAccountError,
    ValidationError,
)
from ledger_engine.models import Account
from ledger_engine.storage import load_from_csv, load_from_json, save_to_csv, save_to_json


class BankingLedgerEngine:
    """Central engine managing accounts, transfers, algorithmic queries, and file persistence."""

    def __init__(self) -> None:
        self._accounts: Dict[str, Account] = {}

    def register_account(self, account: Account) -> None:
        if not isinstance(account, Account):
            raise ValidationError("Only Account instances can be registered.")
        if account.account_id in self._accounts:
            raise DuplicateAccountError(f"Account '{account.account_id}' already exists.")
        self._accounts[account.account_id] = account

    def get_account(self, account_id: str) -> Account:
        if account_id not in self._accounts:
            raise AccountNotFoundError(f"Account '{account_id}' not found.")
        return self._accounts[account_id]

    def remove_account(self, account_id: str) -> Account:
        if account_id not in self._accounts:
            raise AccountNotFoundError(f"Account '{account_id}' not found.")
        return self._accounts.pop(account_id)

    def transfer(self, source_id: str, target_id: str, amount: float) -> None:
        if source_id == target_id:
            raise ValidationError("Source and target accounts for transfer must be different.")
        source = self.get_account(source_id)
        target = self.get_account(target_id)
        source.withdraw(amount)
        target.deposit(amount)

    def run_monthly_batch(self) -> Dict[str, float]:
        """Demonstrate polymorphism by calling apply_monthly_update across heterogeneous account types."""
        return {acc_id: acc.apply_monthly_update() for acc_id, acc in sorted(self._accounts.items())}

    def list_accounts_sorted_by_balance(self, descending: bool = True) -> List[Account]:
        return merge_sort_accounts(
            list(self._accounts.values()),
            key=lambda acc: acc.balance,
            reverse=descending,
        )

    def list_accounts_sorted_by_id(self) -> List[Account]:
        return merge_sort_accounts(
            list(self._accounts.values()),
            key=lambda acc: acc.account_id,
            reverse=False,
        )

    def find_account_binary_search(self, account_id: str) -> Account:
        sorted_list = self.list_accounts_sorted_by_id()
        found = binary_search_account_by_id(sorted_list, account_id)
        if found is None:
            raise AccountNotFoundError(f"Account '{account_id}' not found via binary search.")
        return found

    def export_json(self, filepath: Path) -> None:
        save_to_json(self.list_accounts_sorted_by_id(), filepath)

    def import_json(self, filepath: Path) -> int:
        loaded = load_from_json(filepath)
        for acc in loaded:
            self._accounts[acc.account_id] = acc
        return len(loaded)

    def export_csv(self, filepath: Path) -> None:
        save_to_csv(self.list_accounts_sorted_by_id(), filepath)

    def import_csv(self, filepath: Path) -> int:
        loaded = load_from_csv(filepath)
        for acc in loaded:
            self._accounts[acc.account_id] = acc
        return len(loaded)
