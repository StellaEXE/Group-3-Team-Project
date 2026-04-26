import sqlite3
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
        """Fetches all accounts for a user and reconstructs their current balances"""

        # This query joins all possible detail tables and calculates the dynamic balance
        # It handles Credit Cards differently, as expenses should INCREASE the (debt) balance
        query = """
                SELECT a.account_id, 
                       a.account_name, 
                       a.account_type, 
                       a.enc_acc_num, 
                       c.routing_number, 
                       s.interest_rate, 
                       cc.enc_cvv                                       AS cc_enc_cvv, 
                       cc.credit_limit, 
                       dc.enc_cvv                                       AS dc_enc_cvv, 
                       dc.linked_checking_id, 
                       COALESCE((SELECT SUM(CASE
                                                WHEN t.transaction_type IN ('INCOME', 'TRANSFER_IN') THEN
                                                    CASE WHEN a.account_type = 'CREDIT' THEN -t.amount ELSE t.amount END
                                                WHEN t.transaction_type IN ('EXPENSE', 'TRANSFER_OUT') THEN
                                                    CASE WHEN a.account_type = 'CREDIT' THEN t.amount ELSE -t.amount END
                                                ELSE 0 
                           END)
                                 FROM transactions t 
                                 WHERE t.account_id = a.account_id), 0) as reconstructed_balance
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
        """Factory method to construct the correct Account subclass from SQL."""
        account_id = UUID(row[0])
        name = row[1]
        acc_type = row[2]
        enc_acc_num = row[3]
        balance = Decimal(str(row[10]))  # The reconstructed balance

        if acc_type == 'CHECKING':
            return CheckingAccount(account_id, name, balance, enc_acc_num, routing_number=row[4])

        elif acc_type == 'SAVINGS':
            return SavingsAccount(account_id, name, balance, enc_acc_num, interest_rate=Decimal(str(row[5])))

        elif acc_type == 'CREDIT':
            return CreditCardAccount(account_id, name, balance, enc_acc_num,
                                     enc_cvv=row[6], credit_limit=Decimal(str(row[7])),
                                     apr=Decimal('0.24'))  # Placeholder APR

        elif acc_type == 'DEBIT':
            return DebitCardAccount(account_id, name, balance, enc_acc_num,
                                    enc_cvv=row[8], linked_checking_id=UUID(row[9]))

        raise ValueError(f"Unknown account type: {acc_type}")

    def save_new_account(self, user_id: str, account: Account) -> None:
        """Saves a new account to the base table and its specific details table"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Determine type string based on instance
            # Using a dictionary to map the class type to the SQL string constant
            type_map = {
                CheckingAccount: 'CHECKING',
                SavingsAccount: 'SAVINGS',
                CreditCardAccount: 'CREDIT',
                DebitCardAccount: 'DEBIT'
            }

            acc_type = type_map.get(account.__class__)

            if not acc_type:
                raise ValueError(f"Unsupported Account subclass: {type(account)}")

            # 2. Insert into Base accounts table
            # Accessing protected _enc_acc_num for database persistence
            cursor.execute("""
                           INSERT INTO accounts (account_id, user_id, account_name, account_type, enc_acc_num)
                           VALUES (?, ?, ?, ?, ?)
                           """, (str(account.id), user_id, account.name, acc_type, account._enc_acc_num))

            # 3. Insert into Specific Details table
            if isinstance(account, CheckingAccount):
                cursor.execute("INSERT INTO checking_details (account_id, routing_number) VALUES (?, ?)",
                               (str(account.id), account.routing_number))

            elif isinstance(account, SavingsAccount):
                cursor.execute("INSERT INTO savings_details (account_id, interest_rate) VALUES (?, ?)",
                               (str(account.id), float(account.interest_rate)))

            elif isinstance(account, CreditCardAccount):
                cursor.execute("INSERT INTO credit_card_details (account_id, enc_cvv, credit_limit) VALUES (?, ?, ?)",
                               (str(account.id), account._enc_cvv, float(account.credit_limit)))

            elif isinstance(account, DebitCardAccount):
                cursor.execute(
                    "INSERT INTO debit_card_details (account_id, enc_cvv, linked_checking_id) VALUES (?, ?, ?)",
                    (str(account.id), account._enc_cvv, str(account.linked_checking_id)))

            conn.commit()

    def delete_financial_account(self, account_id: UUID) -> bool:
        """Permanently removes an account. Cascades automatically to transactions and detail tables."""
        query = "DELETE FROM accounts WHERE account_id = ?"

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # The parameterized query handles the UUID string safely
                cursor.execute(query, (str(account_id),))
                conn.commit()

                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Database execution error: {e}")
            return False