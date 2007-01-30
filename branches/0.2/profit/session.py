#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

class Session(dict):
    def __init__(self):
        self['account'] = None
        self['connection'] = None
        self['tickers'] = ['AAPL', 'INTC', 'GOOG', ]
        self['orders'] = None
        self['strategy'] = None
        
