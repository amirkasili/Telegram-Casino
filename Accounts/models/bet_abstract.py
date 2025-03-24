from typing import Dict
from abc import ABC, abstractmethod


class BetsServiceAbstract(ABC):
    """
    An abstract class representing a bet service.

    Attributes:
        BET_STATUS_WON (str): Status indicating the bet was won.
        BET_STATUS_FAILED (str): Status indicating the bet was lost.
        BET_STATUS_PENDING (str): Status indicating the bet is pending.
        VALID_STATUSES (List[str]): List of valid bet statuses.

        bet_type (str): The type of bet.
        _bet_amount (float): The amount of the bet.
        _multiplier (float): The multiplier for the bet.
        bet_status (str): The current status of the bet.
    """

    BET_STATUS_WON = 'WON'
    BET_STATUS_FAILED = 'FAILED'
    BET_STATUS_DRAW = 'DRAW'
    BET_STATUS_PENDING = 'PENDING'
    VALID_STATUSES = [BET_STATUS_WON, BET_STATUS_FAILED, BET_STATUS_DRAW]

    def __init__(self, bet_type: str, bet_amount: float, bet_multiplier: float):
        """
        Initialize a bet with its type, amount, and multiplier.

        Args:
            bet_type (str): The type of bet.
            bet_amount (float): The amount of the bet.
            bet_multiplier (float): The multiplier for the bet.
        """
        self.bet_type: str = bet_type
        self._bet_amount: float = bet_amount
        self._multiplier: float = bet_multiplier
        self.bet_status = self.BET_STATUS_PENDING

    @abstractmethod
    def to_dict(self) -> Dict:
        """
        Convert the bet details into a dictionary for serialization or storage.

        Returns:
            Dict: A dictionary containing the bet type, amount, multiplier, and status.
        """
        pass

    @abstractmethod
    def calculate_profit(self) -> float:
        """
        Calculate the profit based on the bet status and multiplier.

        Returns:
            float: The amount of profit (positive if won, negative if lost).
        """
        pass

    def change_bet_status(self, status: str) -> None:
        """
        Change the status of the bet to either 'WON' or 'FAILED'.

        Args:
            status (str): The new status of the bet.

        Raises:
            ValueError: If the status is not 'WON' or 'FAILED'.
        """
        if status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid bet status. Must be one of {self.VALID_STATUSES}.")
        self.bet_status = status
