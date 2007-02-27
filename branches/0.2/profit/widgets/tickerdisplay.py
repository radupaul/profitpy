#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase <troy@gci.net>
# Distributed under the terms of the GNU General Public License v2

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QFrame, QIcon

from ib.ext.TickType import TickType

from profit.lib import ValueTableItem
from profit.widgets.ui_tickerdisplay import Ui_TickerDisplay


fieldColumns = {
    TickType.ASK_SIZE : 3,
    TickType.ASK : 4,
    TickType.BID_SIZE : 5,
    TickType.BID : 6,
    TickType.LAST_SIZE : 7,
    TickType.LAST : 8,
    }


from itertools import ifilter

class TickerDisplay(QFrame, Ui_TickerDisplay):
    def __init__(self, session, parent=None):
        QFrame.__init__(self, parent)
        self.setupUi(self)
        self.tickerItems = {}
        self.tickers = session.builder.tickers()
        self.tickerTable.verticalHeader().hide()
        self.lastTickerMessages(session.messages)
        session.register(self.on_tickerPriceSize, 'TickPrice')
        session.register(self.on_tickerPriceSize, 'TickSize')
        session.register(self.on_updatePortfolio, 'UpdatePortfolio')

    def lastTickerMessages(self, messages):
        for symbol, tickerId in self.tickers.items():
            for field in fieldColumns.keys():
                def pred((time, message)):
                    return message.__class__.__name__ in ('TickSize', 'TickPrice') and \
                           message.field == field and \
                           message.tickerId == tickerId
                try:
                    message = ifilter(pred, reversed(messages)).next()
                except (StopIteration, ):
                    pass
                else:
                    self.on_tickerPriceSize(message[1])

    def on_updatePortfolio(self, message):
        sym = message.contract.m_symbol
        try:
            tid = self.tickers[sym]
            items = self.tickerItems[tid]
        except (KeyError, ):
            pass
        else:
            items[1].setValue(message.position)
            items[2].setValue(message.marketValue)

    def on_tickerPriceSize(self, message):
        tid = message.tickerId
        table = self.tickerTable
        table.setUpdatesEnabled(False)

        try:
            value = message.price
        except (AttributeError, ):
            value = message.size

        try:
            items = self.tickerItems[tid]
        except (KeyError, ):
            sym = dict([(b, a) for a, b in self.tickers.items()])[tid]
            columnCount = table.columnCount()
            row = table.rowCount()
            table.insertRow(row)
            items = self.tickerItems[tid] = \
                    [ValueTableItem() for i in range(columnCount)]
            items[0].setSymbol(sym)
            for item in items[1:]:
                item.setValueAlign()
            for col, item in enumerate(items):
                table.setItem(row, col, item)
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

        table.setUpdatesEnabled(True)
