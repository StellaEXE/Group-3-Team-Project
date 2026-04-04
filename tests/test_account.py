import uuid
from decimal import Decimal
from account.CheckingAccount import CheckingAccount
from account.SavingsAccount import SavingsAccount
from account.CreditCardAccount import CreditCardAccount
from account.DebitCardAccount import DebitCardAccount


# --- HELPER FOR TESTING ---
class MockTransaction:
    def __init__(self, txn_id):
        self.id = txn_id


def test_accounts():
    # Setup shared data
    acc_num_enc = b'encrypted_acc_number'
    cvv_enc = b'encrypted_cvv'

    # --- ACCOUNT ---
    print("Testing Base Account Logic...")
    checking = CheckingAccount(uuid.uuid4(), "Test Checking", Decimal('1000.00'), acc_num_enc, "123456789")

    checking.deposit(Decimal('500.00'))
    assert checking.balance == Decimal('1500.00')

    checking.withdraw(Decimal('200.00'))
    assert checking.balance == Decimal('1300.00')

    # Fix: Wrap the ID in a MockTransaction object
    txn_id = uuid.uuid4()
    mock_txn = MockTransaction(txn_id)

    checking.add_transaction(mock_txn)
    assert len(checking.get_transactions()) == 1

    checking.remove_transaction(txn_id)
    assert len(checking.get_transactions()) == 0
    print("Base Account tests passed.\n")

    # --- CHECKING ACCOUNT ---
    print("Testing Checking Account...")
    checking_acc = CheckingAccount(uuid.uuid4(), "Student Checking", Decimal('500.00'), acc_num_enc, "074029032")
    assert checking_acc.routing_number == "074029032"
    print("Checking Account tests passed.\n")

    # --- SAVINGS ACCOUNT ---
    print("Testing Savings Account...")
    savings = SavingsAccount(uuid.uuid4(), "Emergency Fund", Decimal('10000.00'), acc_num_enc, Decimal('0.045'))

    interest = savings.calculate_monthly_interest()
    assert interest == Decimal('37.50')

    savings.apply_interest()
    assert savings.balance == Decimal('10037.50')
    print("Savings Account tests passed.\n")

    # --- CREDIT CARD ACCOUNT ---
    print("Testing Credit Card Account...")
    credit = CreditCardAccount(uuid.uuid4(), "Titanium Rewards", Decimal('500.00'), acc_num_enc, cvv_enc,
                               Decimal('15000.00'), Decimal('0.24'))

    charge = credit.calculate_interest_charge(Decimal('500.00'))
    assert charge == Decimal('10.00')

    credit.apply_interest_charge(Decimal('500.00'))
    assert credit.balance == Decimal('510.00')
    print("Credit Card Account tests passed.\n")

    # --- DEBIT CARD ACCOUNT ---
    print("Testing Debit Card Account...")
    linked_id = uuid.uuid4()
    debit = DebitCardAccount(uuid.uuid4(), "Daily Swipe", Decimal('100.00'), acc_num_enc, cvv_enc, linked_id)
    assert debit.linked_checking_id == linked_id
    print("Debit Card Account tests passed.\n")

    print("All account tests completed successfully!")


if __name__ == "__main__":
    test_accounts()