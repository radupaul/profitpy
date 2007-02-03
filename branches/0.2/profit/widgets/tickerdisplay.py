#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

import sys
#from PyQt4.QtCore import Qt
from PyQt4.QtGui import QFrame, QIcon, QTableWidgetItem

from ib.client import message
from ib.types import TickType

from profit.lib import Signals, ValueTableItem
from profit.widgets.ui_tickerdisplay import Ui_TickerDisplay


labels = [
    'Symbol',
    'Position',
    'Value',
    'Ask Size',
    'Ask Price',
    'Bid Size',
    'Bid Price',
    'Last Size',
    'Last Price',
    ]


labelTypes = {
    TickType.ASK_SIZE : labels.index('Ask Size'),
    TickType.ASK : labels.index('Ask Price'),
    TickType.BID_SIZE : labels.index('Bid Size'),
    TickType.BID : labels.index('Bid Price'),
    TickType.LAST_SIZE : labels.index('Last Size'),
    TickType.LAST : labels.index('Last Price'),
    }


class TickerDisplay(QFrame, Ui_TickerDisplay):
    def __init__(self, session, parent=None):
        QFrame.__init__(self, parent)
        self.setupUi(self)
        self.tickerItems = {}
        self.tickers = session['tickers']        
        self.setupTable()
        session.register('TickPrice', self.on_tickerPriceSize)
        session.register('TickSize', self.on_tickerPriceSize)
        
    def setupTable(self):
        table = self.table()
        table.setSortingEnabled(False)        
        table.setColumnCount(len(labels))
        table.setHorizontalHeaderLabels(labels)
        table.setSelectionMode(table.SingleSelection)
        table.verticalHeader().hide()
        for i in range(len(labels)):
            table.resizeColumnToContents(i)

    def on_tickerPriceSize(self, message):
        tid = message.tickerId
        table = self.table()        
        table.setUpdatesEnabled(False)
        
        try:
            items = self.tickerItems[tid]
        except (KeyError, ):
            sym = dict([(b,a) for a, b in self.tickers.items()])[tid]
            columnCount = table.columnCount()
            row = table.rowCount()
            table.insertRow(row)
            items = self.tickerItems[tid] = \
                    [TickerTableItem() for i in range(columnCount)]
            items[0].setSymbol(sym)
            for col, item in enumerate(items):
                table.setItem(row, col, item)
            table.sortItems(0)
            table.resizeColumnToContents(0)

        index = labelTypes.get(message.field, None)
        if index is not None:
            items[index].setValue(message.value)
            table.resizeColumnToContents(index)
        table.setUpdatesEnabled(True)

    def table(self):
        return self.tickerTable


class TickerTableItem(ValueTableItem):
    def setSymbol(self, value):
        icon = QIcon(':images/tickers/%s.png' % (value.lower(), ))
        if not icon.isNull():
            self.setIcon(icon)
        self.setText(value)
