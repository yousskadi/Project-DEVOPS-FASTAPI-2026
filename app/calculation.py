def add(num1: int, num2: int):
    return num1 + num2


def subtract(num1: int, num2: int):
    return num1 - num2


def multiply(num1: int, num2: int):
    return num1 * num2

def divide(num1: int, num2: int):
    if num2 == 0:
        raise ValueError("Cannot divide by zero")
    return num1 / num2

class BankAccount():
    def __init__(self, balance: float = 0.0):
        self.balance = balance

    def deposit(self, amount: float):
        self.balance += amount

    def withdraw(self, amount: float):
        if amount > self.balance:
            raise Exception("Insufficient funds")
        self.balance -= amount
