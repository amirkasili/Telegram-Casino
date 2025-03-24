from typing import Dict
from Accounts.models.user import User

class BetsPolymorphism:
    """
    Bets polymorphism class to use in other games classes.
    """
    BET_STATUS_WON = 'WON'
    BET_STATUS_FAILED = 'FAILED'  # Updated for consistency
    BET_STATUS_DRAW = 'DRAW'

    def __init__(self, amount: float, bet_type: str, owner : User):
        """
        Initializing the bet polymorphism class.
        :param amount: The bet amount.
        :param bet_type: The type of bet.
        """
        self.bet_status = None
        self.amount = amount
        self.owner = owner
        self.bet_type = bet_type

    def to_dict(self) -> Dict:
        """
        Convert the bet details to a dictionary.
        :return: A dictionary containing bet details.
        """
        return {
            "type": self.bet_type,
            "amount": self.amount,
            "status": self.bet_status
        }

    def change_bet_status(self, status: str) -> None:
        """
        Change the bet status if valid.
        :param status: The status to change.
        :return: None
        """
        if status not in [self.BET_STATUS_WON, self.BET_STATUS_FAILED, self.BET_STATUS_DRAW]:
            raise ValueError(f"Invalid bet status: {status}")
        self.bet_status = status
