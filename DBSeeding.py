import sqlite3
import uuid
import os
from datetime import datetime
from decimal import Decimal

# --- INTERNAL IMPORTS ---
from core.auth.AuthenticationService import AuthenticationService
from core.transaction.Transaction import Transaction
from core.transaction.TransactionRepository import TransactionRepository

# --- CONFIGURATION ---
DB_PATH = 'WealthTrackersDB.sqlite'
USER_ID = "BasilissaOfNuts"
PASSWORD = "Im2ooUncFor0r5!t"
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

        # --- GENERIC CATEGORY SEEDING ---
        # We commit these immediately so they are available for the TransactionRepository
        generics = [("General Expense",), ("General Income",)]
        for gen in generics:
            cursor.execute("SELECT category_id FROM categories WHERE category_name = ?", gen)
            if not cursor.fetchone():
                cursor.execute("INSERT INTO categories (category_name) VALUES (?)", gen)

        conn.commit()
        cursor.execute("BEGIN TRANSACTION;")  # Re-open for the rest of the seed

        # --- USER CREATION ---
        enc_email = auth.encrypt(EMAIL, session_key)
        enc_phone = auth.encrypt(PHONE, session_key)
        cursor.execute("""
                       INSERT INTO users (user_id, username, password_hash, encryption_salt, enc_email, enc_phone)
                       VALUES (?, ?, ?, ?, ?, ?)
                       """, (USER_ID, "Basilissa", password_hash, salt, enc_email, enc_phone))

        # --- ACCOUNT CREATION ---
        # We seed a few standard accounts for the test user
        checking_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO accounts VALUES (?, ?, ?, ?, ?)",
                       (checking_id, USER_ID, "Main Checking", "CHECKING", auth.encrypt("123456789", session_key)))
        cursor.execute("INSERT INTO checking_details VALUES (?, ?)", (checking_id, "987654321"))

        savings_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO accounts VALUES (?, ?, ?, ?, ?)",
                       (savings_id, USER_ID, "High Yield Savings", "SAVINGS", auth.encrypt("987654321", session_key)))
        cursor.execute("INSERT INTO savings_details VALUES (?, ?)", (savings_id, 0.045))

        # --- VENDOR SEEDING ---
        # Seeding common vendors with their default categories
        vendors = [
            ('MICRO CENTER', 8), ('ALI\'I POKE', 11), ('PANDA EXPRESS', 11),
            ('DUKE ENERGY', 10), ('DISCORD', 9), ('STEAM', 9), ('HOYOVERSE', 9)
        ]

        vendor_map = {}
        for name, cat_id in vendors:
            cursor.execute("INSERT INTO vendors (vendor_name, default_category_id) VALUES (?, ?)", (name, cat_id))
            vendor_map[name] = {"id": cursor.lastrowid, "cat_id": cat_id}

        # --- TRANSACTION SEEDING ---
        # Using the TransactionRepository to ensure all logic (like shared balance) is triggered

        # Micro Center Purchase
        vm = vendor_map["MICRO CENTER"]
        txn_repo.save_transaction(Transaction(
            uuid.uuid4(), uuid.UUID(checking_id), vm["id"], "MICRO CENTER",
            vm["cat_id"], "Shopping", Decimal("450.00"), datetime.now(), 'EXPENSE'
        ))

        # Discord Subscription
        vm = vendor_map["DISCORD"]
        txn_repo.save_transaction(Transaction(
            uuid.uuid4(), uuid.UUID(checking_id), vm["id"], "DISCORD",
            vm["cat_id"], "Entertainment", Decimal("9.99"), datetime.now(), 'EXPENSE'
        ))

        # Hoyoverse Top-up
        vm = vendor_map["HOYOVERSE"]
        txn_repo.save_transaction(Transaction(
            uuid.uuid4(), uuid.UUID(checking_id), vm["id"], "HOYOVERSE",
            vm["cat_id"], "Entertainment", Decimal("80.99"), datetime.now(), 'EXPENSE'
        ))

        conn.commit()
        print(f"--- SEED COMPLETE ---")
        print(f"User: {USER_ID} created with Main Checking and Savings accounts.")

    except Exception as e:
        if conn: conn.rollback()
        print(f"Critical Seed Failure: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    seed()