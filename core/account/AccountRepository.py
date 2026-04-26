import sqlite3
import uuid
from uuid import UUID
from decimal import Decimal
from typing import List

from core.account.Account import Account
from core.account.CheckingAccount import CheckingAccount
from core.account.SavingsAccount import SavingsAccount
from core.account.CreditCardAccount import CreditCardAccount
from core.account.DebitCardAccount import DebitCardAccount

class AccountRepository:
    def __init__(self, db_connection_path: str):
        self.db_path = db_connection_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def fetch_all_accounts(self, user_id: str) -> List[Account]:
        """Fetches all accounts and calculates 'Tied' balances for Checking/Debit pairs."""

        # This query calculates the balance by looking at the account's own transactions
        # PLUS transactions from any linked debit cards if it is a checking account.
        query = """
                SELECT a.account_id,
                       a.account_name,
                       a.account_type,
                       a.enc_acc_num,
                       c.routing_number,
                       s.interest_rate,
                       cc.enc_cvv,
                       cc.credit_limit,
                       dc.enc_cvv,
                       dc.linked_checking_id,
                       COALESCE((SELECT SUM(CASE \
                                                WHEN t.transaction_type IN ('INCOME', 'TRANSFER_IN') THEN \
                                                    CASE WHEN a2.account_type = 'CREDIT' THEN -t.amount ELSE t.amount END \
                                                WHEN t.transaction_type IN ('EXPENSE', 'TRANSFER_OUT') THEN \
                                                    CASE WHEN a2.account_type = 'CREDIT' THEN t.amount ELSE -t.amount END \
                                                ELSE 0 END) \
                                 FROM transactions t \
                                          JOIN accounts a2 ON t.account_id = a2.account_id \
                                 WHERE ( \
                                           /* Standard Case: Transaction belongs to this account */ \
                                           t.account_id = a.account_id \
                                               OR \
                                               /* Checking Case: Include transactions from linked debit cards */ \
                                           (a.account_type = 'CHECKING' AND t.account_id IN (SELECT account_id \
                                                                                             FROM debit_card_details \
                                                                                             WHERE linked_checking_id = a.account_id)) \
                                               OR \
                                               /* Debit Case: Include transactions from the parent checking account */ \
                                           (a.account_type = 'DEBIT' AND t.account_id = (SELECT linked_checking_id \
                                                                                         FROM debit_card_details \
                                                                                         WHERE account_id = a.account_id)) \
                                           )), 0) as tied_balance
                FROM accounts a
                         LEFT JOIN checking_details c ON a.account_id = c.account_id
                         LEFT JOIN savings_details s ON a.account_id = s.account_id
                         LEFT JOIN credit_card_details cc ON a.account_id = cc.account_id
                         LEFT JOIN debit_card_details dc ON a.account_id = dc.account_id
                WHERE a.user_id = ?
                """

        accounts = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (user_id,))
            for row in cursor.fetchall():
                accounts.append(self._map_to_subclass(row))
        return accounts

    @staticmethod
    def _map_to_subclass(row: tuple) -> Account:
        account_id = UUID(row[0])
        name = row[1]
        acc_type = row[2]
        enc_acc_num = row[3]
        balance = Decimal(str(row[10]))

        if acc_type == 'CHECKING':
            return CheckingAccount(account_id, name, balance, enc_acc_num, routing_number=row[4])
        elif acc_type == 'SAVINGS':
            return SavingsAccount(account_id, name, balance, enc_acc_num, interest_rate=Decimal(str(row[5])))
        elif acc_type == 'CREDIT':
            return CreditCardAccount(account_id, name, balance, enc_acc_num, enc_cvv=row[6],
                                     credit_limit=Decimal(str(row[7])), apr=Decimal('0.24'))
        elif acc_type == 'DEBIT':
            return DebitCardAccount(account_id, name, balance, enc_acc_num, enc_cvv=row[8],
                                    linked_checking_id=UUID(row[9]))
        raise ValueError(f"Unknown type: {acc_type}")

    def save_new_account(self, user_id: str, account: Account) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            type_map = {CheckingAccount: 'CHECKING', SavingsAccount: 'SAVINGS',
                        CreditCardAccount: 'CREDIT', DebitCardAccount: 'DEBIT'}
            acc_type = type_map.get(account.__class__)

            cursor.execute("INSERT INTO accounts VALUES (?, ?, ?, ?, ?)",
                           (str(account.id), user_id, account.name, acc_type, account._enc_acc_num))

            if isinstance(account, CheckingAccount):
                cursor.execute("INSERT INTO checking_details VALUES (?, ?)", (str(account.id), account.routing_number))
            elif isinstance(account, SavingsAccount):
                cursor.execute("INSERT INTO savings_details VALUES (?, ?)",
                               (str(account.id), float(account.interest_rate)))
            elif isinstance(account, CreditCardAccount):
                cursor.execute("INSERT INTO credit_card_details VALUES (?, ?, ?)",
                               (str(account.id), account._enc_cvv, float(account.credit_limit)))
            elif isinstance(account, DebitCardAccount):
                cursor.execute("INSERT INTO debit_card_details VALUES (?, ?, ?)",
                               (str(account.id), account._enc_cvv, str(account.linked_checking_id)))

            # Seed initial balance
            if account.balance > 0:
                cursor.execute("INSERT INTO transactions VALUES (?, ?, 2, 3, ?, datetime('now'), 'INCOME')",
                               (str(uuid.uuid4()), str(account.id), float(account.balance)))
            conn.commit()

    def delete_financial_account(self, account_id: UUID) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM accounts WHERE account_id = ?", (str(account_id),))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False