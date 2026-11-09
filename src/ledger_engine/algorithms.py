"""Core sorting and searching algorithms operating on Account objects."""

from typing import Callable, List, Optional
from ledger_engine.models import Account


def merge_sort_accounts(
    accounts: List[Account],
    key: Callable[[Account], object] = lambda acc: acc.account_id,
    reverse: bool = False,
) -> List[Account]:
    """Deterministic O(n log n) Merge Sort implementation for Account lists."""
    if len(accounts) <= 1:
        return list(accounts)

    mid = len(accounts) // 2
    left = merge_sort_accounts(accounts[:mid], key=key, reverse=reverse)
    right = merge_sort_accounts(accounts[mid:], key=key, reverse=reverse)

    merged: List[Account] = []
    i = j = 0
    while i < len(left) and j < len(right):
        left_val = key(left[i])
        right_val = key(right[j])
        condition = (left_val >= right_val) if reverse else (left_val <= right_val)
        if condition:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def binary_search_account_by_id(sorted_accounts: List[Account], target_id: str) -> Optional[Account]:
    """O(log n) Binary Search over an account list sorted ascending by account_id."""
    low = 0
    high = len(sorted_accounts) - 1

    while low <= high:
        mid = (low + high) // 2
        current_id = sorted_accounts[mid].account_id
        if current_id == target_id:
            return sorted_accounts[mid]
        if current_id < target_id:
            low = mid + 1
        else:
            high = mid - 1

    return None
