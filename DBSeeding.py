import sqlite3
import uuid
import os
from datetime import datetime, timedelta
from auth.AuthenticationService import AuthenticationService

# --- CONFIGURATION ---
DB_PATH = 'WealthTrackersDB.sqlite'
USER_ID = "BasilissaOfNuts"
PASSWORD = "ImTooUncFor0rb!t"
EMAIL = "IHateAsymDuals@gmail.com"
PHONE = "777-666-9999"


def get_vendor_id(cursor, name):
    # Helper to ensure vendors uniqueness
    cursor.execute("INSERT OR IGNORE INTO vendors (vendor_name) VALUES (?)", (name,))
    cursor.execute("SELECT vendor_id FROM vendors WHERE vendor_name = ?", (name,))

    return cursor.fetchone()[0]

def seed():
    auth = AuthenticationService()
    conn = None
    salt = os.urandom(16)
    password_hash = auth.hash_password(PASSWORD)
    session_key = auth.derive_aes_key(PASSWORD, salt)

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("BEGIN TRANSACTION;")

        # Clean up existing data
        cursor.execute("DELETE FROM users WHERE user_id = ?", (USER_ID,))

        enc_email = auth.encrypt(EMAIL, session_key)
        enc_phone = auth.encrypt(PHONE, session_key)

        cursor.execute("""
                       INSERT INTO users (user_id, username, password_hash, encryption_salt, enc_email, enc_phone)
                       VALUES (?, ?, ?, ?, ?, ?)
                       """, (USER_ID, USER_ID, password_hash, salt, enc_email, enc_phone))

        # Create 1 Account of each type to test
        # --- Checking ---
        checking_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO accounts VALUES (?, ?, ?, ?, ?)",
                       (checking_id, USER_ID, "Ivy Tech Student Checking", "CHECKING",
                        auth.encrypt("1000999888", session_key)))
        cursor.execute("INSERT INTO checking_details VALUES (?, ?)", (checking_id, "074029032"))

        # --- ####### --- (What's a Savings Account?)
        savings_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO accounts VALUES (?, ?, ?, ?, ?)",
                       (savings_id, USER_ID, "Emergency Fund", "SAVINGS", auth.encrypt("555666777", session_key)))
        cursor.execute("INSERT INTO savings_details VALUES (?, ?)", (savings_id, 0.045))  # 4.5% APY

        # --- Credit Card ---
        credit_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO accounts VALUES (?, ?, ?, ?, ?)",
                       (credit_id, USER_ID, "Titanium Rewards Visa", "CREDIT",
                        auth.encrypt("4111222233334444", session_key)))
        cursor.execute("INSERT INTO credit_card_details VALUES (?, ?, ?)",
                       (credit_id, auth.encrypt("999", session_key), 15000.00))

        # --- Debit Card (Linked to Checking) ---
        debit_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO accounts VALUES (?, ?, ?, ?, ?)",
                       (debit_id, USER_ID, "Daily Swipe Card", "DEBIT", auth.encrypt("5111222233334444", session_key)))
        cursor.execute("INSERT INTO debit_card_details VALUES (?, ?, ?)",
                       (debit_id, auth.encrypt("111", session_key), checking_id))

        # Transaction 1: RTX 5090 Purchase (Shopping)
        vid_mc = get_vendor_id(cursor, "Micro Center")
        cursor.execute("""
                       INSERT INTO transactions (transaction_id, account_id, vendor_id, category_id, amount,
                                                 transaction_date, transaction_type)
                       VALUES (?, ?, ?, ?, ?, ?, ?)
                       """, (str(uuid.uuid4()), credit_id, vid_mc, 6, 3999.99, datetime.now().isoformat(), 'EXPENSE'))

        # Transaction 2: Monthly Salary (Income)
        vid_ivy = get_vendor_id(cursor, "Ivy Tech Payroll")
        cursor.execute("""
                       INSERT INTO transactions (transaction_id, account_id, vendor_id, category_id, amount,
                                                 transaction_date, transaction_type)
                       VALUES (?, ?, ?, ?, ?, ?, ?)
                       """, (str(uuid.uuid4()), checking_id, vid_ivy, 2, 3500.00,
                             (datetime.now() - timedelta(days = 5)).isoformat(), 'INCOME'))

        # Transaction C: Eating Out (Food & Dining)
        vid_panda = get_vendor_id(cursor, "Panda Express")
        cursor.execute("""
                       INSERT INTO transactions (transaction_id, account_id, vendor_id, category_id, amount,
                                                 transaction_date, transaction_type)
                       VALUES (?, ?, ?, ?, ?, ?, ?)
                       """, (str(uuid.uuid4()), debit_id, vid_panda, 3, 15.45, datetime.now().isoformat(), 'EXPENSE'))

        conn.commit()
        print(f"--- SEED COMPLETE ---")
        print(f"User: {USER_ID} | PII Encrypted: Yes")
        print(f"Accounts Created: Checking, Savings, Credit, Debit (Linked)")
        print(f"Transactions: Loaded (Includes RTX 5090 Purchase)")

    except Exception as e:
        if conn: conn.rollback()
        print(f"Critical Seed Failure: {e}")
    finally:
        if conn: conn.close()


if __name__ == "__main__":
    seed()