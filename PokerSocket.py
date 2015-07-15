#!/usr/bin/python
# -*- encoding: utf-8 -*-

import socket, sys, pprint, time
from PokerTools import *

class PokerSocket:
    # conn_args: ((string<ip>, int<port>), (string<ip>, int<port>), string<pid>)
    def __init__(self, conn_args, timeout = 5, sock = None):
        self.timeout = timeout
        self.pid = conn_args[2]
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(conn_args[1])
        while True:
            try:
                self.sock.connect(conn_args[0])
                break
            except:
                print('Connect timeout...')
                time.sleep(1)
        print('Connected')
            
    def start(self):
        self.sock.sendall('reg: %s %s need_notify \n' % (self.pid, 'ARE_YOU_OK'))
        ps = PokerState(self.pid)
        pm = PokerMessage(ps)
        tempData = ''
        while True:
            try:
                data = self.sock.recv(1024)
                if data:
                    reply = pm.msgHandler(tempData + data)
                    if reply == 'game-over':
                        self.sock.shutdown(socket.SHUT_RDWR)
                        self.sock.close()
                        break
                    elif reply == 'waiting':
                        tempData += data
                    elif reply:
                        #pprint.pprint(ps.state)
                        tempData = ''
                        self.sock.sendall(reply)
                    else:
                        tempData = ''
            
            except:
                print('Oops!')
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
                break
            

