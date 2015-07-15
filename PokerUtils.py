#!/usr/bin/python
# -*- encoding: utf-8 -*-

import itertools, operator, random
from deuces import Card, Evaluator

class PokerUtils:
    def __init__(self):
        self.emulateCount = 1000
        self.maxRank = 7462
        self.evaluator = Evaluator()
        self.color = {
            'SPADES': 0,
            'HEARTS': 1,
            'CLUBS': 2,
            'DIAMONDS': 3
            }
        self.rColor = ['♠', '♥', '♣', '♦']
        self.eColor = ['s', 'h', 'c', 'd']
        self.rPoint = ['2', '3', '4', '5', '6', '7',
                       '8', '9', 'T', 'J', 'Q', 'K', 'A']
        self.ePoint = self.rPoint
        self.type = {
            'HIGH_CARD': 0,
            'ONE_PAIR': 1,
            'TWO_PAIR': 2,
            'THREE_OF_A_KIND': 3,
            'STRAIGHT': 4,
            'FLUSH': 5,
            'FULL_HOUSE': 6,
            'FOUR_OF_A_KIND': 7,
            'STRAIGHT_FLUSH': 8
            }
        self.entries = {
            'HIGH_CARD': self.__is_high_card,
            'ONE_PAIR': self.__is_one_pair,
            'TWO_PAIR': self.__is_two_pair,
            'THREE_OF_A_KIND': self.__is_three_of_a_kind,
            'STRAIGHT': self.__is_straight,
            'FLUSH': self.__is_flush,
            'FULL_HOUSE': self.__is_full_house,
            'FOUR_OF_A_KIND': self.__is_four_of_a_kind,
            'STRAIGHT_FLUSH': self.__is_straight_flush
            }
    
    # cards: [(int<color>, int<point>), ...]
    # point is reverse-sorted
    def __diff_cards(self, cards):
        _cardsPoint = []
        for card in cards:
            if card[1] not in _cardsPoint:
                _cardsPoint.append(card[1])
        return len(_cardsPoint)
    
    def __is_high_card(self, cards):
        return self.__diff_cards(cards) == 5 and \
               not self.__is_flush(cards) and \
               not self.__is_straight(cards)
    
    def __is_one_pair(self, cards):
        return self.__diff_cards(cards) == 4
    
    def __is_two_pair(self, cards):
        return self.__diff_cards(cards) == 3 and \
               (cards[2][1] != cards[0][1] and cards[2][1] != cards[4][1])
    
    def __is_three_of_a_kind(self, cards):
        return self.__diff_cards(cards) == 3 and \
               (cards[0][1] == cards[1][1] == cards[2][1] or
                cards[1][1] == cards[2][1] == cards[3][1] or
                cards[2][1] == cards[3][1] == cards[4][1])
    
    def __is_straight(self, cards):
        return self.__diff_cards(cards) == 5 and \
           (cards[4][1] == 12 or cards[0][1] - cards[4][1] == 4)
    
    def __is_flush(self, cards):
        return cards[0][0] == cards[1][0] == \
           cards[2][0] == cards[3][0] == cards[4][0]
    
    def __is_full_house(self, cards):
        return self.__diff_cards(cards) == 2 and \
               cards[0][1] == cards[1][1] and cards[3][1] == cards[4][1]
    
    def __is_four_of_a_kind(self, cards):
        return self.__diff_cards(cards) == 2 and \
               (cards[0][1] != cards[1][1] or cards[3][1] != cards[4][1])
    
    def __is_straight_flush(self, cards):
        return self.__is_straight(cards) and self.__is_flush(cards)
    
    def sortedGroupList(self, cards):
        cards = [(card / 13, card % 13) for card in cards]
        return sorted(cards, key = lambda card: card[1], reverse = True)
    
    def getColorOf(self, card):
        return card / 13
    
    def getPointOf(self, card):
        return card % 13

    def cardsBeautify(self, cards):
        return ' '.join([self.rColor[card[0]] + self.rPoint[card[1]] \
                         for card in cards])
    
    def toOrigin(self, cards):
        cards = [self.color[card[0]] * 13 + card[1] - 2 for card in cards]
        return cards
    
    def modifyCardsOrder(self, cards, cardsType):
        if cardsType in ['STRAIGHT_FLUSH', 'FLUSH', 'STRAIGHT', 'HIGH_CARD']:
            return cards
        if cardsType == 'FOUR_OF_A_KIND':
            if cards[0][1] != cards[1][1]:
                cards = cards[1:] + cards[:1]
        elif cardsType == 'FULL_HOUSE':
            if cards[1][1] != cards[2][1]:
                cards = cards[2:] + cards[:2]
        elif cardsType == 'THREE_OF_A_KIND':
            if cards[1][1] != cards[2][1]:
                cards = cards[2:] + cards[:2]
            elif cards[0][1] != cards[1][1] and cards[3][1] != cards[4][1]:
                cards = cards[1:4] + cards[0:1] + cards[4:5]
        elif cardsType == 'TWO_PAIR':
            if cards[0][1] != cards[1][1]:
                cards = cards[1:] + cards[:1]
            elif cards[0][1] == cards[1][1] and cards[3][1] == cards[4][1]:
                cards = cards[0:2] + cards[3:5] + cards[2:3]
        elif cardsType == 'ONE_PAIR':
            if cards[3][1] == cards[4][1]:
                cards = cards[3:] + cards[:3]
            elif cards[2][1] == cards[3][1]:
                cards = cards[2:4] + cards[0:2] + cards[4:5]
            elif cards[1][1] == cards[2][1]:
                cards = cards[1:3] + cards[0:1] + cards[3:5]
        return cards
    
    # cards: (int<>, int<>, ...)
    def cardsType(self, cards):
        cards = self.sortedGroupList(cards)
        # 12 3 2 1 0 ---> 3 2 1 0 12
        if cards[0][1] == 12 and cards[1][1] == 3 and \
           cards[2][1] == 2 and cards[3][1] == 12 and cards[4][1] == 3:
            cards = a[1:] + a[:1]
        for key in self.type:
            if self.entries[key](cards):
                cards = self.modifyCardsOrder(cards, key)
                rank = self.type[key] * 13 ** 5
                for idx, card in enumerate(cards):
                    rank += card[1] * 13 ** (4 - idx)
                return rank, key, self.cardsBeautify(cards)

    # The small the better
    # cards: (int<card>, ...)
    def cardsRank(self, cards):
        evaCards = []
        for card in cards:
            evaCards.append(Card.new(self.ePoint[self.getPointOf(card)] + \
                                     self.eColor[self.getColorOf(card)]))
        rank = self.evaluator.evaluate(evaCards)
        return rank
    
    def restCards(self, usedCards):
        mask = [1] * 52
        for card in usedCards:
            mask[card] = 0
        return list(itertools.compress(range(52), mask))
    
    def randomChoose(self, restCards, num):
        return random.sample(set(restCards), num)
        
    def C(self, n, k):
        return  reduce(operator.mul, range(n - k + 1, n + 1)) / \
               reduce(operator.mul, range(1, k +1))
    
    # hold/ftr: ((string<color>, int<point>), ...)
    # point: 2-14   
    def loseRate(self, hold, ftr):
        hold = self.toOrigin(hold)
        ftr = self.toOrigin(ftr)
        cards = hold + ftr
        myRank = self.cardsRank(tuple(cards))
        total = self.C(52 - len(cards), 2)
        count = 0
        restCards = self.restCards(cards)
        for _hold in itertools.combinations(restCards, 2):
            for _cards in itertools.combinations(ftr + list(_hold), 5):
                _rank = self.cardsRank(tuple(_cards))
                if _rank < myRank:
                    count += 1
                    break
                
        return count * 100.0 / total

    # ftr/cards: (int<card>, ...)
    # Return: 1 if win, else 0
    def emulate(self, myRank, ftr, cards, playerCount):
        ftr = list(ftr)
        cards = list(cards)
        ftr += self.randomChoose(self.restCards(cards), 5 - len(ftr))
        players = [[]] * playerCount
        usedCards = []
        minRank = self.maxRank
        for idx in range(playerCount):
            players[idx] = self.randomChoose(self.restCards(cards + ftr + usedCards), 2)
            rank = self.cardsRank(tuple(ftr + players[idx]))
            if rank < minRank:
                minRank = rank
            usedCards += players[idx]
        if myRank < minRank:
            return 1
        else:
            return 0
        
    # Hand Strength
    # hold/ftr: ((string<color>, int<point>), ...)
    def HS(self, hold, ftr, playerCount):
        hold = self.toOrigin(hold)
        ftr = self.toOrigin(ftr)
        cards = hold + ftr
        myRank = self.cardsRank(tuple(cards))
        winCount = 0
        for idx in range(self.emulateCount):
            winCount += self.emulate(myRank, tuple(ftr), tuple(cards), playerCount)
        return winCount * 1.000 / self.emulateCount

    # Rate of Return
    def RR(self, hold, ftr, playerCount, bet, pot):
        if bet == 0:
            return 2.0
        HS = self.HS(hold, ftr, playerCount)
        return HS * (bet + pot) / bet, HS
        
if __name__ == '__main__':
    pu = PokerUtils()
    print(pu.loseRate((('DIAMONDS', 12), ('HEARTS', 10)), (('CLUBS', 5), ('DIAMONDS', 9), ('SPADES', 3))))
    print(pu.HS((('DIAMONDS', 12), ('HEARTS', 10)), (('CLUBS', 5), ('DIAMONDS', 9), ('SPADES', 3)), 1))
