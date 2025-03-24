from .wallet import Wallet
from typing import Dict, List, Optional
import json
import os
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class BetType(Enum):
    BACCARAT = "BACCARAT"
    ROULETTE = "ROULETTE"
    LIMBO = "LIMBO"


class User:
    """
    A class representing a user with a unique Telegram ID and a wallet.

    Attributes:
        id (str): The user's Telegram ID.
        wallet (Wallet): The user's wallet.
        _bets (List[Dict]): A list of the user's bets.

    Methods:
        add_bet(bet_type, bet_data): Adds a bet to the user's bet history.
        to_dict(): Converts the user to a dictionary for storage or serialization.
        load_bets(): Returns the user's bets.
        __repr__(): Returns a string representation of the user.
    """

    def __init__(self, user_id: str, wallet: Wallet = None):
        """
        Initialize a user with a unique Telegram ID and a wallet.

        Args:
            user_id (str): The user's Telegram ID.
            wallet (Wallet): The user's wallet (optional, defaults to a new Wallet).
        """
        self.id = user_id
        self.wallet = wallet if wallet else Wallet()
        self._bets = []

    @property
    def balance(self) -> float:
        """
        Get the current balance from the wallet.

        Returns:
            float: The current balance of the user.
        """
        return self.wallet.balance

    def add_bet(self, bet_type: BetType, bet_data: Dict) -> None:
        """
        Add a bet to the user's bets list based on the bet type.

        Args:
            bet_type (BetType): The type of bet.
            bet_data (Dict): A dictionary containing the bet details.

        Raises:
            ValueError: If the bet type is invalid.
        """
        if bet_type == BetType.ROULETTE:
            bet_data.update({
                "number": bet_data.get("number", ""),
                "color": bet_data.get("color", "")
            })
        elif bet_type == BetType.BACCARAT:
            bet_data.update({
                'multiplier': bet_data.get('multiplier', "")
            })
        elif bet_type == BetType.LIMBO:
            bet_data.update({
                "target_multiplier": bet_data.get("target_multiplier", "")
            })
        else:
            raise ValueError(f"Invalid bet type: {bet_type}")

        self._bets.append(bet_data)

    def to_dict(self) -> Dict:
        """
        Convert the user to a dictionary for storage or serialization.

        Returns:
            Dict: A dictionary containing the user's ID, balance, and bets.
        """
        return {
            "telegram_id": self.id,  # user_id is stored as a string
            "balance": self.balance,
            "bets": self._bets
        }

    def load_bets(self) -> List[Dict]:
        """
        Get the user's bets.

        Returns:
            List[Dict]: A list of the user's bets.
        """
        return self._bets

    def __repr__(self) -> str:
        """
        Return a string representation of the user.

        Returns:
            str: A string displaying the user's ID and balance.
        """
        return f"User(id={self.id}, balance={self.balance})"


class UserManager:
    """
    A class for managing users and their data in a JSON database.

    Attributes:
        db_file (str): The path to the JSON file storing user data.
        users (Dict[str, User]): A dictionary mapping user IDs to User objects.

    Methods:
        load_users(): Load users from the JSON database file.
        save_users(): Save the current state of users to the JSON database file.
        get_user(user_id): Retrieve a user by their Telegram ID.
        create_user(user_id): Create a new user and add them to the database.
        update_user(user): Update a user's data in the database.
        delete_user(user_id): Delete a user from the database.
        add_bet_to_user(user_id, bet_type, bet_data): Add a bet to a user's bet history.
    """

    def __init__(self, db_file: str = "db.json"):
        """
        Initialize the UserManager with the path to the database file.

        Args:
            db_file (str): The path to the JSON file storing user data.
        """
        self.db_file = db_file
        if not os.path.exists(self.db_file):
            with open(self.db_file, "w", encoding="utf-8") as file:
                json.dump({}, file)  # Initialize with an empty dictionary
        self.users = self.load_users()

    def load_users(self) -> Dict[str, 'User']:
        """
        Load users from the JSON database file.

        Returns:
            Dict[str, User]: A dictionary mapping user IDs (as strings) to User objects.
        """
        try:
            with open(self.db_file, "r", encoding="utf-8") as file:
                users_data = json.load(file)
                if isinstance(users_data, list):  # Handle case where db.json is a list
                    users_data = {}  # Reset to an empty dictionary
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {self.db_file}: {e}")
            users_data = {}  # Handle case where db.json is empty or invalid
        except FileNotFoundError as e:
            logger.error(f"Database file not found: {self.db_file}: {e}")
            users_data = {}

        users = {}
        for user_id, user_data in users_data.items():
            user = User(user_id)
            user._bets = user_data.get("bets", [])

            # Validate balance before depositing
            balance = user_data.get("balance", 0.0)
            if balance > 0:  # Only deposit if balance is positive
                user.wallet.deposit(balance)

            users[user.id] = user

        return users

    def save_users(self) -> None:
        """
        Save the current state of users to the JSON database file.

        Returns:
            None
        """
        users_data = {user.id: user.to_dict() for user in self.users.values()}
        with open(self.db_file, "w", encoding="utf-8") as file:
            json.dump(users_data, file, indent=4)

    def get_user(self, user_id: str) -> Optional['User']:
        """
        Retrieve a user by their Telegram ID.

        Args:
            user_id (str): The Telegram ID of the user (as a string).

        Returns:
            Optional[User]: The User object if found, otherwise None.
        """
        return self.users.get(user_id)

    def create_user(self, user_id: str) -> 'User':
        """
        Create a new user and add them to the database.

        Args:
            user_id (str): The Telegram ID of the new user (as a string).

        Returns:
            User: The newly created User object.

        Raises:
            ValueError: If a user with the same ID already exists.
        """
        if user_id in self.users:
            raise ValueError(f"User with ID {user_id} already exists.")

        user = User(user_id)
        self.users[user_id] = user
        self.save_users()
        return user

    def update_user(self, user: 'User') -> None:
        """
        Update a user's data in the database.

        Args:
            user (User): The User object to update.

        Returns:
            None

        Raises:
            ValueError: If the user does not exist in the database.
        """
        if user.id not in self.users:
            raise ValueError(f"User with ID {user.id} does not exist.")

        self.users[user.id] = user
        self.save_users()

    def delete_user(self, user_id: str) -> None:
        """
        Delete a user from the database.

        Args:
            user_id (str): The Telegram ID of the user to delete (as a string).

        Returns:
            None

        Raises:
            ValueError: If the user does not exist in the database.
        """
        if user_id not in self.users:
            raise ValueError(f"User with ID {user_id} does not exist.")

        del self.users[user_id]
        self.save_users()

    def add_bet_to_user(self, user_id: str, bet_type: BetType, bet_data: Dict) -> None:
        """
        Add a bet to a user's bet history.

        Args:
            user_id (str): The Telegram ID of the user (as a string).
            bet_type (BetType): The type of bet.
            bet_data (Dict): A dictionary containing the bet details.

        Returns:
            None

        Raises:
            ValueError: If the user does not exist in the database.
        """
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} does not exist.")

        user.add_bet(bet_type, bet_data)
        self.save_users()
