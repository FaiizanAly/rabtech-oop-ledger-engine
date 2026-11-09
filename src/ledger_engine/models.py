"""OOP Class Hierarchy demonstrating Inheritance, Encapsulation, and Polymorphism."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from ledger_engine.exceptions import InsufficientFundsError, ValidationError


class Account(ABC):
    """Abstract base class representing a bank account with encapsulated state."""

    def __init__(self, account_id: str, owner_name: str, balance: float = 0.0) -> None:
        if not isinstance(account_id, str) or not account_id.strip():
            raise ValidationError("account_id must be a non-empty string.")
        if not isinstance(owner_name, str) or not owner_name.strip():
            raise ValidationError("owner_name must be a non-empty string.")
        if not isinstance(balance, (int, float)) or isinstance(balance, bool) or balance < 0:
            raise ValidationError("Initial balance must be a non-negative number.")

        self.__account_id: str = account_id.strip()
        self.__owner_name: str = owner_name.strip()
        self._balance: float = round(float(balance), 2)
        self._transactions: List[Dict[str, Any]] = []

    @property
    def account_id(self) -> str:
        return self.__account_id

    @property
    def owner_name(self) -> str:
        return self.__owner_name

    @owner_name.setter
    def owner_name(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("owner_name must be a non-empty string.")
        self.__owner_name = value.strip()

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def transactions(self) -> List[Dict[str, Any]]:
        return list(self._transactions)

    @property
    @abstractmethod
    def account_type(self) -> str:
        """Return polymorphic account type identifier."""

    def _validate_positive_amount(self, amount: float) -> float:
        if not isinstance(amount, (int, float)) or isinstance(amount, bool) or amount <= 0:
            raise ValidationError("Transaction amount must be a positive number greater than 0.")
        return round(float(amount), 2)

    def deposit(self, amount: float) -> float:
        clean_amount = self._validate_positive_amount(amount)
        self._balance = round(self._balance + clean_amount, 2)
        self._transactions.append({"type": "DEPOSIT", "amount": clean_amount, "balance_after": self._balance})
        return self._balance

    @abstractmethod
    def withdraw(self, amount: float) -> float:
        """Polymorphic withdrawal behavior implemented by concrete subclasses."""

    @abstractmethod
    def apply_monthly_update(self) -> float:
        """Polymorphic monthly settlement (interest gain or fee deduction)."""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "account_id": self.account_id,
            "account_type": self.account_type,
            "owner_name": self.owner_name,
            "balance": self.balance,
            "interest_rate": getattr(self, "interest_rate", 0.0),
            "overdraft_limit": getattr(self, "overdraft_limit", 0.0),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Account":
        if not isinstance(data, dict):
            raise ValidationError("Account record must be a dictionary.")
        acc_type = str(data.get("account_type", "")).upper().strip()
        try:
            acc_id = str(data["account_id"])
            owner = str(data["owner_name"])
            balance = float(data.get("balance", 0.0))
        except (KeyError, ValueError, TypeError) as exc:
            raise ValidationError(f"Malformed account fields: {exc}") from exc

        if acc_type == "SAVINGS":
            rate = float(data.get("interest_rate", 0.04) or 0.04)
            return SavingsAccount(acc_id, owner, balance=balance, interest_rate=rate)
        if acc_type == "CHECKING":
            limit = float(data.get("overdraft_limit", 500.0) if data.get("overdraft_limit") is not None else 500.0)
            return CheckingAccount(acc_id, owner, balance=balance, overdraft_limit=limit)
        raise ValidationError(f"Unsupported account_type: '{acc_type}'. Expected 'SAVINGS' or 'CHECKING'.")


class SavingsAccount(Account):
    """Savings account with interest accrual and strict non-negative balance rule."""

    def __init__(
        self,
        account_id: str,
        owner_name: str,
        balance: float = 0.0,
        interest_rate: float = 0.04,
    ) -> None:
        super().__init__(account_id, owner_name, balance)
        if not isinstance(interest_rate, (int, float)) or isinstance(interest_rate, bool) or interest_rate < 0:
            raise ValidationError("interest_rate must be a non-negative number.")
        self.__interest_rate = round(float(interest_rate), 4)

    @property
    def account_type(self) -> str:
        return "SAVINGS"

    @property
    def interest_rate(self) -> float:
        return self.__interest_rate

    def withdraw(self, amount: float) -> float:
        clean_amount = self._validate_positive_amount(amount)
        if clean_amount > self._balance:
            raise InsufficientFundsError(
                f"Savings withdrawal of {clean_amount} exceeds current balance of {self._balance}."
            )
        self._balance = round(self._balance - clean_amount, 2)
        self._transactions.append({"type": "WITHDRAW", "amount": clean_amount, "balance_after": self._balance})
        return self._balance

    def apply_monthly_update(self) -> float:
        interest = round(self._balance * self.__interest_rate, 2)
        if interest > 0:
            self._balance = round(self._balance + interest, 2)
            self._transactions.append({"type": "INTEREST", "amount": interest, "balance_after": self._balance})
        return self._balance


class CheckingAccount(Account):
    """Checking account supporting configurable overdraft protection and overdraft fee on monthly settlement."""

    OVERDRAFT_FEE = 25.0

    def __init__(
        self,
        account_id: str,
        owner_name: str,
        balance: float = 0.0,
        overdraft_limit: float = 500.0,
    ) -> None:
        super().__init__(account_id, owner_name, balance)
        if not isinstance(overdraft_limit, (int, float)) or isinstance(overdraft_limit, bool) or overdraft_limit < 0:
            raise ValidationError("overdraft_limit must be a non-negative number.")
        self.__overdraft_limit = round(float(overdraft_limit), 2)

    @property
    def account_type(self) -> str:
        return "CHECKING"

    @property
    def overdraft_limit(self) -> float:
        return self.__overdraft_limit

    def withdraw(self, amount: float) -> float:
        clean_amount = self._validate_positive_amount(amount)
        if clean_amount > (self._balance + self.__overdraft_limit):
            raise InsufficientFundsError(
                f"Checking withdrawal of {clean_amount} exceeds available funds + overdraft limit "
                f"({self._balance + self.__overdraft_limit})."
            )
        self._balance = round(self._balance - clean_amount, 2)
        self._transactions.append({"type": "WITHDRAW", "amount": clean_amount, "balance_after": self._balance})
        return self._balance

    def apply_monthly_update(self) -> float:
        if self._balance < 0:
            self._balance = round(self._balance - self.OVERDRAFT_FEE, 2)
            self._transactions.append(
                {"type": "OVERDRAFT_FEE", "amount": self.OVERDRAFT_FEE, "balance_after": self._balance}
            )
        return self._balance
