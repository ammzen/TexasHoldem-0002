#!/usr/bin/python
# -*- encoding: utf-8 -*-

from PokerUtils import *

class PokerAlgorithm:
    def __init__(self, mode, pokerState):
        self.ps = pokerState
        self.pu = PokerUtils()
        self.maxHands = 600
        self.SB = 20
        self.isBluffed = False
        self.DEBUG = False
        self.activeValue = {
            'all_in': 5,
            'raise': 3,
            'call': 1,
            'blind': 0,
            'check': -1,
            'fold': -2
            }
        self.entries = {
            'hold': self.holdRound,
            'flop': self.RRRound,
            'turn': self.RRRound,
            'river': self.RRRound
            }
        
    def __getHoldType(self, hold):
        hold = list(hold)
        if hold[0][1] < hold[1][1]:
            hold[0], hold[1] = hold[1], hold[0]
        _type = ''
        for card in hold:
            if card[1] >= 10:
                _type += ['T', 'J', 'Q', 'K', 'A'][card[1] - 10]
            else:
                _type += str(card[1])
        if hold[0][0] == hold[1][0]:
            _type += 's'
        return _type
    
    #hold: ((string<color>, int<point>), (string<color>, int<point>))
    def holdGroup(self, hold):
        types = [ # 0-6
            ['87', '53s', 'A9', 'Q9', '76', '42s', '32s', '96s','85s', 'J8',
             'J7s', '65', '54', '74s', 'K9', 'T8', '76', '65s', '54s', '86s'],
            ['66', 'J8s', '98s', 'T8s', '44', 'J9', '43s', '75s', 'T9', '33',
             '98', '64s', '22', 'K8s', 'K7s', 'K6s', 'K5s', 'K4s', 'K3s',
             'K2s', 'Q8s', '55', '87s', '97s'],
            ['77', 'Q9s', 'KJ', 'QJ', 'JTs', 'A7s', 'A6s', 'A5s', 'A4s',
             'A3s', 'A2s', 'J9s', 'T9s', 'K9s', 'KT', 'QT'],
            ['A8s', 'KQ', '88', 'QTs', 'A9s', 'AT', 'AJ', 'JTs'],
            ['99', 'QJs', 'KJs', 'KTs'],
            ['JJ', 'TT', 'AJs', 'ATs', 'AK', 'AQ', 'KQs'],
            ['AA', 'KK', 'QQ', 'AKs', 'AQs']
            ]
        holdType = self.__getHoldType(hold)
        for i, _type in enumerate(types):
            if holdType in _type:
                return i
        return -1

    # players: (pid, jetton, money, bet, <action>)
    def __call_bet(self, players):
        maxBet = 0
        beted = 0
        for player in players:
            if int(player[3]) > maxBet:
                maxBet = int(player[3])
            if player[0] == self.ps.getMyPID():
                beted = int(player[3])
        return maxBet - beted
        
    def __get_player_count(self, players):
        count = 0
        for player in players:
            if player[0] == self.ps.getMyPID():
                continue
            if player[4] != 'fold':
                count += 1
        return count

    # P: [1, 2, 3]
    def __random_req(self, P, bet):
        inq = random.choice(['fold'] * P[0] + ['call'] * P[1] +
                             ['raise ' + str(bet + 2 * P[2] * self.SB)] * P[2])
        return inq

    def __is_bluffable(self, players):
        onlines = self.ps.getOnlines()
        if len(players) <= 2 * len(onlines) / 3:
            return False
        blind = []
        for player in players:
            if player[4] == 'blind':
                blind.append(player[0])
            if player[4] in ['raise', 'all_in']:
                return False
        for pid in onlines:
            if pid in blind or pid not in [player[0] for player in players]:
                if self.ps.averageActive(pid) > 0.0:
                    return False
        return True

    def __is_money_enough(self):
        restHands = self.maxHands - self.ps.getHandCount()
        needed =  3 * self.SB * restHands / (2 * len(self.ps.getOnlines()))
        return self.ps.getMyMoneyAndJetton() - needed >= 2000
    
    # players: (pid, jetton, money, bet, <action>)
    def holdRound(self, players):
        group = self.holdGroup(self.ps.getHold())
        bet = self.__call_bet(players)
        pot = self.ps.getPot()
        onlines = self.ps.getOnlines()
        
        if len(onlines) == 1 or self.DEBUG:
            if group >= 2:
                return 'all_in'
            elif bet == 0:
                return 'check'
            else:
                return 'fold'
            
        if pot > 50 * self.SB and bet == 0:
            return 'check'
        
        if len(onlines) - len(players) <= 1 and self.__is_bluffable(players):
            if not self.isBluffed:
                self.isBluffed = True
                return 'raise ' + str(bet + self.SB)
        
        if self.ps.getMyMoneyAndJetton() < 25 * self.SB or \
           self.__is_money_enough():
            group -= 1

        if group >= 0 and group <= 4:
            if self.__is_bluffable(players) and not self.isBluffed:
                self.isBluffed = True
                return 'call' if pot > 20 * self.SB \
                       else 'raise ' + str(bet + 2 * self.SB)
            if bet < 2 * group * self.SB:
                return 'call'
            return 'check' if bet == 0 else 'fold'
    
        if group >= 5:
            if len(onlines) < 3:
                return 'call' if pot > 25 * self.SB \
                       else 'raise ' + str(bet + group * self.SB)
            elif bet > 50 * self.SB and len(onlines) >= 4:
                return 'fold'
            else:
                return 'call'

        if group >= 0 and bet <= 2 * self.SB:
            return 'call'

        if bet <= self.SB:
            return 'call'
        
        return 'check' if bet == 0 else 'fold'
    
    def RRRound(self, players):
        bet = self.__call_bet(players)
        onlines = self.ps.getOnlines()
        pot = self.ps.getPot()
        hold = self.ps.getHold()
        ftr = self.ps.getFTR()
        playerCount = self.__get_player_count(players)
        LR = self.pu.loseRate(hold, ftr)
        
        if len(onlines) == 1 or self.DEBUG:
            if LR < 25.0:
                return 'all_in'
            elif bet == 0:
                return 'check'
            else:
                return 'fold'

        if LR > 2.0 and (self.ps.getMyMoneyAndJetton() - bet < 50 * self.SB):
            return 'call' if LR < 20.0 else 'fold'
            
        if self.ps.getRound() == 'flop' and self.__is_bluffable(players):
            if not self.isBluffed:
                self.isBluffed = True
                return 'raise ' + str(bet + 10 * self.SB)
        
        if bet == 0:
            return 'check'

        RR, HS = self.pu.RR(hold, ftr, playerCount, bet, pot)
        #print('===========================')
        #print hold, ftr, playerCount, bet, pot
        #print RR, HS
        #print LR
        #print('===========================')
        if HS < 0.5 and (self.ps.getMyMoneyAndJetton() - bet < 6 * self.SB):
            return 'fold'
        
        if self.ps.getMyMoneyAndJetton() < 25 * self.SB or \
           self.__is_money_enough():
            RR -= 1.0
        elif len(onlines) <= 3:
            RR += 0.5
            
        if RR < 1.0:
            return 'fold'
        if RR < 1.5:
            if self.ps.getRound() == 'flop' and self.__is_bluffable(players):
                if not self.isBluffed:
                    self.isBluffed = True
                    return 'raise ' + str(bet + 10 * self.SB)
            return self.__random_req([7, 3, 0], bet)
        if RR < 2.0:
            return self.__random_req([0, 7, 3], bet)
        if RR < 4.0:
            return self.__random_req([0, 6, 4], bet)
        if RR >= 4.0:
            return self.__random_req([0, 1, 9], bet)


    def replyHandler(self, players):
        return self.entries[self.ps.getRound()](players)
