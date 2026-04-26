import sqlite3
import uuid
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import List, Dict

from core.transaction.Transaction import Transaction

class TransactionRepository:
    def __init__(self, db_connection_path: str):
        self.db_path = db_connection_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")

        return conn

    def fetch_transactions(self, account_id: UUID) -> List[Transaction]:
        query = """
                SELECT t.transaction_id, \
                       t.account_id, \
                       t.vendor_id, \
                       v.vendor_name,
                       t.category_id, \
                       c.category_name, \
                       t.amount, \
                       t.transaction_date, \
                       t.transaction_type
                FROM transactions t
                         JOIN vendors v ON t.vendor_id = v.vendor_id
                         JOIN categories c ON t.category_id = c.category_id
                WHERE t.account_id = ?
                ORDER BY t.transaction_date DESC \
                """

        return self._execute_fetch(query, (str(account_id),))

    def fetch_user_transactions(self, user_id: str) -> List[Transaction]:
        query = """
                SELECT t.transaction_id, \
                       t.account_id, \
                       t.vendor_id, \
                       v.vendor_name,
                       t.category_id, \
                       c.category_name, \
                       t.amount, \
                       t.transaction_date, \
                       t.transaction_type
                FROM transactions t
                         JOIN accounts a ON t.account_id = a.account_id
                         JOIN vendors v ON t.vendor_id = v.vendor_id
                         JOIN categories c ON t.category_id = c.category_id
                WHERE a.user_id = ?
                ORDER BY t.transaction_date DESC \
                LIMIT 50 \
                """
        return self._execute_fetch(query, (user_id,))

    def _execute_fetch(self, query, params):
        transactions = []
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            for row in cursor.fetchall():
                transactions.append(Transaction(
                    txn_id=UUID(row[0]), account_id=UUID(row[1]),
                    vendor_id=row[2], vendor_name=row[3],
                    category_id=row[4], category_name=row[5],
                    amount=Decimal(str(row[6])),
                    date=datetime.fromisoformat(row[7]),
                    txn_type=row[8]
                ))
        finally:
            conn.close()

        return transactions

    def save_transaction(self, txn_obj: Transaction) -> None:
        """Saves transaction, automatically registering vendors if they don't exist."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # 1. Resolve or Create Vendor
            # We check by name to be safe
            cursor.execute("SELECT vendor_id FROM vendors WHERE vendor_name = ?", (txn_obj.vendor_name,))
            result = cursor.fetchone()

            if result:
                vendor_id = result[0]
            else:
                placeholder = "General Expense" if txn_obj.type in ('EXPENSE', 'TRANSFER_OUT') else "General Income"
                cursor.execute("SELECT category_id FROM categories WHERE category_name = ?", (placeholder,))
                cat_res = cursor.fetchone()
                default_cat = cat_res[0] if cat_res else 1

                cursor.execute("INSERT INTO vendors (vendor_name, default_category_id) VALUES (?, ?)",
                               (txn_obj.vendor_name, default_cat))
                vendor_id = cursor.lastrowid

            # 2. Insert Transaction
            query = """
                    INSERT INTO transactions (transaction_id, account_id, vendor_id, category_id, amount, \
                                              transaction_date, transaction_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?) \
                    """
            cursor.execute(query, (
                str(txn_obj.id), str(txn_obj.account_id), vendor_id,
                txn_obj.category_id, float(txn_obj.amount),
                txn_obj.date.isoformat(), txn_obj.type
            ))

            conn.commit()
        finally:
            conn.close()  # CRITICAL FIX