from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any

class Transaction:
    def __init__(self, txn_id: UUID, account_id: UUID, vendor_id: int, vendor_name: str,
                 category_id: int, category_name: str, amount: Decimal, date: datetime, txn_type: str):
        self._id = txn_id
        self._account_id = account_id
        self._vendor_id = vendor_id
        self._vendor_name = vendor_name
        self._category_id = category_id
        self._category_name = category_name
        self._amount = amount
        self._date = date
        self._type = txn_type

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def account_id(self) -> UUID:
        return self._account_id

    @property
    def vendor_id(self) -> int:
        return self._vendor_id

    @property
    def category_id(self) -> int:
        return self._category_id

    @property
    def amount(self) -> Decimal:
        return self._amount

    @property
    def date(self) -> datetime:
        return self._date

    @property
    def type(self) -> str:
        return self._type

    def update_category(self, new_category_id: int, new_category_name: str) -> None:
        self._category_id = new_category_id
        self._category_name = new_category_name

    def get_details(self) -> Dict[str, Any]:
        """Returns dictionary for UI/Analytics."""
        return {
            "id": str(self._id),
            "vendor": self._vendor_name,
            "category": self._category_name,
            "amount": float(self._amount),
            "date": self._date.isoformat(),
            "type": self._type
        }