import pytest

from app.calculation import add, subtract, multiply, divide, BankAccount


@pytest.fixture
def zero_bank_account():
    return BankAccount()

@pytest.fixture
def bank_account():
    return BankAccount(100)


@pytest.mark.parametrize("num1, num2, expected", [
    (5, 3, 8),
    (2, 4, 6),
    (7, 2, 9)
])
def test_add(num1, num2, expected):
    print("Function add run")
    assert add(num1, num2) == expected

def test_subtract():
    print("function subtract")
    assert subtract(5, 3) == 2

def test_multiply():
    print("function multiply")
    assert multiply(5, 3) == 15

def test_divide():
    print("function divide")
    assert divide(15, 5) == 3

### Test class BankAccount
def test_bank_set_initial_amount(bank_account):
    assert bank_account.balance == 100

def test_bank_default_amount(zero_bank_account):
    assert zero_bank_account.balance == 0

def test_bank_withdraw(bank_account):
    bank_account.withdraw(50)
    assert bank_account.balance == 50

def test_bank_deposit(bank_account):
    bank_account.deposit(50)
    assert bank_account.balance == 150

## Test Transaction
@pytest.mark.parametrize("deposit, withdraw, expected", [
    (50, 25, 125),
    (20, 10, 110),
    (30, 15, 115)

])
def test_bank_transaction(bank_account, deposit, withdraw, expected):
    bank_account.deposit(deposit)
    bank_account.withdraw(withdraw)
    assert bank_account.balance == expected

def test_insufficient_funds(bank_account):
    with pytest.raises(Exception):
        bank_account.withdraw(150)
