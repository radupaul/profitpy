#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

import sys

from PyQt4.QtCore import QObject, SIGNAL

from ib.opt import ibConnection
from ib.opt.message import registry

from ib.ext.Contract import Contract
from ib.ext.ExecutionFilter import ExecutionFilter
from ib.ext.Order import Order

from profit.lib import Signals


class SessionBuilder(object):
    def account(self):
        return None

    def connection(self):
        return None

    def orders(self):
        return None

    def portfolio(self):
        return None

    def strategy(self):
        return None

    def tickers(self):
        return {'AAPL':100, 'EBAY':101, 'NVDA':102}

    def contract(self, symbol, secType='STK', exchange='SMART',
                 currency='USD'):
        contract = Contract()
        contract.m_symbol = symbol
        contract.m_secType = secType
        contract.m_exchange = exchange
        contract.m_currency = currency
        return contract

    def order(self):
        return Order()

    def messages(self):
        pass

    def build(self, session):
        names = ['account', 'connection', 'orders', 'portfolio', 'strategy', 'tickers', 'messages']
        for name in names:
            call = getattr(self, name)
            session[name] = call()


class Session(QObject):
    def __init__(self, data=None, builder=None):
        QObject.__init__(self)
        self.setObjectName('session')
        self.data = data if data else {}
        self.builder = builder if builder else SessionBuilder()
        self.builder.build(self)

    def __iter__(self):
        return iter(self.data)

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]

    def disconnectTWS(self):
        if self.isConnected:
            self.connection.disconnect()
            self.emit(Signals.disconnectedTWS)

    def get_isConnected(self):
        return self.connection and self.connection.isConnected()
    isConnected = property(get_isConnected)

    def get_connection(self):
        return self['connection']

    def set_connection(self, value):
        self['connection'] = value
    connection = property(get_connection, set_connection)

    #def deregister(self, call, key):
    #    self.disconnect(self, SIGNAL(key), call)

    #def deregisterAll(self, call):
    #    names = [typ.__name__ for typ in registry.values()]
    #    for name in names:
    #        self.disconnect(self, SIGNAL(name), call)

    def register(self, call, key):
        self.connect(self, SIGNAL(key), call)

    def registerAll(self, call):
        names = [typ.__name__ for typ in registry.values()]
        for name in names:
            self.connect(self, SIGNAL(name), call)

    def connectTWS(self, hostName, portNo, clientId):
        self.connection = con = ibConnection(hostName, portNo, clientId)
        #con.enableLogging()
        con.connect()
        con.registerAll(self.receiveMessage)
        self.emit(Signals.connectedTWS)

    def receiveMessage(self, message):
        self.emit(SIGNAL(message.__class__.__name__), message)

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
        #connection.reqExecutions(filt)
        connection.reqAllOpenOrders()
        connection.reqOpenOrders()

        #contract = self.builder.contract('ASDF', secType='ASDF')
        #connection.reqMktData(1, contract, '')

        contract = self.builder.contract('AAPL')
        order = self.builder.order()
        order.m_action = 'SELL'
        order.m_orderType = 'MKT'
        order.m_totalQuantity = '300'
        order.m_lmtPrice = contract.m_auxPrice = 78.5
        order.m_openClose = 'O'
        connection.placeOrder(23423, contract, order)
