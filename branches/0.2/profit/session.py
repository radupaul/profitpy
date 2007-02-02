#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

import sys

from ib.client import build_qt4 as tws_build_qt4
from ib.types import Contract


class SessionBuilder(object):
    def account(self):
        return None

    def orders(self):
        return None

    def strategy(self):
        return None

    def tickers(self):
        return {'AAPL':100, 'INTC':101, 'GOOG':102}

    def contract(self, symbol):
        return Contract(symbol=symbol,
                        secType='STK',
                        exchange='SMART',
                        currency='USD')


class Session(dict):
    def __init__(self, builder=None):
        if builder is None:
            builder = SessionBuilder()
        self.builder = builder
        self.listeners = []        
        self['connection'] = None        
        self['account'] = builder.account()
        self['orders'] = builder.orders()
        self['strategy'] = builder.strategy()
        self['tickers'] = builder.tickers()

    def active(self):
        connection = self.connection()
        return connection and connection.active()

    def connection(self):
        return self['connection']
    
    def register(self, listener):
        self.listeners.append(listener)
        connection = self.connection()
        if connection and connection.active():
            self.connectListener(connection, listener)
            
    def connectTWS(self, hostName, portNo, clientId):
        self['connection'] = connection = tws_build_qt4(clientId)
        for listener in self.listeners:
            self.connectListener(connection, listener)
        connection.connect((hostName, portNo))
        return self
    
    def requestTickers(self):
        connection = self.connection()
        for sym, tid in self['tickers'].items():
            contract = self.builder.contract(sym)
            connection.reqMktData(tid, contract)
            connection.reqMktDepth(tid, contract)

    @staticmethod
    def connectListener(connection, listener):
        for message in listener.readMessageTypes():
            connection.register(message, listener)
        for message in listener.writeMessageTypes():
            connection.register(message, listener, which=connection.WRITER)

