#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

import sys
import time

from PyQt4.QtCore import QThread, SIGNAL
from PyQt4.QtCore import QObject, QTimer
from ib.opt import ibConnection

from ib.ext.Contract import Contract
from ib.ext.ExecutionFilter import ExecutionFilter


class SessionBuilder(object):
    def account(self):
        return None

    def orders(self):
        return None

    def strategy(self):
        return None

    def tickers(self):
        return {'AAPL':100, 'EBAY':101, 'NVDA':102}

    def contract(self, symbol):
        c = Contract()
        c.m_symbol = symbol
        c.m_secType = 'STK'
        c.m_exchange = 'SMART'
        c.m_currency = 'USD'
        return c


class SessionThread(object): # QThread
    def run(self):
        while True:
            time.sleep(1)


class Session(QObject):
    def __init__(self, builder=None):
        QObject.__init__(self)
        if builder is None:
            builder = SessionBuilder()
        self.builder = builder
        self.data = {}
        self['connection'] = None
        self['account'] = builder.account()
        self['orders'] = builder.orders()
        self['strategy'] = builder.strategy()
        self['tickers'] = builder.tickers()

    def __iter__(self):
        return self.data.iterkeys()

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]

    def get_connected(self):
        return self.connection and self.connection.isConnected()
    connected = property(get_connected)

    def disconnect(self):
        if self.connected:
            self.connection.disconnect()

    def get_connection(self):
        return self['connection']

    def set_connection(self, value):
        self['connection'] = value

    connection = property(get_connection, set_connection)

    def register(self, call, key):
        self.connect(self, SIGNAL(key), call)

    def connectTWS(self, hostName, portNo, clientId):
        self.connection = ibConnection(hostName, portNo, clientId)
        self.connection.connect()
        self.connection.registerAll(self.emitMessage)

    def emitMessage(self, msg):
        self.emit(SIGNAL(msg.__class__.__name__), msg)

    def requestTickers(self):
        connection = self.connection
        for sym, tid in self['tickers'].items():
            contract = self.builder.contract(sym)
            connection.reqMktData(tid, contract, '')
            connection.reqMktDepth(tid, contract, 1)

    def requestAccount(self):
        self.connection.reqAccountUpdates(True, "")

    def requestOrders(self):
        connection = self.connection
        filt = ExecutionFilter()
        connection.reqExecutions(filt)
        connection.reqAllOpenOrders()
        connection.reqOpenOrders()
