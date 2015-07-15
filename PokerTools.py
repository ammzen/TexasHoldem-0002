#!/usr/bin/python
# -*- encoding: utf-8 -*-

import StringIO, random, re
from PokerAlgorithm import PokerAlgorithm

class PokerState:
    ''' State example
    {
        'players': [
            {
                'pid': string<>,
                'jetton': int<>,
                'money': int<>,
                'active': int<>,
                'activeCount': int<>,
                'showdownCount': int<>,
                'winCount': int<>
            },
            ...
        ],
        'hold': [(string<color>, int<point>), ...],
        'ftr': [(string<color>, int<point>), ...],
        'button': string<>,
        'mypid': string<>,
        'blind': int<>,
        'pot': int<>,
        'round': string<seat/blind/hold/flop/turn/river/showdown>,
        'handCount': int<>,
        'onlines': int<>
    }
    '''
    def __init__(self, mypid):
        self.state = {
            'players': [],
            'hold': [],
            'ftr': [], # flop & turn & river
            'button': None,
            'mypid': mypid,
            'blind': None, # small blind
            'pot': None,
            'round': None,
            'handCount': 0,
            'onlines': 0
            }

    def cleanState(self):
        self.state['hold'] = []
        self.state['ftr'] = []
        self.state['button'] = None
        self.state['blind'] = None
        self.state['pot'] = None
        self.state['round'] = None
        
    def addCard(self, card_type, card):
        self.state[card_type].append(card)
        
    def get(self):
        return self.state
    
    def findPlayer(self, pid):
        for i, v in enumerate(self.state['players']):
            if v['pid'] == pid:
                return self.state['players'][i]
        return None
            
    # info: (pid, jetton, money)
    def addPlayer(self, info):
        if info[0] != self.state['mypid']:
            self.state['onlines'].append(info[0])
        player = self.findPlayer(info[0])
        if player is None:
            newPlayer = {
                'pid': info[0],
                'jetton': int(info[1]),
                'money': int(info[2]),
                'active': 0,
                'activeCount': 0,
                'showdownCount': 0,
                'winCount': 0
                }
            self.state['players'].append(newPlayer)
        else:
            self.setJettonMoney(info[0], int(info[1]), int(info[2]))

    def addActive(self, pid, value):
        player = self.findPlayer(pid)
        player['active'] += value
        player['activeCount'] += 1

    def averageActive(self, pid):
        if self.findPlayer(pid)['activeCount'] == 0:
            return 0.0
        return self.findPlayer(pid)['active'] * 1.0 / \
               self.findPlayer(pid)['activeCount']

    def addHandCount(self):
        self.state['handCount'] += 1
        
    def getHandCount(self):
        return self.state['handCount']
        
    def setButton(self, pid):
        self.state['button'] = pid
        
    def setBlind(self, blind):
        self.state['blind'] = blind

    def getBlind(self):
        return self.state['blind']
        
    def setMyPID(self, pid):
        self.state['mypid'] = pid

    def getMyPID(self):
        return self.state['mypid']
        
    def setPot(self, num):
        self.state['pot'] = num

    def getPot(self):
        return self.state['pot']
        
    def setRound(self, curRound):
        self.state['round'] = curRound

    def getRound(self):
        return self.state['round']

    def addShowdownCount(self, pid):
        player = self.findPlayer(pid)
        player['showdownCount'] += 1
        
    def getShowdownRate(self, pid):
        if self.getHandCount() == 0:
            return 0.0
        return self.findPlayer(pid)['showdownCount'] * 1.0 / self.getHandCount()

    def addWinCount(self, pid):
        player = self.findPlayer(pid)
        player['winCount'] += 1
        
    def getWinRate(self, pid):
        if self.getHandCount() == 0:
            return 0.0
        return self.findPlayer(pid)['winCount'] * 1.0 / self.getHandCount()
    
    def setJettonMoney(self, pid, jetton, money):
        player = self.findPlayer(pid)
        player['jetton'] = jetton
        player['money'] = money

    def getHold(self):
        return tuple(self.state['hold'])

    def getFTR(self):
        return tuple(self.state['ftr'])
    
    def getCards(self):
        return tuple(self.state['hold'] + self.state['ftr'])

    def getMoneyAndJetton(self, pid):
        player = self.findPlayer(pid)
        return player['jetton'] + player['money']

    def getMyMoneyAndJetton(self):
        return self.getMoneyAndJetton(self.state['mypid'])

    def getMyJetton(self):
        player = self.findPlayer(self.state['mypid'])
        return player['jetton']
    
    def cleanOnlines(self):
        self.state['onlines'] = []

    def getOnlines(self):
        return self.state['onlines']

    def getPlayers(self):
        players = []
        for player in self.state['players']:
            players.append(player['pid'])
        return players
    
