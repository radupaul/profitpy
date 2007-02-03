#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

import sys

from PyQt4.QtCore import SIGNAL
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
        return {'AAPL':100, 'EBAY':101, 'NVDA':102}

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
        self.receivers = []
        self['broker'] = None        
        self['account'] = builder.account()
        self['orders'] = builder.orders()
        self['strategy'] = builder.strategy()
        self['tickers'] = builder.tickers()

    def active(self):
        connection = self.connection()
        return connection and connection.active()

    def disconnect(self):
        connection = self.connection()
        if connection and connection.active():
            connection.disconnect()
        
    def connection(self):
        return self['broker']
    
    def register(self, key, call):
        self.receivers.append((key,call))
        connection = self.connection()
        if connection and connection.active():
            self.readerConnect(key, call)

            
    def connectTWS(self, hostName, portNo, clientId):
        self['broker'] = connection = tws_build_qt4(clientId)
        for key, call in self.receivers:
            self.readerConnect(key, call)
        connection.connect((hostName, portNo))
        return self
    
    def requestTickers(self):
        connection = self.connection()
        for sym, tid in self['tickers'].items():
            contract = self.builder.contract(sym)
            connection.reqMktData(tid, contract)
            connection.reqMktDepth(tid, contract)

    def requestAccount(self):
        connection = self.connection()
        connection.reqAccountUpdates()


    def readerConnect(self, key, call):
        reader = self.connection().reader
        reader.connect(reader, SIGNAL(key), call)
