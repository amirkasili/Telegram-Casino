import logging

logger = logging.getLogger(__name__)


class Wallet:
    """
    A class representing a user's wallet.

    Attributes:
        _balance (float): The current balance of the wallet.

    Methods:
        deposit(amount): Deposits an amount into the wallet.
        withdraw(amount): Withdraws an amount from the wallet.
        have_enough_balance(amount): Checks if the wallet has enough balance.
        __repr__(): Returns a string representation of the wallet.
    """

    def __init__(self):
        """Initialize the wallet with a balance of 0.0."""
        self._balance = 0.0

    @property
    def balance(self) -> float:
        """
        Get the current balance of the user wallet.

        Returns:
            float: The current balance of the user.
        """
        return self._balance

    def deposit(self, amount: float) -> None:
        """
        Deposit an amount into the wallet.

        Args:
            amount (float): The amount to deposit. Must be a positive number.

        Raises:
            ValueError: If the amount is less than or equal to zero.
        """
        if amount <= 0:
            raise ValueError(
                'The amount should be a non-zero and non-negative')
        self._balance += amount
        logger.debug(
            f"Deposited {amount:.2f}. New balance: {self._balance:.2f}")

    def withdraw(self, amount: float) -> None:
        """
        Withdraw an amount from the wallet.

        Args:
            amount (float): The amount to withdraw. Must be a positive number.

        Raises:
            ValueError: If the amount exceeds the balance or the balance is zero.
        """
        if amount > self._balance:
            raise ValueError("Insufficient balance for withdrawal")
        if self._balance == 0:
            raise ValueError("No balance available for withdrawal")
        self._balance -= amount
        logger.debug(
            f"Withdrew {amount:.2f}. New balance: {self._balance:.2f}")

    def have_enough_balance(self, amount: float) -> bool:
        """
        Check if the user has enough balance.

        Args:
            amount (float): The amount to check.

        Returns:
            bool: True if the user has enough balance, False otherwise.
        """
        return self._balance >= amount

    def __repr__(self) -> str:
        """
        Return a string representation of the wallet including its balance.

        Returns:
            str: A string displaying the wallet's balance.
        """
        return f"Wallet(balance={self._balance:.2f})"
