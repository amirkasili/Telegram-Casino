from Games.models.bets_polymorphism import BetsPolymorphism
from Accounts.models.user import User
from Accounts.models.bets_service import BetsService
from typing import Dict
import random

# Define card ranks and suits
suits = ['♥️', '♦️', '♣️', '♠️']
ranks = ['Two', 'Three', 'Four', 'Five', 'Six', 'Seven',
         'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Ace']
values = {'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5, 'Six': 6, 'Seven': 7, 'Eight': 8,
          'Nine': 9, 'Ten': 10, 'Jack': 0, 'Queen': 0, 'King': 0, 'Ace': 1}


class Card:
    """Represents a single card in the deck."""

    def __init__(self, suit, rank) -> None:
        self.suit = suit
        self.rank = rank
        self.value = values[rank]

    def __str__(self):
        return f"{self.rank} {self.suit}"


class Deck:
    """Represents a deck of shuffled Baccarat cards."""

    def __init__(self) -> None:
        self.deck = [Card(suit, rank) for suit in suits for rank in ranks]
        self.shuffle()

    def shuffle(self):
        """Shuffle the deck."""
        random.shuffle(self.deck)

    def deal(self):
        """Deal one card from the deck."""
        return self.deck.pop()


class Hand:
    """Represents a player's hand in Baccarat."""

    def __init__(self):
        self.cards = []
        self.value = 0

    def add_card(self, card: Card):
        """Add a card to the hand and update the value."""
        self.cards.append(card)
        self.value = sum(card.value for card in self.cards) % 10

    def __str__(self):
        return ', '.join(str(card) for card in self.cards)


class BaccaratBetService(BetsPolymorphism):
    """Handles Baccarat betting logic."""

    def __init__(self, amount: float, owner: User, bet_type: str = 'BACCARAT'):
        super().__init__(amount, bet_type, owner)
        self.multiplier = 2
        self.bet = BetsService(
            bet_type=self.bet_type,
            bet_amount=self.amount,
            bet_multiplier=self.multiplier,
            owner=self.owner
        )

    def to_dict(self) -> Dict:
        """Return bet details as a dictionary."""
        return {
            'type': self.bet_type,
            'amount': self.amount,
            'multiplier': self.multiplier,
            'status': self.bet_status
        }

    @staticmethod
    def creating_instances():
        """Create a shuffled deck and initial hands for player and banker."""
        deck = Deck()
        player_hand = Hand()
        banker_hand = Hand()

        # Deal two cards to each hand
        player_hand.add_card(deck.deal())
        banker_hand.add_card(deck.deal())
        player_hand.add_card(deck.deal())
        banker_hand.add_card(deck.deal())

        return deck, player_hand, banker_hand

    @staticmethod
    def get_multiplier(bet_type):
        """Generate a random multiplier for added excitement."""
        multipliers = {
            "player": random.uniform(1, 3),  # 1x to 3x
            "banker": random.uniform(1, 3),  # 1x to 3x
            "tie": random.uniform(1, 5)  # 1x to 5x
        }
        return round(multipliers[bet_type], 2)

    def check_winnings(self, betted_option):
        """Check the outcome of the bet and determine winnings."""
        text = "🎰 Baccarat Game Results 🎰\n\n"

        deck, player_hand, banker_hand = self.creating_instances()
        player_score = player_hand.value
        banker_score = banker_hand.value

        text += f"🃏 Player Hand:\n {player_hand} (Total: {player_score})\n"
        text += f"🏦 Banker Hand:\n {banker_hand} (Total: {banker_score})\n"

        # Natural win check
        if player_score in [8, 9] or banker_score in [8, 9]:
            text += "✨ Natural win! ✨\n"
        else:
            # Third card rule for Player
            player_third_card = None
            if player_score <= 5:
                player_third_card = deck.deal()
                player_hand.add_card(player_third_card)
                player_score = player_hand.value
                text += f"🎴 Player draws: {player_third_card} (New Total: {player_score})\n"

            # Third card rule for Banker
            banker_third_card = None
            if banker_score <= 2 or (player_third_card and banker_score <= 5):
                banker_third_card = deck.deal()
                banker_hand.add_card(banker_third_card)
                banker_score = banker_hand.value
                text += f"🎴 Banker draws: {banker_third_card} (New Total: {banker_score})\n"

        # Determine the winner
        if player_score > banker_score:
            winner = "player"
            base_payout = 2
        elif banker_score > player_score:
            winner = "banker"
            base_payout = 1.95
        else:
            winner = "tie"
            base_payout = 9

        text += f"\n🏆 The winner is: {winner.upper()}! 🏆\n"

        # Check if the player won the bet
        if betted_option == winner:
            multiplier = self.get_multiplier(betted_option)
            self.multiplier = base_payout * multiplier
            self.change_bet_status(self.BET_STATUS_WON)
            self.bet.change_bet_status(self.bet.BET_STATUS_WON)
            total_winnings = self.bet.calculate_profit()
            text += f"✅ You won the bet! Multiplier: {multiplier}x, Total Winnings: {total_winnings} coins! 💰\n"
        else:
            self.change_bet_status(self.BET_STATUS_FAILED)
            self.bet.change_bet_status(self.bet.BET_STATUS_FAILED)
            text += "❌ You lost the bet! Better luck next time!\n"
        self.bet.resolve_bet(self.bet.bet_status)
        return text
