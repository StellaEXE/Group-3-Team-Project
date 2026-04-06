import sqlite3
import uuid
import os
from datetime import datetime, timedelta
from decimal import Decimal

# --- INTERNAL IMPORTS ---
from auth.AuthenticationService import AuthenticationService
from transaction.Transaction import Transaction
from transaction.TransactionRepository import TransactionRepository

# --- CONFIGURATION ---
DB_PATH = 'WealthTrackersDB.sqlite'
USER_ID = "BasilissaOfNuts"
PASSWORD = "ImTooUncFor0rb!t"
EMAIL = "IHateAsymDuals@gmail.com"
PHONE = "777-666-9999"


def seed():
    auth = AuthenticationService()
    txn_repo = TransactionRepository(DB_PATH)
    conn = None
    salt = os.urandom(16)
    password_hash = auth.hash_password(PASSWORD)
    session_key = auth.derive_aes_key(PASSWORD, salt)

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("BEGIN TRANSACTION;")

        # --- CLEANUP ---
        cursor.execute("DELETE FROM users WHERE user_id = ?", (USER_ID,))
        cursor.execute("DELETE FROM vendors;")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='vendors';")

        # --- USER CREATION ---
        enc_email = auth.encrypt(EMAIL, session_key)
        enc_phone = auth.encrypt(PHONE, session_key)

        cursor.execute("""
                       INSERT INTO users (user_id, username, password_hash, encryption_salt, enc_email, enc_phone)
                       VALUES (?, ?, ?, ?, ?, ?)
                       """, (USER_ID, USER_ID, password_hash, salt, enc_email, enc_phone))

        # --- VENDOR SEEDING ---
        # Storing (Vendor ID, Default Category ID) for object creation
        # Categories: 3 = Electronic Deposit, 8 = Shopping, 9 = Entertainment, 10 = Bills, 11 = Food & Dining
        vendors_to_seed = [
            ("MICRO CENTER", 8, "Shopping"),
            ("IVY TECH PAYROLL", 3, "Electronic Deposit"),
            ("ALI'I POKE", 11, "Food & Dining"),
            ("PANDA EXPRESS", 11, "Food & Dining"),
            ("DUKE ENERGY", 10, "Bills & Utilities"),
            ("DISCORD", 9, "Entertainment"),
            ("TWITCH", 9, "Entertainment"),
            ("HOYOVERSE", 9, "Entertainment"),
            ("STEAM", 9, "Entertainment")
        ]

        vendor_map = {}
        for name, cat_id, cat_name in vendors_to_seed:
            cursor.execute("INSERT INTO vendors (vendor_name, default_category_id) VALUES (?, ?)", (name, cat_id))
            vendor_map[name] = {
                "id": cursor.lastrowid,
                "cat_id": cat_id,
                "cat_name": cat_name
            }

        # --- ACCOUNT CREATION ---
        # Checking
        checking_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO accounts VALUES (?, ?, ?, ?, ?)",
                       (checking_id, USER_ID, "Ivy Tech Student Checking", "CHECKING",
                        auth.encrypt("1000999888", session_key)))
        cursor.execute("INSERT INTO checking_details VALUES (?, ?)", (checking_id, "074029032"))

        # Savings
        savings_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO accounts VALUES (?, ?, ?, ?, ?)",
                       (savings_id, USER_ID, "Emergency Fund", "SAVINGS", auth.encrypt("555666777", session_key)))
        cursor.execute("INSERT INTO savings_details VALUES (?, ?)", (savings_id, 0.045))

        # Credit Card
        credit_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO accounts VALUES (?, ?, ?, ?, ?)",
                       (credit_id, USER_ID, "Titanium Rewards Visa", "CREDIT",
                        auth.encrypt("4111222233334444", session_key)))
        cursor.execute("INSERT INTO credit_card_details VALUES (?, ?, ?)",
                       (credit_id, auth.encrypt("999", session_key), 15000.00))

        # Debit Card
        debit_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO accounts VALUES (?, ?, ?, ?, ?)",
                       (debit_id, USER_ID, "Daily Swipe Card", "DEBIT", auth.encrypt("5111222233334444", session_key)))
        cursor.execute("INSERT INTO debit_card_details VALUES (?, ?, ?)",
                       (debit_id, auth.encrypt("111", session_key), checking_id))

        conn.commit()  # Commit structural changes before using TransactionRepository

        # --- TRANSACTION SEEDING ---
        # Using the TransactionRepository for object-oriented insertion

        # Transaction 1: RTX 5090 Purchase
        vm = vendor_map["MICRO CENTER"]
        txn_repo.save_transaction(Transaction(
            uuid.uuid4(), uuid.UUID(credit_id), vm["id"], "MICRO CENTER",
            vm["cat_id"], vm["cat_name"], Decimal("3999.99"), datetime.now(), 'EXPENSE'
        ))

        # Transaction 2: Monthly Salary
        vm = vendor_map["IVY TECH PAYROLL"]
        txn_repo.save_transaction(Transaction(
            uuid.uuid4(), uuid.UUID(checking_id), vm["id"], "IVY TECH PAYROLL",
            vm["cat_id"], vm["cat_name"], Decimal("3500.00"), datetime.now() - timedelta(days=5), 'INCOME'
        ))

        # Transaction 3: Poke Bowl Delivery
        vm = vendor_map["ALI'I POKE"]
        txn_repo.save_transaction(Transaction(
            uuid.uuid4(), uuid.UUID(debit_id), vm["id"], "ALI'I POKE",
            vm["cat_id"], vm["cat_name"], Decimal("35.39"), datetime.now(), 'EXPENSE'
        ))

        # Transaction 4: Panda Express Lunch
        vm = vendor_map["PANDA EXPRESS"]
        txn_repo.save_transaction(Transaction(
            uuid.uuid4(), uuid.UUID(debit_id), vm["id"], "PANDA EXPRESS",
            vm["cat_id"], vm["cat_name"], Decimal("15.45"), datetime.now(), 'EXPENSE'
        ))

        # Transaction 5: Monthly Electricity
        vm = vendor_map["DUKE ENERGY"]
        txn_repo.save_transaction(Transaction(
            uuid.uuid4(), uuid.UUID(checking_id), vm["id"], "DUKE ENERGY",
            vm["cat_id"], vm["cat_name"], Decimal("142.50"), datetime.now(), 'EXPENSE'
        ))

        # Transaction 6: Discord Nitro
        vm = vendor_map["DISCORD"]
        txn_repo.save_transaction(Transaction(
            uuid.uuid4(), uuid.UUID(credit_id), vm["id"], "DISCORD",
            vm["cat_id"], vm["cat_name"], Decimal("9.99"), datetime.now(), 'EXPENSE'
        ))

        # Transaction 7: Twitch Subscription
        vm = vendor_map["TWITCH"]
        txn_repo.save_transaction(Transaction(
            uuid.uuid4(), uuid.UUID(credit_id), vm["id"], "TWITCH",
            vm["cat_id"], vm["cat_name"], Decimal("5.99"), datetime.now(), 'EXPENSE'
        ))

        # Transaction 8: Gacha Spending
        vm = vendor_map["HOYOVERSE"]
        txn_repo.save_transaction(Transaction(
            uuid.uuid4(), uuid.UUID(credit_id), vm["id"], "HOYOVERSE",
            vm["cat_id"], vm["cat_name"], Decimal("80.99"), datetime.now(), 'EXPENSE'
        ))

        # Transaction 9: New PC Game
        vm = vendor_map["STEAM"]
        txn_repo.save_transaction(Transaction(
            uuid.uuid4(), uuid.UUID(debit_id), vm["id"], "STEAM",
            vm["cat_id"], vm["cat_name"], Decimal("59.99"), datetime.now(), 'EXPENSE'
        ))

        print(f"--- SEED COMPLETE ---")
        print(f"User: {USER_ID} | Vendors Seeded: {len(vendor_map)}")
        print(f"Transactions Loaded: 9 (Using TransactionRepository)")

    except Exception as e:
        if conn: conn.rollback()
        print(f"Critical Seed Failure: {e}")
    finally:
        if conn: conn.close()


if __name__ == "__main__":
    seed()