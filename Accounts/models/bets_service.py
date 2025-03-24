from .bet_abstract import BetsServiceAbstract
from Accounts.models.user import User
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class BetsService(BetsServiceAbstract):
    """
    A class representing a bet service that handles placing, resolving, and managing bets.

    Attributes:
        _owner (User): The user who owns the wallet associated with the bet.
        _bet_amount (float): The amount of the bet.
        _multiplier (float): The multiplier for the bet.
        bet_type (str): The type of bet (e.g., Football, Roulette, Limbo).
        bet_status (str): The current status of the bet.

    Methods:
        to_dict(): Convert the bet details into a dictionary for storage or display.
        _calculate_profit(): Calculate the profit based on the bet status and multiplier.
        resolve_bet(status): Resolve the bet by updating its status and adjusting the wallet balance.
        __repr__(): Return a string representation of the bet.
    """

    def __init__(self, bet_type: str, bet_amount: float, bet_multiplier: float, owner: User):
        """
        Initialize the bet service with the bet type, amount, multiplier, and owner.

        Args:
            bet_type (str): The type of bet (e.g., Football, Roulette, Limbo).
            bet_amount (float): The amount of the bet.
            bet_multiplier (float): The multiplier for the bet.
            owner (User): The user who owns the wallet (optional, will create a new Wallet if not provided).

        Raises:
            ValueError: If the user does not have enough balance to place the bet.
        """
        super().__init__(bet_type, bet_amount, bet_multiplier)
        self._owner = owner

        # Check if the owner has a wallet and enough balance to place the bet
        if not self._owner.wallet.have_enough_balance(bet_amount):
            logger.error(f"Insufficient balance for bet: {bet_amount}")
            raise ValueError(
                'You do not have enough balance to bet on this amount.')

        # Reduce the bet amount from the owner's wallet
        self._owner.wallet.withdraw(bet_amount)

    def to_dict(self) -> Dict:
        """
        Convert the bet details into a dictionary for storage or display.

        Returns:
            Dict: A dictionary containing the bet type, amount, multiplier, and status.
        """
        return {
            "type": self.bet_type,
            "amount": self._bet_amount,
            "multiplier": self._multiplier,
            "status": self.bet_status
        }

    def calculate_profit(self) -> float:
        """
        Calculate the profit based on the bet status and multiplier.

        Returns:
            float: The calculated profit (positive if won, negative if lost, bet amount if draw, zero if pending).
        """
        if self.bet_status == BetsServiceAbstract.BET_STATUS_WON:
            profit = self._bet_amount * self._multiplier

        elif self.bet_status == BetsServiceAbstract.BET_STATUS_FAILED:
            profit = -self._bet_amount

        elif self.bet_status == BetsServiceAbstract.BET_STATUS_DRAW:
            profit = self._bet_amount

        else:
            return 0.0

        return profit

    def resolve_bet(self, status: str) -> None:
        """
        Resolve the bet by updating its status and adjusting the owner's wallet balance.

        Args:
            status (str): The status of the bet (BetsServiceAbstract.BET_STATUS_WON or BetsServiceAbstract.BET_STATUS_FAILED).

        Returns:
            None
        """
        self.change_bet_status(status)
        profit = self.calculate_profit()

        # Update the owner's wallet balance based on the bet outcome
        if profit > 0:
            self._owner.wallet.deposit(profit)
        elif profit <= 0:
            # If the bet is lost, the amount is already deducted during the bet placement
            pass

    def __repr__(self) -> str:
        """
        Return a string representation of the bet.

        Returns:
            str: A string displaying the bet details.
        """
        return f"BetsService(type={self.bet_type}, amount={self._bet_amount}, multiplier={self._multiplier}, status={self.bet_status})"