class PokerMessage:
    def __init__(self, ps):
        self.ps = ps
        self.pa = PokerAlgorithm(0, ps)
        self.entries = {
            'seat/': self.__seat,
            'game-over': self.__game_over,
            'blind/': self.__blind,
            'hold/': self.__hold,
            'flop/': self.__flop,
            'turn/': self.__turn,
            'river/': self.__river,
            'showdown/': self.__showdown,
            'pot-win/': self.__pot_win,
            'inquire/': self.__inquire,
            'notify/': self.__notify
            }
        
    def __readline(self):
        return self.msg_buf.readline().strip()
    
    def __readlines(self):
        ret = []
        for line in self.msg_buf.readlines():
            ret.append(line.strip())
        return ret

    def isClosed(self, msg):
        closeList = ['/seat', '/blind', '/hold', '/flop',
                     '/turn', '/river', '/showdown',
                     '/pot-win', '/inquire', '/notify', 'game-over']
        return (msg.strip().split('\n')[-1].strip() in closeList)
        
    def __get_point(self, point):
        L = ['J', 'Q', 'K', 'A']
        if point in L:
            return 11 + L.index(point)
        else:
            return int(point)
        
    def __seat(self):
        '''
        seat/ eol
        button: pid jetton money eol
        small blind: pid jetton money eol
        (big blind: pid jetton money eol)0-1
        (pid jetton money eol)0-5
        /seat eol
        '''
        self.ps.cleanOnlines()
        player = self.__readline().split(': ')[1].split(' ')
        self.ps.addPlayer(player)
        self.ps.setButton(player[0])
        for _player in self.__readlines():
            if _player == '/seat':
                break
            if _player.find('blind') != -1:
                player = _player.split(':')[1].strip().split(' ')
                self.ps.addPlayer(player)
            else:
                player = _player.split(' ')
                self.ps.addPlayer(player)
        self.ps.cleanState()
        self.ps.setRound('seat')
        self.ps.addHandCount()
        
    def __game_over(self):
        '''
        game-over eol
        '''
        return 'game-over'
    
    def __blind(self):
        '''
        blind/ eol
        (pid: bet eol)1-2
        /blind eol
        '''
        blind = self.__readline().split(': ')
        self.ps.setBlind(int(blind[1]))
        self.ps.setRound('blind')
            
    def __hold(self):
        '''
        hold/ eol
        color point eol
        color point eol
        /hold eol
        '''
        for _card in self.__readlines():
            if _card == '/hold':
                break
            card = _card.split(' ')
            self.ps.addCard('hold', (card[0], self.__get_point(card[1])))
        self.ps.setRound('hold')
        self.pa.isBluffed = False
        
    def __flop(self):
        '''
        flop/ eol
        color point eol
        color point eol
        color point eol
        /flop eol
        '''
        for _card in self.__readlines():
            if _card == '/flop':
                break
            card = _card.split(' ')
            self.ps.addCard('ftr', (card[0], self.__get_point(card[1])))
        self.ps.setRound('flop')
        self.pa.isBluffed = False
        
    def __turn(self):
        '''
        turn/ eol
        color point eol
        /turn eol
        '''
        card = self.__readline().split(' ')
        self.ps.addCard('ftr', (card[0], self.__get_point(card[1])))
        self.ps.setRound('turn')
        
    def __river(self):
        '''
        river/ eol
        color point eol
        /river eol
        '''
        card = self.__readline().split(' ')
        self.ps.addCard('ftr', (card[0], self.__get_point(card[1])))
        self.ps.setRound('river')
        
    def __showdown(self):
        '''
        showdown/ eol
        common/ eol
        (color point eol)5
        /common eol
        (rank: pid color point color point nut_hand eol)2-8
        /showdown eol
        '''
        isRank = False
        for _rank in self.__readlines():
            if _rank == 'common/':
                continue
            if _rank == '/common':
                isRank = True
                continue
            if _rank == '/showdown':
                break
            if isRank:
                rank = _rank.split(': ')[1].split(' ')
                # TODO: Get more infomation.
                self.ps.addShowdownCount(rank[0])
            else:
                # Not needed now.
                common = _rank.split(' ')
        self.ps.setRound('showdown')
                
    def __pot_win(self):
        '''
        pot-win/ eol
        (pid: num eol)0-8
        /pot-win eol
        '''
        for _win in self.__readlines():
            if _win == '/pot-win':
                break
            pid, num = _win.split(':')
            self.ps.addWinCount(pid)
            
    def __inquire(self):
        '''
        inquire/ eol
        (pid jetton money bet blind | check | call | raise | all_in | fold eol)1-8
        total pot: num eol
        /inquire eol
        '''
        players = []
        for _inquire in self.__readlines():
            if _inquire == '/inquire':
                break
            if _inquire.find('total pot') == -1:
                inquire = _inquire.split(' ')
                players.append(inquire)
                if inquire[4] != 'blind':
                    self.ps.addActive(inquire[0], self.pa.activeValue[inquire[4]])
                self.ps.setJettonMoney(inquire[0], int(inquire[1]), int(inquire[2]))
            else:
                self.ps.setPot(int(_inquire.split(': ')[1]))
        reply = self.pa.replyHandler(tuple(players)) + ' \n'
        return reply
    
    def __notify(self):
        '''
        notify/ eol
        (pid jetton money bet blind | check | call | raise | all_in | fold eol)1-8
        total pot: num eol
        /notify eol
        '''
        for _notify in self.__readlines():
            if _notify == '/notify':
                break
            if _notify.find('total pot') == -1:
                notify = _notify.split(' ')
                self.ps.addActive(notify[0], self.pa.activeValue[notify[4]])
                self.ps.setJettonMoney(notify[0],
                                       int(notify[1]), int(notify[2]))
            else:
                self.ps.setPot(int(_notify.split(': ')[1]))
                
    def msgHandler(self, msg):
        if not self.isClosed(msg):
            return 'waiting'
        patt = r'((?P<TypeTag>[^/]+)/[\s\S]+?/(?P=TypeTag)|game-over)'
        results = re.findall(patt, msg)
        for result in results:
            self.msg_buf = StringIO.StringIO(result[0])
            msg_type = self.__readline()
            reply = self.entries[msg_type]()
            if reply:
                return reply
            
