from typing import Dict
from .bets_polymorphism import BetsPolymorphism
from Accounts.models.bets_service import BetsService
import random


class LimboBetService(BetsPolymorphism):
    """
    🎯 Limbo Bet Service

    Handles limbo betting logic, including placing bets, generating random multipliers,
    and determining whether the bet was successful.
    """

    def __init__(self, amount: float, target_multiplier: float, owner, bet_type: str = 'LIMBO'):
        """
        Initializes a Limbo bet.

        Args:
            amount (float): The bet amount.
            target_multiplier (float): The chosen target multiplier.
            owner: The user placing the bet.
            bet_type (str, optional): The type of bet. Defaults to 'LIMBO'.

        Raises:
            ValueError: If the target multiplier is not between 1 and 10.
        """
        super().__init__(amount, bet_type, owner)
        self.target = target_multiplier

        # Validate multiplier range (must be between 1 and 10)
        if not (1 <= self.target <= 10):
            raise ValueError('❌ Error: Your target multiplier must be between 1 and 10.')

        # Initialize a BetsService instance for managing bet state
        self.bet = BetsService(
            bet_type=self.bet_type,
            bet_amount=self.amount,
            bet_multiplier=self.target,
            owner=owner
        )

    def to_dict(self) -> Dict:
        """
        Converts the bet details into a dictionary.

        Returns:
            Dict: A dictionary containing bet details.
        """
        return {
            'type': self.bet_type,
            'amount': self.amount,
            'target_multiplier': self.target,
            "status": self.bet_status
        }

    @staticmethod
    def get_multiplier() -> float:
        """
        Generates a random multiplier based on predefined probabilities.

        Returns:
            float: The randomly chosen multiplier.
        """
        probabilities = {
            1.3: 19,
            1.5: 17,
            2.0: 15,
            2.5: 13,
            3.0: 12,
            3.5: 10,
            4.0: 8,
            5.0: 6,
            6.0: 4,
            7.0: 2,
            10.0: 1
        }

        # Create a weighted list of multipliers based on probabilities
        multipliers = [value for value, weight in probabilities.items() for _ in range(weight)]

        return random.choice(multipliers)

    def check_winning(self, chosen_multiplier: float) -> None:
        """
        Determines whether the user wins or loses based on the generated multiplier.

        Args:
            chosen_multiplier (float): The randomly generated multiplier.

        Updates:
            - Sets the bet status to WON or FAILED.
            - Resolves the bet outcome in the `BetsService` instance.
        """
        if self.target > chosen_multiplier:
            self.change_bet_status(self.BET_STATUS_FAILED)
            self.bet.change_bet_status(self.bet.BET_STATUS_FAILED)
            print(f'❌ You lost. The multiplier was {chosen_multiplier}.')
        else:
            self.change_bet_status(self.BET_STATUS_WON)
            self.bet.change_bet_status(self.bet.BET_STATUS_WON)
            print(f'🎉 You won! The multiplier was {chosen_multiplier}.')

        # Resolve the bet and apply profit/loss
        self.bet.resolve_bet(self.bet.bet_status)
