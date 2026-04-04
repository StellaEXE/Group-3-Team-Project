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


def seed():
    auth = AuthenticationService()
    conn = None
    salt = os.urandom(16)
    password_hash = auth.hash_password(PASSWORD)
    session_key = auth.derive_aes_key(PASSWORD, salt)

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Enable foreign keys for the default_category_id link
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

        # --- VENDOR SEEDING (With Default Categories) ---
        # IDs based on category list: 3 = Electronic Deposit, 8 = Shopping, 9 = Entertainment, 10 = Bills, 11 = Food & Dining
        vendors_to_seed = [
            ("MICRO CENTER", 8),
            ("IVY TECH PAYROLL", 3),
            ("ALI'I POKE", 11),
            ("PANDA EXPRESS", 11),
            ("DUKE ENERGY", 10),
            ("DISCORD", 9),
            ("TWITCH", 9),
            ("HOYOVERSE", 9),
            ("STEAM", 9)
        ]

        vendor_map = {}
        for name, cat_id in vendors_to_seed:
            cursor.execute("INSERT INTO vendors (vendor_name, default_category_id) VALUES (?, ?)", (name, cat_id))
            vendor_map[name] = cursor.lastrowid

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

        # --- TRANSACTION SEEDING (One per Vendor) ---

        # Transaction 1: RTX 5090 Purchase (Shopping)
        cursor.execute("""
                       INSERT INTO transactions (transaction_id, account_id, vendor_id, category_id, amount,
                                                 transaction_date, transaction_type)
                       VALUES (?, ?, ?, (SELECT default_category_id FROM vendors WHERE vendor_id = ?),
                               3999.99, ?, 'EXPENSE')
                       """, (str(uuid.uuid4()), credit_id, vendor_map["MICRO CENTER"],
                             vendor_map["MICRO CENTER"], datetime.now().isoformat()))

        # Transaction 2: Monthly Salary (Electronic Deposit)
        cursor.execute("""
                       INSERT INTO transactions (transaction_id, account_id, vendor_id, category_id, amount,
                                                 transaction_date, transaction_type)
                       VALUES (?, ?, ?, (SELECT default_category_id FROM vendors WHERE vendor_id = ?),
                               3500.00, ?, 'INCOME')
                       """, (str(uuid.uuid4()), checking_id, vendor_map["IVY TECH PAYROLL"],
                             vendor_map["IVY TECH PAYROLL"], (datetime.now() - timedelta(days=5)).isoformat()))

        # Transaction 3: Poke Bowl Delivery (Food & Dining)
        cursor.execute("""
                       INSERT INTO transactions (transaction_id, account_id, vendor_id, category_id, amount,
                                                 transaction_date, transaction_type)
                       VALUES (?, ?, ?, (SELECT default_category_id FROM vendors WHERE vendor_id = ?),
                               35.39, ?, 'EXPENSE')
                       """, (str(uuid.uuid4()), debit_id, vendor_map["ALI'I POKE"],
                             vendor_map["ALI'I POKE"], datetime.now().isoformat()))

        # Transaction 4: Panda Express Lunch (Food & Dining)
        cursor.execute("""
                       INSERT INTO transactions (transaction_id, account_id, vendor_id, category_id, amount,
                                                 transaction_date, transaction_type)
                       VALUES (?, ?, ?, (SELECT default_category_id FROM vendors WHERE vendor_id = ?),
                               15.45, ?, 'EXPENSE')
                       """, (str(uuid.uuid4()), debit_id, vendor_map["PANDA EXPRESS"],
                             vendor_map["PANDA EXPRESS"], datetime.now().isoformat()))

        # Transaction 5: Monthly Electricity (Bills)
        cursor.execute("""
                       INSERT INTO transactions (transaction_id, account_id, vendor_id, category_id, amount,
                                                 transaction_date, transaction_type)
                       VALUES (?, ?, ?, (SELECT default_category_id FROM vendors WHERE vendor_id = ?),
                               142.50, ?, 'EXPENSE')
                       """, (str(uuid.uuid4()), checking_id, vendor_map["DUKE ENERGY"],
                             vendor_map["DUKE ENERGY"], datetime.now().isoformat()))

        # Transaction 6: Discord Nitro (Entertainment)
        cursor.execute("""
                       INSERT INTO transactions (transaction_id, account_id, vendor_id, category_id, amount,
                                                 transaction_date, transaction_type)
                       VALUES (?, ?, ?, (SELECT default_category_id FROM vendors WHERE vendor_id = ?),
                               9.99, ?, 'EXPENSE')
                       """, (str(uuid.uuid4()), credit_id, vendor_map["DISCORD"],
                             vendor_map["DISCORD"], datetime.now().isoformat()))

        # Transaction 7: Twitch Subscription (Entertainment)
        cursor.execute("""
                       INSERT INTO transactions (transaction_id, account_id, vendor_id, category_id, amount,
                                                 transaction_date, transaction_type)
                       VALUES (?, ?, ?, (SELECT default_category_id FROM vendors WHERE vendor_id = ?),
                               5.99, ?, 'EXPENSE')
                       """, (str(uuid.uuid4()), credit_id, vendor_map["TWITCH"],
                             vendor_map["TWITCH"], datetime.now().isoformat()))

        # Transaction 8: Gacha / In-game Currency (Entertainment)
        cursor.execute("""
                       INSERT INTO transactions (transaction_id, account_id, vendor_id, category_id, amount,
                                                 transaction_date, transaction_type)
                       VALUES (?, ?, ?, (SELECT default_category_id FROM vendors WHERE vendor_id = ?),
                               80.99, ?, 'EXPENSE')
                       """, (str(uuid.uuid4()), credit_id, vendor_map["HOYOVERSE"],
                             vendor_map["HOYOVERSE"], datetime.now().isoformat()))

        # Transaction 9: New PC Game (Entertainment)
        cursor.execute("""
                       INSERT INTO transactions (transaction_id, account_id, vendor_id, category_id, amount,
                                                 transaction_date, transaction_type)
                       VALUES (?, ?, ?, (SELECT default_category_id FROM vendors WHERE vendor_id = ?),
                               59.99, ?, 'EXPENSE')
                       """, (str(uuid.uuid4()), debit_id, vendor_map["STEAM"],
                             vendor_map["STEAM"], datetime.now().isoformat()))

        conn.commit()
        print(f"--- SEED COMPLETE ---")
        print(f"User: {USER_ID} | Vendors Seeded: {len(vendor_map)}")
        print(f"Transactions Loaded: 9 (One per vendor)")

    except Exception as e:
        if conn: conn.rollback()
        print(f"Critical Seed Failure: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    seed()