import uuid
import pytest
from decimal import Decimal
from unittest.mock import MagicMock

from analytics.AnalyticsProcessor import AnalyticsProcessor
from account.CheckingAccount import CheckingAccount
from account.CreditCardAccount import CreditCardAccount
from account.AccountRepository import AccountRepository
from transaction.TransactionRepository import TransactionRepository


@pytest.fixture
def mock_repos():
    """Provides mocked repositories to isolate Analytics logic"""
    mock_acc_repo = MagicMock(spec=AccountRepository)
    mock_txn_repo = MagicMock(spec=TransactionRepository)

    return mock_txn_repo, mock_acc_repo

def test_get_total_net_worth(mock_repos):
    mock_txn_repo, mock_acc_repo = mock_repos
    processor = AnalyticsProcessor(mock_txn_repo, mock_acc_repo)
    user_id = "user123"

    # Setup mocked accounts: $1500 in Checking, $500 debt on Credit Card
    checking = CheckingAccount(uuid.uuid4(), "Main", Decimal('1500.00'), b'enc', "123")
    credit = CreditCardAccount(uuid.uuid4(), "Visa", Decimal('500.00'), b'enc', b'cvv', Decimal('5000.00'),
                               Decimal('0.24'))

    mock_acc_repo.fetch_all_accounts.return_value = [checking, credit]

    # Net worth should be 1500 - 500 = 1000
    net_worth = processor.get_total_net_worth(user_id)
    assert net_worth == Decimal('1000.00')
    mock_acc_repo.fetch_all_accounts.assert_called_once_with(user_id)

def test_get_debt_to_credit_ratio(mock_repos):
    mock_txn_repo, mock_acc_repo = mock_repos
    processor = AnalyticsProcessor(mock_txn_repo, mock_acc_repo)
    user_id = "user123"

    # Setup 2 credit cards: $500 debt on $5000 limit, $250 debt on $2500 limit
    cc1 = CreditCardAccount(uuid.uuid4(), "Visa", Decimal('500.00'), b'enc', b'cvv', Decimal('5000.00'),
                            Decimal('0.24'))
    cc2 = CreditCardAccount(uuid.uuid4(), "Mastercard", Decimal('250.00'), b'enc', b'cvv', Decimal('2500.00'),
                            Decimal('0.24'))

    mock_acc_repo.fetch_all_accounts.return_value = [cc1, cc2]

    # Total Debt = 750
    # Total Limit = 7500
    # Ratio = 0.10
    ratio = processor.get_debt_to_credit_ratio(user_id)
    assert ratio == 0.10

def test_format_category_data(mock_repos):
    mock_txn_repo, mock_acc_repo = mock_repos
    processor = AnalyticsProcessor(mock_txn_repo, mock_acc_repo)
    acc_id = uuid.uuid4()

    # Mock the DB returning Decimals
    mock_txn_repo.get_total_spending_by_category.return_value = {
        "Food & Dining": Decimal("145.50"),
        "Entertainment": Decimal("59.99")
    }

    # Processor should convert to floats for UI
    formatted_data = processor.format_category_data_for_charts(acc_id)

    assert isinstance(formatted_data["Food & Dining"], float)
    assert formatted_data["Food & Dining"] == 145.50
    assert formatted_data["Entertainment"] == 59.99

if __name__ == "__main__":
    pytest.main([__file__])