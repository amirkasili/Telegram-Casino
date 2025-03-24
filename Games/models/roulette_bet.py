from typing import Dict, List
from .bets_polymorphism import BetsPolymorphism
from Accounts.models.bets_service import BetsService
import random


class NotEnteringTheDetails(Exception):
    """Error for not entering bet details."""


class RouletteBetService(BetsPolymorphism):
    """
    🎰 Roulette Bet Service

    Handles roulette betting logic, including placing bets on colors or numbers, 
    spinning the roulette wheel, and determining bet outcomes.
    """

    def __init__(self, amount: float, owner, target_color: str = None, target_numbers: List[int] = None, bet_type: str = "ROULETTE"):
        """
        Initialize a roulette bet.

        Args:
            amount (float): The bet amount.
            owner: The user placing the bet.
            target_color (str, optional): The chosen color ('red', 'black', or 'green'). Defaults to None.
            target_numbers (List[int], optional): The chosen numbers (0-36). Defaults to None.
            bet_type (str, optional): The type of bet. Defaults to "ROULETTE".
        """
        super().__init__(amount, bet_type, owner)
        self.odd = 2  # Default payout multiplier for color bets
        self.target_color = target_color
        self.target_numbers = target_numbers

        # Initialize a BetsService instance for managing bet state
        self.bet = BetsService(
            bet_amount=amount,
            bet_multiplier=self.odd,
            bet_type=bet_type,
            owner=owner
        )

    def to_dict(self) -> Dict:
        """
        Convert the bet details into a dictionary.

        Returns:
            Dict: A dictionary containing bet details.
        """
        return {
            'type': self.bet_type,
            'amount': self.amount,
            'number': self.target_numbers,
            'color': self.target_color,
            'status': self.bet_status
        }

    @staticmethod
    def roulette_spin() -> List:
        """
        Simulates spinning the roulette wheel.

        Returns:
            List: A list containing the spin result [color, number].
        """
        number = random.randint(0, 36)  # Randomly generate a number (0-36)

        # Determine the color based on roulette rules
        if number == 0:
            color = 'green'
        else:
            color = 'red' if number % 2 == 0 else 'black'

        return [color, number]

    def check_winning(self, result: List) -> float:
        """
        Check if the bet wins based on the spin result.

        Args:
            result (List): A list containing the spin result [color, number].

        Returns:
            float: The profit earned from the bet.
        """
        color, number = result  # Extract color and number from the spin result

        # Check if the user bet on color and won
        if self.target_color and self.target_color == color:
            self.change_bet_status(self.BET_STATUS_WON)
            self.bet.change_bet_status(self.bet.BET_STATUS_WON)

        # Check if the user bet on a specific number and won
        elif self.target_numbers and number in self.target_numbers:
            self.change_bet_status(self.BET_STATUS_WON)
            self.bet.change_bet_status(self.bet.BET_STATUS_WON)

        # If no conditions met, the bet is lost
        else:
            self.change_bet_status(self.BET_STATUS_FAILED)
            self.bet.change_bet_status(self.bet.BET_STATUS_FAILED)

        # Calculate the profit/loss from the bet
        self.bet.resolve_bet(self.bet.bet_status)
        profit = self.bet.calculate_profit()
        return profit
