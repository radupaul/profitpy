#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

import sys

from cPickle import PicklingError, UnpicklingError, dump, load
from itertools import ifilter
from time import time

from PyQt4.QtCore import QObject, SIGNAL

from ib.ext.Contract import Contract
from ib.ext.ExecutionFilter import ExecutionFilter
from ib.ext.Order import Order
from ib.ext.TickType import TickType

from ib.opt import ibConnection
from ib.opt.message import registry

from profit.lib import Signals


class TickerCollection(QObject):
    def __init__(self, session):
        QObject.__init__(self)
        self.tickers = {}
        session.register(self.on_tickPriceSize, 'TickPrice')
        session.register(self.on_tickPriceSize, 'TickSize')

    def on_tickPriceSize(self, message):
        try:
            tickerdata = self.tickers[message.tickerId]
        except (KeyError, ):
            tickerdata = self.tickers[message.tickerId] = TickerData()
        try:
            value = message.price
        except (AttributeError, ):
            value = message.size
        try:
            seq = tickerdata.series[message.field]
        except (KeyError, ):
            seq = tickerdata.series[message.field] = []
        seq.append(value)


class TickerData(object):
    def __init__(self):
        self.series = {
            TickType.BID_SIZE:[],
            TickType.BID:[],
            TickType.ASK_SIZE:[],
            TickType.ASK:[],
            TickType.LAST_SIZE:[],
            TickType.LAST:[],
            }



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
        self.messages = []
        self.savepoint = 0 # len messages
        self.filename = None
        self.nextid = None
        self.tickerCollection = TickerCollection(self)

    def items(self):
        return [
            ('account', ()),
            ('connection', ()),
            ('executions', ()),
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
        return bool(self.connection and self.connection.isConnected())

    @property
    def isModified(self):
        return len(self.messages) != self.savepoint

    def register(self, obj, name, other=None):
        if other is None:
            self.connect(self, SIGNAL(name), obj)
        else:
            self.connect(self, SIGNAL(name), obj, other)

    def registerAll(self, obj, other=None):
        names = [typ.__name__ for typ in registry.values()]
        for name in names:
            if other is None:
                self.connect(self, SIGNAL(name), obj)
            else:
                self.connect(self, SIGNAL(name), obj, other)

    def registerMeta(self, instance):
        prefix = 'on_session_'
        names = [n for n in dir(instance) if n.startswith('on_session_')]
        for name in names:
            keys = name[len(prefix):].split('_')
            for key in keys:
                self.register(getattr(instance, name), key)

    def deregister(self, obj, name, other=None):
        if other is None:
            self.disconnect(self, SIGNAL(name), obj)
        else:
            self.disconnect(self, SIGNAL(name), obj, other)

    def deregisterAll(self, obj, other=None):
        names = [typ.__name__ for typ in registry.values()]
        for name in names:
            if other is None:
                self.disconnect(self, SIGNAL(name), obj)
            else:
                self.disconnect(self, SIGNAL(name), obj, other)

    def deregisterMeta(self, instance):
        raise NotImplementedError()

    def connectTWS(self, hostName, portNo, clientId, enableLogging=False):
        self.connection = con = ibConnection(hostName, portNo, clientId)
        con.enableLogging(enableLogging)
        con.connect()
        con.registerAll(self.receiveMessage)
        con.register(self.on_nextValidId, 'NextValidId')
        self.emit(Signals.connectedTWS)

    def on_nextValidId(self, message):
        self.nextid = int(message.orderId)

    def receiveMessage(self, message, timefunc=time):
        self.messages.append((timefunc(), message))
        self.emit(SIGNAL(message.__class__.__name__), message)

    def requestTickers(self):
        connection = self.connection
        for sym, tid in self.builder.tickers().items():
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

        contract = self.builder.contract('ASDF', secType='ASDF')
        connection.reqMktData(1, contract, '')
        return

    def testContract(self, symbol='AAPL'):
        orderid = self.nextid

        if orderid is None:
            return False

        contract = self.builder.contract(symbol)
        order = self.builder.order()
        order.m_action = 'SELL'
        order.m_orderType = 'MKT'
        order.m_totalQuantity = '300'
        order.m_lmtPrice = contract.m_auxPrice = 78.5
        order.m_openClose = 'O'
        self.connection.placeOrder(orderid, contract, order)
        self.nextid += 1
        return True

    def save(self):
        status = False
        try:
            handle = open(self.filename, 'wb')
        except (IOError, ):
            pass
        else:
            last = len(self.messages)
            messages = self.messages[0:last]
            try:
                dump(messages, handle, protocol=-1)
                self.savepoint = last
                status = True
            except (PicklingError, ):
                pass
            finally:
                handle.close()
        return status

    def load(self, filename):
        """ Restores session messages from file.

        This function first yields the total number of messages
        loaded, then yields the index of each message after it has
        pumped the message thru the receiveMessage function.  This
        oddness is used to support the QProgressDialog used in the
        main window during session loading.

        @param filename name of file from which to read messages.
        @return None
        """
        try:
            handle = open(filename, 'rb')
        except (IOError, ):
            pass
        else:
            try:
                messages = load(handle)
                yield len(messages)
                for index, (mtime, message) in enumerate(messages):
                    self.receiveMessage(message, lambda:mtime)
                    yield index
            except (UnpicklingError, ):
                pass
            finally:
                self.filename = filename
                self.savepoint = len(messages)
                handle.close()

