#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase <troy@gci.net>
# Distributed under the terms of the GNU General Public License v2

from itertools import ifilter

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QFrame, QIcon

from ib.ext.TickType import TickType

from profit.lib import ValueTableItem, disabledUpdates, nameIn
from profit.widgets.portfoliodisplay import replayPortfolio
from profit.widgets.ui_tickerdisplay import Ui_TickerDisplay


fieldColumns = {
    TickType.ASK_SIZE : 3,
    TickType.ASK : 4,
    TickType.BID_SIZE : 5,
    TickType.BID : 6,
    TickType.LAST_SIZE : 7,
    TickType.LAST : 8,
    }


def replayTick(messages, tickers, callback):
    ismsg = nameIn('TickSize', 'TickPrice')
    for symbol, tickerId in tickers.items():
        for field in fieldColumns.keys():
            def pred((t, m)):
                return ismsg(m) and m.field==field and m.tickerId==tickerId
            for time, message in ifilter(pred, reversed(messages)):
                callback(message)
                break


class TickerDisplay(QFrame, Ui_TickerDisplay):
    def __init__(self, session, parent=None):
        QFrame.__init__(self, parent)
        self.setupUi(self)
        self.tickerItems = {}
        self.tickers = tickers = session.builder.tickers()
        self.tickerTable.verticalHeader().hide()
        replayTick(session.messages, tickers,
                   self.on_session_TickPrice_TickSize)
        replayPortfolio(session.messages, self.on_session_UpdatePortfolio)
        session.registerMeta(self)

    @disabledUpdates('tickerTable')
    def on_session_UpdatePortfolio(self, message):
        sym = message.contract.m_symbol
        try:
            tid = self.tickers[sym]
            items = self.tickerItems[tid]
        except (KeyError, ):
            pass
        else:
            items[1].setValue(message.position)
            items[2].setValue(message.marketValue)

    @disabledUpdates('tickerTable')
    def on_session_TickPrice_TickSize(self, message):
        tid = message.tickerId
        table = self.tickerTable
        try:
            value = message.price
        except (AttributeError, ):
            value = message.size
        try:
            items = self.tickerItems[tid]
        except (KeyError, ):
            items = self.tickerItems[tid] = table.newItemsRow()
            sym = dict([(b, a) for a, b in self.tickers.items()])[tid]
            items[0].setSymbol(sym)
            for item in items[1:]:
                item.setValueAlign()
            table.sortItems(0)
            table.resizeColumnToContents(0)
            table.resizeRowsToContents()
        try:
            index = fieldColumns[message.field]
        except (KeyError, ):
            pass
        else:
            items[index].setValue(value)
            table.resizeColumnToContents(index)
