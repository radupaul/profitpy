#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

import sys

from ib.client import build_qt4 as tws_build_qt4
from ib.types import Contract

class Session(dict):
    def __init__(self):
        self.listeners = []        
        self['account'] = self.buildAccount()
        self['connection'] = self.buildConnection()
        self['tickers'] = self.buildTickers()
        self['orders'] = self.buildOrders()
        self['strategy'] = self.buildStrategy()
        
    def register(self, listener):
        self.listeners.append(listener)
        connection = self['connection']
        if connection and connection.active():
            self.connectListener(connection, listener)
            
    def connectTWS(self, hostName, portNo, clientId):
        self['connection'] = connection = tws_build_qt4(clientId)
        for listener in self.listeners:
            self.connectListener(connection, listener)
        connection.connect((hostName, portNo))
        return self

    def active(self):
        return self['connection'] and self['connection'].active()
    
    def requestTickers(self):
        connection = self['connection']
        for sym, tid in self['tickers'].items():
            contract = Contract(symbol=sym, secType='STK', exchange='SMART',
                                currency='USD')
            connection.reqMktData(tid, contract)
            connection.reqMktDepth(tid, contract)

    def connectListener(self, connection, listener):
        for message in listener.readMessageTypes():
            connection.register(message, listener)
        for message in listener.writeMessageTypes():
            connection.register(message, listener, which=connection.WRITER)

    def buildAccount(self):
        return None

    def buildConnection(self):
        return None
    
    def buildTickers(self):
        return {'AAPL':100, 'INTC':101, 'GOOG':102}

    def buildOrders(self):
        return None

    def buildStrategy(self):
        return None
    
