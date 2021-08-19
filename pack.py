import logging
import random

NUM_OF_PACKS = 6


COLORS_CARDS = ['heart', 'diamonds', 'spades', 'clubs']


class Card:

    def __init__(self, value, color):
        self.value = value
        self.color = color

    AC = 11
    TWO = 2
    THREE = 2
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    PRINCES = 10
    QUEEN = 10
    KING = 10

    def convert(self):
        return [
            "AC",
            "02",
            "03",
            "04",
            "05",
            "06",
            "07",
            "08",
            "09",
            "10",
            "PR",
            "QE",
            "KI",
        ]


class Pack:
    def __init__(self):
        self.cards = Pack.get_random_cards()
        self.start_cards_num = len(self.cards)

    def get_card(self):
        if len(self.cards) == 0:
            logging.info("take new packs")
            self.cards = Pack.get_random_cards()

        return self.cards.pop(0)

    @staticmethod
    def get_pack():
        return range(1, 14)

    @staticmethod
    def get_random_cards():
        one_pack = [Card(value, color) for value in Pack.get_pack() for color in COLORS_CARDS]
        six_packs = one_pack * NUM_OF_PACKS
        random.shuffle(six_packs)
        return six_packs


