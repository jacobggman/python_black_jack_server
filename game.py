from builtins import classmethod
from enum import Enum, auto
from pack import Pack, Card
import logging
from typing import List
from itertools import combinations

# hit, stand, double, split


class Error(Enum):
    UNKNOWN = auto()


class PlayerAction(Enum):
    STAND = auto()
    HIT = auto()
    DOUBLE = auto()
    SPLIT = auto()




class Player:
    money: int
    sit_index: int
    round_bet: int = -1
    cards: List[Card]

    def __int__(self):
        round_bet = -1
        self.cards = []

    def round_reset(self):
        self.round_bet = 0
        self.cards = []


class Table:
    def __init__(self, sits_num, pack, listener, notifier):
        self.sits = [] * sits_num
        self.sits_num = sits_num
        self.pack = pack
        self.cards = []
        self.listener = listener
        self.notifier = notifier

    def dealer_play(self):
        while self.get_sum_of_cards(self.cards) < 17:
            card = self.pack.get_card()
            self.cards.append(card)
            tell_dealer_up_card(card)

    def full_sits(self):
        return all([x is not None for x in self.sits])

    def play(self):

        # gets cards if don't have or shuffle when have less than 50 percent
        check_cards()

        # send the amount of sits
        tell_players_sits()

        awaiting_players = get_awating_players()

        # player take sit (if have any)
        # gets new players if have
        for player in awaiting_players:
            if self.full_sits():
                say_sits_full(player)
                break
            player.tell_numbers_of_sits()
            not_answer = True
            while not_answer:
                sit_index_ans = player.listen_sit()
                if sit_index_ans.is_error():
                    player_kick(player)
                    continue
                sit_index = sit_index_ans.value()
                bad_index = sit_index > -1 and sit_index > len(self.sits) and self.sits[sit_index] is None
                if bad_index:
                    player.tell_bad_index()

                not_answer = False
                self.sits[sit_index] = player
                player.sit_index = sit_index
                tell_players_new_player(player)

        self.get_bets()

        # get players one card
        give_players_card()

        # get card to itself
        card = self.pack.get_card()
        self.cards.append(card)
        tell_dealer_draw_card()

        # give card to players
        give_players_card()

        # get card to itself face down
        card = self.pack.get_card()
        self.cards.append(card)
        tell_dealer_up_card(card)

        # let players play
        for player in self.get_players():
            if self.check_finish_play(player.cards):
                continue

            not_answer = True
            while not_answer:
                answer = ask_player_action(player)
                if answer.is_error():
                    remove_player(player)
                    break

                not_answer = False
                if answer.value == PlayerAction.HIT:
                    card = self.pack.get_card()
                    give_player_card(player, card)
                    player_get_cards(player, card)
                elif answer.value == PlayerAction.STAND:
                    player_stand(player)
                # TODO: split and double
                else:
                    not_answer = True
                    wrong_play(player)

        dealer_show_card(self.cards[0])
        # check if pass 21

        # dealer play
        self.dealer_play()

        # get players there win or loses
        # check blackjack
        dealer_score = self.get_sum_of_cards(self.cards)
        dealer_black_jack = dealer_score == 21 and len(self.cards)
        self.dealer_black_jack()

        for player in self.get_players():
            player_score = self.get_sum_of_cards(player.cards)
            player_black_jack = player_score == 21 and len(player.cards)

            if player_black_jack and dealer_black_jack:
                player.money += player.round_bet
                player_push(player)
            elif player_black_jack and not dealer_black_jack:
                player.money += player.round_bet * 2.5
                self.player_black_jack(player)
            elif not player_black_jack and dealer_black_jack:
                self.player_lose(player)
            elif player_score > 21:
                self.player_lose(player)
            elif player_score == dealer_score:
                player.money += player.round_bet
                player_push(player)
            elif dealer_score > 21:
                player.money += player.round_bet * 2
                player_win(player)
            elif player_score < dealer_score:
                self.player_lose(player)
            elif player_score > dealer_score:
                player.money += player.round_bet * 2
                player_win(player)

        self.round_reset()


    def get_sum_of_card(self, card):
        value = card.value
        if value == 1:
            return [1, 11]
        elif value > 10:
            return [10]
        else:
            return [value]

    def get_sum_of_cards(self, cards, add=0):
        cards_sum = 0
        cards.sort(key=lambda card: card.value, reverse=True)

        last_index = -1
        num_of_cards = len(cards)
        for card_index in range(num_of_cards):
            value = cards[card_index].value
            if value == 1:
                last_index = card_index
                break
            elif value > 10:
                cards_sum += 10
            else:
                cards_sum += value

        biggest_sum = cards_sum
        if last_index != -1:
            numbers_of_aces = num_of_cards - last_index
            perm = set(combinations([1, 11] * numbers_of_aces, numbers_of_aces))

            temp_sum = cards_sum
            for x in perm:
                temp_sum += x

            if 21 > temp_sum > biggest_sum:
                biggest_sum = temp_sum
            elif biggest_sum > temp_sum and biggest_sum > 21:  # take the smaller
                biggest_sum = temp_sum

        return biggest_sum

    def check_finish_play(self, cards):
        sum_of_cards = self.get_sum_of_cards(cards[:])
        black_jack = len(cards) == 2 and sum_of_cards == 21
        return sum_of_cards > 21 or black_jack

    def get_bets(self):
        for player in self.get_players():
            while True:
                answer = player.get_bet()
                if answer.is_error():
                    self.sits[player.sit_index] = None
                    self.tell_player_kicked()
                    break
                bet = answer.value()
                if bet > player.money:
                    player.tell_bet_to_big()
                    continue
                player.money -= bet
                player.round_bet = bet

                self.tell_player_bet(player, bet)

    def get_players(self):
        for sit in self.sits:
            if sit is None:
                continue
            yield sit

    def round_reset(self):
        for player in self.get_players():
            player.round_reset()

        self.cards = []

    def give_player_card(self):
        for player in self.get_players():
            card = self.pack.get_card()
            player.cards = self.pack.get_card()
            tell_player_card(player, card)

