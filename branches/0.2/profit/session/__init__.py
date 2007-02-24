#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

import sys

from PyQt4.QtCore import QObject, SIGNAL

from ib.ext.Contract import Contract
from ib.ext.ExecutionFilter import ExecutionFilter
from ib.ext.Order import Order
from ib.opt import ibConnection
from ib.opt.message import registry

from profit.lib import Signals


class SessionBuilder(object):
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


class Session(QObject):
    def __init__(self, data=None, builder=None):
        QObject.__init__(self)
        self.setObjectName('session')
        self.data = data if data else {}
        self.builder = builder if builder else SessionBuilder()
        self.connection = None

    def items(self):
        return [
            ('account', ()),
            ('connection', ()),
            ('messages', ()),
            ('orders', ()),
            ('portfolio', ()),
            ('strategy', ()),
            ('tickers', self.builder.tickers()),
            ]

    def disconnectTWS(self):
        if self.isConnected:
            self.connection.disconnect()
            self.emit(Signals.disconnectedTWS)

    @property
    def isConnected(self):
        return self.connection and self.connection.isConnected()

    def register(self, call, name):
        self.connect(self, SIGNAL(name), call)

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

    # not yet needed

    #def deregister(self, call, key):
    #    self.disconnect(self, SIGNAL(key), call)

    #def deregisterAll(self, call):
    #    names = [typ.__name__ for typ in registry.values()]
    #    for name in names:
    #        self.disconnect(self, SIGNAL(name), call)

