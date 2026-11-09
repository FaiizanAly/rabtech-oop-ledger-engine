# Banking Ledger Data Management Engine

**Task 03: Core Algorithms, OOP Structures & Robust Error Handling**  
*RabTech Python Software Engineering Internship*  
**Author:** Faizan Ali (`git.faizanali@gmail.com`)

---

## Overview

The **Banking Ledger Data Management Engine** is an enterprise-grade Python package demonstrating fundamental software engineering principles:
- **Object-Oriented Programming (OOP):** Strict encapsulation, class inheritance, and polymorphic monthly settlements.
- **Robust Error Handling:** A centralized custom exception hierarchy providing actionable, typed operational errors.
- **Core Algorithms:** Native implementations of deterministic $O(n \log n)$ Merge Sort and $O(\log n)$ Binary Search.
- **Data Persistence:** Production-ready JSON and CSV import/export engines with strict schema and header validation.
- **Automated Testing:** 100% passing test suite achieving **96% code coverage** using `pytest` and `pytest-cov`.

---

## Target Directory Structure

```text
.
├── .gitignore
├── pyproject.toml
├── README.md
├── data/
│   ├── sample_accounts.json
│   └── sample_accounts.csv
├── src/
│   └── ledger_engine/
│       ├── __init__.py
│       ├── exceptions.py
│       ├── models.py
│       ├── algorithms.py
│       ├── storage.py
│       └── engine.py
└── tests/
    └── test_engine.py
```

---

## Architecture Overview

The system architecture is grounded in clean Object-Oriented Design principles:

### 1. Inheritance
- **`Account` (Abstract Base Class):** Inherits from `abc.ABC`. Defines common ledger attributes (`account_id`, `owner_name`, `balance`, `transactions`) and abstract methods (`withdraw()`, `apply_monthly_update()`, `account_type`).
- **`SavingsAccount`:** Extends `Account`. Implements interest accrual based on a configurable annual interest rate and strictly prohibits negative balances.
- **`CheckingAccount`:** Extends `Account`. Features configurable overdraft protection and assesses a fixed monthly fee (`OVERDRAFT_FEE = $25.00`) when the account balance is negative at settlement time.

### 2. Encapsulation
- **Private State:** Critical identifiers such as `__account_id`, `__owner_name`, `__interest_rate`, and `__overdraft_limit` are strictly private to prevent external tampering.
- **Managed Properties:** Access is governed via Python `@property` getters and setters with type and boundary validation.
- **Protected State:** `_balance` and `_transactions` are protected, modified strictly via audited methods (`deposit()`, `withdraw()`, `apply_monthly_update()`).
- **Defensive Copying:** The `transactions` property returns a copy of the transaction history list to maintain immutability of historical records.

### 3. Polymorphism
Concrete subclasses implement divergent business behavior through unified interfaces:
- **`withdraw(amount)`:** `SavingsAccount` rejects any withdrawal that exceeds the current balance. `CheckingAccount` authorizes withdrawals up to `balance + overdraft_limit`.
- **`apply_monthly_update()`:** `SavingsAccount` computes and adds accrued interest to the balance. `CheckingAccount` detects overdraft balances and deducts the overdraft service fee.
- **Heterogeneous Batch Execution:** `BankingLedgerEngine.run_monthly_batch()` processes all registered accounts uniformly without inspecting concrete types.

---

## Custom Exception Hierarchy

All application errors derive from the base exception `LedgerError`, establishing clean separation from standard Python runtime errors.

| Exception Class | Inherits From | Description / Trigger Conditions |
|---|---|---|
| `LedgerError` | `Exception` | Base exception for all banking ledger operational and domain errors. |
| `ValidationError` | `LedgerError` | Raised when input parameters, IDs, names, or monetary amounts fail validation. |
| `InsufficientFundsError` | `LedgerError` | Raised when a withdrawal exceeds available balance (or balance + overdraft limit). |
| `AccountNotFoundError` | `LedgerError` | Raised when querying, removing, or transferring against a non-existent account ID. |
| `DuplicateAccountError` | `LedgerError` | Raised when registering an account ID that already exists in the ledger. |
| `DataPersistenceError` | `LedgerError` | Raised when JSON or CSV serialization/deserialization fails or encounters invalid schema/headers. |

