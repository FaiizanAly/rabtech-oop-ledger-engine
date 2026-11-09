"""Custom exception hierarchy for graceful handling of invalid inputs and operational errors."""


class LedgerError(Exception):
    """Base exception for all banking ledger engine errors."""


class ValidationError(LedgerError):
    """Raised when account fields, amounts, or parameters fail validation."""


class InsufficientFundsError(LedgerError):
    """Raised when a withdrawal exceeds available balance or overdraft limits."""


class AccountNotFoundError(LedgerError):
    """Raised when a requested account ID does not exist in the ledger."""


class DuplicateAccountError(LedgerError):
    """Raised when attempting to register an account ID that already exists."""


class DataPersistenceError(LedgerError):
    """Raised when JSON or CSV serialization/deserialization fails."""
