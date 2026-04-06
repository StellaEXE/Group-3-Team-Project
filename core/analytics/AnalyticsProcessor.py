from decimal import Decimal
from uuid import UUID
from typing import Dict

from core.account.AccountRepository import AccountRepository
from core.account.CreditCardAccount import CreditCardAccount
from core.transaction.TransactionRepository import TransactionRepository

class AnalyticsProcessor:
    def __init__(self, txn_repo: TransactionRepository, acc_repo: AccountRepository):
        self._txn_repo = txn_repo
        self._acc_repo = acc_repo

    def get_total_net_worth(self, user_id: str) -> Decimal:
        """Calculates total assets minus total liabilities
           Credit Card balances represent debt (liabilities), so they are subtracted
           All other accounts represent assets and are added"""
        accounts = self._acc_repo.fetch_all_accounts(user_id)
        net_worth = Decimal('0.00')

        for acc in accounts:
            if isinstance(acc, CreditCardAccount):
                net_worth -= acc.balance
            else:
                net_worth += acc.balance

        return net_worth

    def get_debt_to_credit_ratio(self, user_id: str) -> float:
        """Calculates the ratio of total credit card debt to total credit limits
           Returns a float between 0.0 and 1.0 (or higher if over limit)"""
        accounts = self._acc_repo.fetch_all_accounts(user_id)
        total_debt = Decimal('0.00')
        total_credit_limit = Decimal('0.00')

        for acc in accounts:
            if isinstance(acc, CreditCardAccount):
                total_debt += acc.balance
                total_credit_limit += acc.credit_limit

        if total_credit_limit == Decimal('0.00'):
            return 0.0

        return float(total_debt / total_credit_limit)

    def format_category_data_for_charts(self, account_id: UUID) -> Dict[str, float]:
        """Fetches category spending and converts Decimals to floats for PyQt"""
        raw_data = self._txn_repo.get_total_spending_by_category(account_id)
        return {category: float(amount) for category, amount in raw_data.items()}

    def format_vendor_data_for_charts(self, account_id: UUID) -> Dict[str, float]:
        """Fetches vendor spending and converts Decimals to floats for UI charting"""
        raw_data = self._txn_repo.get_total_spending_by_vendor(account_id)

        return {vendor: float(amount) for vendor, amount in raw_data.items()}