---

## Core Algorithms

### 1. Merge Sort ($O(n \log n)$)
Implemented in `ledger_engine.algorithms.merge_sort_accounts`:
- **Time Complexity:** $O(n \log n)$ in best, average, and worst cases.
- **Space Complexity:** $O(n)$ auxiliary space.
- **Stability & Flexibility:** Stable sorting supporting arbitrary key extraction functions (e.g. sorting by `balance` descending or `account_id` ascending).

```python
from ledger_engine.algorithms import merge_sort_accounts

# Sort accounts descending by balance
sorted_by_balance = merge_sort_accounts(
    accounts,
    key=lambda acc: acc.balance,
    reverse=True
)
```

### 2. Binary Search ($O(\log n)$)
Implemented in `ledger_engine.algorithms.binary_search_account_by_id`:
- **Time Complexity:** $O(\log n)$ search time over an ascending-ordered collection.
- **Space Complexity:** $O(1)$ auxiliary space (iterative pointer mechanics).
- **Usage:** Pre-sorted list of accounts indexed by `account_id`.

```python
from ledger_engine.algorithms import binary_search_account_by_id

# Fast logarithmic lookup
account = binary_search_account_by_id(sorted_accounts, target_id="ACC-1002")
```

---

## Data Persistence (JSON & CSV)

The engine provides lossless serialization and deserialization across both JSON and CSV formats.

### Sample Artifacts
- **JSON:** [`data/sample_accounts.json`](data/sample_accounts.json)
- **CSV:** [`data/sample_accounts.csv`](data/sample_accounts.csv)

### Python Persistence Example
```python
from pathlib import Path
from ledger_engine import BankingLedgerEngine, SavingsAccount, CheckingAccount

engine = BankingLedgerEngine()

# Register accounts
engine.register_account(SavingsAccount("ACC-1001", "Faizan Ali", balance=15250.75, interest_rate=0.045))
engine.register_account(CheckingAccount("ACC-1002", "Sara Khan", balance=4200.50, overdraft_limit=1000.0))

# Export to JSON and CSV
engine.export_json(Path("data/sample_accounts.json"))
engine.export_csv(Path("data/sample_accounts.csv"))

# Import from disk into a clean engine instance
new_engine = BankingLedgerEngine()
new_engine.import_json(Path("data/sample_accounts.json"))
assert new_engine.get_account("ACC-1001").balance == 15250.75
```

---

## Installation & Setup

### 1. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies
Install the package in editable mode with development dependencies:
```bash
# Windows
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\pip install -e ".[dev]"

# macOS / Linux
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"
```

---

## Verification & Test Coverage

The test suite validates input validation, encapsulation, polymorphism, algorithm correctness, and persistence fault tolerance.

### Run Tests
```bash
.venv\Scripts\python -m pytest -v
```

### Coverage Report
```text
============================= test session starts =============================
platform win32 -- Python 3.14.10, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\Aly\Desktop\RabTech\task3
configfile: pyproject.toml
testpaths: tests
plugins: cov-7.1.0
collecting ... collected 4 items

tests/test_engine.py::test_account_hierarchy_encapsulation_and_polymorphism PASSED [ 25%]
tests/test_engine.py::test_custom_exceptions_on_invalid_inputs_and_overdraft PASSED [ 50%]
tests/test_engine.py::test_engine_operations_and_core_algorithms PASSED  [ 75%]
tests/test_engine.py::test_json_and_csv_persistence_and_error_handling PASSED [100%]

=============================== tests coverage ================================
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src\ledger_engine\__init__.py         5      0   100%
src\ledger_engine\algorithms.py      34      1    97%   51
src\ledger_engine\engine.py          56      1    98%   31
src\ledger_engine\exceptions.py       6      0   100%
src\ledger_engine\models.py         118      3    97%   84, 90-91
src\ledger_engine\storage.py         51      5    90%   27-28, 56-57, 75
---------------------------------------------------------------
TOTAL                               270     10    96%
============================== 4 passed in 0.15s ==============================
```

**Target Requirement:** > 80% coverage  
**Achieved Coverage:** **96%**
