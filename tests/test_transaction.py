import uuid
import os
import sqlite3
import pytest
import tempfile
import gc  # Force garbage collection
from decimal import Decimal
from datetime import datetime
from transaction.Transaction import Transaction
from transaction.TransactionRepository import TransactionRepository

# --- FIXTURES (Setup/Teardown) ---

@pytest.fixture
def temp_db():
    """Creates a temporary file-based database for integration testing"""
    fd, db_path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE categories (category_id INTEGER PRIMARY KEY, category_name TEXT)")
    cursor.execute(
        "CREATE TABLE vendors (vendor_id INTEGER PRIMARY KEY, vendor_name TEXT, default_category_id INTEGER)")
    cursor.execute("""
                   CREATE TABLE transactions
                   (
                       transaction_id   TEXT PRIMARY KEY,
                       account_id       TEXT    NOT NULL,
                       vendor_id        INTEGER NOT NULL,
                       category_id      INTEGER NOT NULL,
                       amount           REAL    NOT NULL,
                       transaction_date TEXT    NOT NULL,
                       transaction_type TEXT    NOT NULL
                   )
                   """)

    cursor.execute("INSERT INTO categories VALUES (1, 'Utilities'), (2, 'Food')")
    cursor.execute("INSERT INTO vendors VALUES (1, 'TEST VENDOR', 1)")
    conn.commit()
    conn.close()

    yield db_path

    # Force garbage collection to close any lingering DB connections held by TransactionRepository objects before deleting the file.
    gc.collect()

    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            # Fallback for busy CI environments
            pass

# --- TRANSACTION DOMAIN TESTS ---

def test_transaction_initialization():
    """Tests that the Transaction object correctly stores and returns data"""
    txn_id = uuid.uuid4()
    acc_id = uuid.uuid4()
    now = datetime.now()

    txn = Transaction(
        txn_id=txn_id,
        account_id=acc_id,
        vendor_id=50,
        vendor_name="STEAM",
        category_id=9,
        category_name="Entertainment",
        amount=Decimal("59.99"),
        date=now,
        txn_type="EXPENSE"
    )

    assert txn.id == txn_id
    assert txn.amount == Decimal("59.99")
    details = txn.get_details()
    assert details["vendor"] == "STEAM"
    assert details["amount"] == 59.99

def test_transaction_update_category():
    """Tests the domain logic for updating a category on the fly"""
    txn = Transaction(uuid.uuid4(), uuid.uuid4(), 1, "V", 1, "Old", Decimal("10"), datetime.now(), "EXPENSE")
    txn.update_category(2, "New")
    assert txn.category_id == 2
    assert txn.get_details()["category"] == "New"

# --- REPOSITORY INTEGRATION TESTS ---

def test_repository_save_and_fetch(temp_db):
    """Tests saving a transaction and retrieving it with JOIN-ed names"""
    repo = TransactionRepository(temp_db)
    txn_id = uuid.uuid4()
    acc_id = uuid.uuid4()

    txn = Transaction(
        txn_id=txn_id,
        account_id=acc_id,
        vendor_id=1,
        vendor_name="TEST VENDOR",
        category_id=1,
        category_name="Utilities",
        amount=Decimal("100.00"),
        date=datetime(2026, 4, 5, 12, 0),
        txn_type="EXPENSE"
    )

    repo.save_transaction(txn)
    results = repo.fetch_transactions(acc_id)

    assert len(results) == 1
    assert results[0].id == txn_id
    assert results[0].get_details()["vendor"] == "TEST VENDOR"

def test_repository_delete(temp_db):
    """Tests deletion"""
    repo = TransactionRepository(temp_db)
    txn_id = uuid.uuid4()
    acc_id = uuid.uuid4()

    txn = Transaction(txn_id, acc_id, 1, "V", 1, "C", Decimal("10"), datetime.now(), "EXPENSE")
    repo.save_transaction(txn)
    repo.delete_transaction(txn_id)

    assert len(repo.fetch_transactions(acc_id)) == 0

def test_repository_aggregation(temp_db):
    """Tests the SQL GROUP BY logic for category spending"""
    repo = TransactionRepository(temp_db)
    acc_id = uuid.uuid4()

    t1 = Transaction(uuid.uuid4(), acc_id, 1, "V", 1, "Utilities", Decimal("50.00"), datetime.now(), "EXPENSE")
    t2 = Transaction(uuid.uuid4(), acc_id, 1, "V", 1, "Utilities", Decimal("25.00"), datetime.now(), "EXPENSE")

    repo.save_transaction(t1)
    repo.save_transaction(t2)

    spending = repo.get_total_spending_by_category(acc_id)
    assert spending["Utilities"] == Decimal("75.00")

if __name__ == "__main__":
    pytest.main([__file__])