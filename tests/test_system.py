import uuid
import os
import sqlite3
import pytest
import tempfile
import gc
from decimal import Decimal
from datetime import datetime
from matplotlib.figure import Figure

# --- SECURITY & STATE ---
from auth.AuthenticationService import AuthenticationService
from auth.UserSession import UserSession

# --- DOMAIN MODELS ---
from account.CheckingAccount import CheckingAccount
from account.CreditCardAccount import CreditCardAccount
from transaction.Transaction import Transaction

# --- DATA PERSISTENCE ---
from account.AccountRepository import AccountRepository
from transaction.TransactionRepository import TransactionRepository

# --- ANALYTICS & VISUALIZATION ---
from analytics.AnalyticsProcessor import AnalyticsProcessor
from visualizer.PieChartVisualizer import PieChartVisualizer
from visualizer.BarGraphVisualizer import BarGraphVisualizer

@pytest.fixture
def integration_db():
    """Sets up the full relational database schema for end-to-end testing."""
    fd, db_path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Security
    cursor.execute(
        "CREATE TABLE users (user_id TEXT PRIMARY KEY, username TEXT UNIQUE, password_hash BLOB, encryption_salt BLOB)")

    # Account
    cursor.execute(
        "CREATE TABLE accounts (account_id TEXT PRIMARY KEY, user_id TEXT, account_name TEXT, account_type TEXT, enc_acc_num BLOB)")
    cursor.execute("CREATE TABLE checking_details (account_id TEXT PRIMARY KEY, routing_number TEXT)")
    cursor.execute("CREATE TABLE savings_details (account_id TEXT PRIMARY KEY, interest_rate REAL)")  # ADDED
    cursor.execute("CREATE TABLE credit_card_details (account_id TEXT PRIMARY KEY, enc_cvv BLOB, credit_limit REAL)")
    cursor.execute(
        "CREATE TABLE debit_card_details (account_id TEXT PRIMARY KEY, enc_cvv BLOB, linked_checking_id TEXT)")  # ADDED

    # Transactions Data
    cursor.execute("CREATE TABLE categories (category_id INTEGER PRIMARY KEY, category_name TEXT UNIQUE)")
    cursor.execute(
        "CREATE TABLE vendors (vendor_id INTEGER PRIMARY KEY, vendor_name TEXT UNIQUE, default_category_id INTEGER)")
    cursor.execute("""
                   CREATE TABLE transactions
                   (
                       transaction_id   TEXT PRIMARY KEY,
                       account_id       TEXT,
                       vendor_id        INTEGER,
                       category_id      INTEGER,
                       amount           REAL,
                       transaction_date TEXT,
                       transaction_type TEXT
                   )
                   """)

    # Seed relational data
    cursor.execute("INSERT INTO categories VALUES (1, 'Electronics'), (2, 'Utilities')")
    cursor.execute("INSERT INTO vendors VALUES (1, 'Micro Center', 1), (2, 'Duke Energy', 2)")

    conn.commit()
    conn.close()

    yield db_path

    # Clear Singleton and temp files
    UserSession().clear_session()
    gc.collect()
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            pass

def test_full_system_workflow(integration_db):
    """Verifies Security -> Repositories -> Models -> Analytics -> Charts"""
    print("\n--- Starting Full System Integration Test ---")

    # --- SECURITY & AUTHENTICATION ---
    auth = AuthenticationService()
    user_id = "stella_exe"
    password = "SuperSecurePassword123!"
    salt = os.urandom(16)

    # Hash password and derive the encryption key
    pwd_hash = auth.hash_password(password)
    derived_key = auth.derive_aes_key(password, salt)

    # Save user to DB manually
    with sqlite3.connect(integration_db) as conn:
        conn.execute("INSERT INTO users VALUES (?, ?, ?, ?)",
                     (user_id, "Stella", pwd_hash, salt))

    # Initialize Singleton UserSession
    session = UserSession()
    session.start_session(user_id, derived_key)
    assert session.active_user_id == user_id
    print("[SUCCESS] Security: User authenticated and session key derived.")

    # --- DATA PERSISTENCE (ACCOUNTS) ---
    acc_repo = AccountRepository(integration_db)

    # Create and encrypt a Checking Account
    check_id = uuid.uuid4()
    enc_num = auth.encrypt("123456789", session.get_key())
    checking = CheckingAccount(check_id, "Main Checking", Decimal('0.00'), enc_num, "987654321")
    acc_repo.save_new_account(user_id, checking)

    # Create and encrypt a Credit Card
    cc_id = uuid.uuid4()
    enc_cc_num = auth.encrypt("5555-4444-3333-2222", session.get_key())
    enc_cvv = auth.encrypt("123", session.get_key())
    credit = CreditCardAccount(cc_id, "Rewards Card", Decimal('0.00'), enc_cc_num, enc_cvv, Decimal('5000.00'),
                               Decimal('0.24'))
    acc_repo.save_new_account(user_id, credit)

    print("[SUCCESS] Persistence: Accounts encrypted and saved.")

    # --- DATA PERSISTENCE (TRANSACTIONS) ---
    txn_repo = TransactionRepository(integration_db)

    # 1. Income to Checking ($2000)
    t1 = Transaction(uuid.uuid4(), check_id, 1, "Direct Deposit", 1, "Salary", Decimal('2000.00'), datetime.now(),
                     "INCOME")
    txn_repo.save_transaction(t1)

    # 2. Expense from Credit Card ($500 at Micro Center)
    t2 = Transaction(uuid.uuid4(), cc_id, 1, "Micro Center", 1, "Electronics", Decimal('500.00'), datetime.now(),
                     "EXPENSE")
    txn_repo.save_transaction(t2)

    # Verify Account Balance Reconstruction
    accounts = acc_repo.fetch_all_accounts(user_id)
    # Check balance of specific account objects
    for acc in accounts:
        if acc.id == check_id: assert acc.balance == Decimal('2000.00')
        if acc.id == cc_id: assert acc.balance == Decimal('500.00')  # CC debt is positive

    print("[SUCCESS] Persistence: Transactions logged and balances reconstructed.")

    # --- ANALYTICS ---
    analytics = AnalyticsProcessor(txn_repo, acc_repo)

    # Net Worth: $2000 (Checking) - $500 (CC Debt) = $1500
    net_worth = analytics.get_total_net_worth(user_id)
    assert net_worth == Decimal('1500.00')

    # Debt-to-Credit: $500 debt / $5000 limit = 0.10
    ratio = analytics.get_debt_to_credit_ratio(user_id)
    assert ratio == 0.10

    # Format data for UI
    chart_data = analytics.format_category_data_for_charts(cc_id)
    assert chart_data["Electronics"] == 500.0

    print("[SUCCESS] Analytics: Net worth and credit ratios calculated accurately.")

    # --- VISUALIZATION ---
    pie_viz = PieChartVisualizer()
    bar_viz = BarGraphVisualizer()

    # Generate figures (No .show() to keep the test automated)
    pie_fig = pie_viz.render(chart_data, "Spending Breakdown")
    bar_fig = bar_viz.render(chart_data, "Vendor Analysis")

    assert isinstance(pie_fig, Figure)
    assert isinstance(bar_fig, Figure)

    print("[SUCCESS] Visualization: Chart figures generated and ready for PyQt layout.")
    print("--- FULL SYSTEM INTEGRATION TEST PASSED ---")

if __name__ == "__main__":
    pytest.main([__file__])