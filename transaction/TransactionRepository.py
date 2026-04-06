import sqlite3
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import List, Dict
from .Transaction import Transaction

class TransactionRepository:
    def __init__(self, db_connection_path: str):
        self.db_path = db_connection_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def fetch_transactions(self, account_id: UUID) -> List[Transaction]:
        query = """
            SELECT 
                t.transaction_id, t.account_id, t.vendor_id, v.vendor_name, 
                t.category_id, c.category_name, t.amount, t.transaction_date, t.transaction_type
            FROM transactions t
            JOIN vendors v ON t.vendor_id = v.vendor_id
            JOIN categories c ON t.category_id = c.category_id
            WHERE t.account_id = ?
            ORDER BY t.transaction_date DESC
        """
        transactions = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (str(account_id),))
            for row in cursor.fetchall():
                transactions.append(Transaction(
                    txn_id = UUID(row[0]),
                    account_id = UUID(row[1]),
                    vendor_id = row[2],
                    vendor_name = row[3],
                    category_id = row[4],
                    category_name = row[5],
                    amount = Decimal(str(row[6])),
                    date = datetime.fromisoformat(row[7]),
                    txn_type = row[8]
                ))
        return transactions

    def save_transaction(self, txn_obj: Transaction) -> None:
        query = """
            INSERT INTO transactions (transaction_id, account_id, vendor_id, category_id, amount, transaction_date, transaction_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                str(txn_obj.id),
                str(txn_obj.account_id),
                txn_obj.vendor_id,
                txn_obj.category_id,
                float(txn_obj.amount),
                txn_obj.date.isoformat(), # Fixed: Using public property
                txn_obj.type
            ))
            conn.commit()

    def delete_transaction(self, txn_id: UUID) -> None:
        query = "DELETE FROM transactions WHERE transaction_id = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (str(txn_id),))
            conn.commit()

    def update_category(self, txn_id: UUID, new_category_id: int) -> None:
        query = "UPDATE transactions SET category_id = ? WHERE transaction_id = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (new_category_id, str(txn_id)))
            conn.commit()

    def get_total_spending_by_category(self, account_id: UUID) -> Dict[str, Decimal]:
        query = """
            SELECT c.category_name, SUM(t.amount)
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
            WHERE t.account_id = ? AND t.transaction_type = 'EXPENSE'
            GROUP BY c.category_name
        """
        totals = {}
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (str(account_id),))
            for row in cursor.fetchall():
                totals[row[0]] = Decimal(str(row[1]))
        return totals

    def get_total_spending_by_vendor(self, account_id: UUID) -> Dict[str, Decimal]:
        """Aggregates EXPENSE totals grouped by vendor name for a specific account."""
        query = """
                SELECT v.vendor_name, SUM(t.amount)
                FROM transactions t
                         JOIN vendors v ON t.vendor_id = v.vendor_id
                WHERE t.account_id = ? \
                  AND t.transaction_type = 'EXPENSE'
                GROUP BY v.vendor_name \
                """
        totals = {}
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (str(account_id),))
            for row in cursor.fetchall():
                totals[row[0]] = Decimal(str(row[1]))
        return totals