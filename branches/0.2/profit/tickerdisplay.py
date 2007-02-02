#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

import sys
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QBrush, QColor, QFrame, QIcon, QTableWidgetItem

from ib.client import message
from ib.types import TickType
from profit.lib import Signals
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
        self.session = session
        session.register(self)
        self.setupTable()
        self.setupTickers()
        
    def setupTable(self):
        table = self.table()
        table.setSortingEnabled(False)        
        table.setColumnCount(len(labels))
        table.setHorizontalHeaderLabels(labels)
        table.setSelectionMode(table.SingleSelection)
        table.verticalHeader().hide()
            
    def readMessageTypes(self):
        return (message.TickPrice, message.TickSize, )

    def writeMessageTypes(self):
        return ()

    def setupTickers(self):
        self.rows = rows = {}
        table = self.table()
        tickers = self.session['tickers']
        columnCount = table.columnCount()
        for sym, tid in sorted(tickers.items()):
            row = table.rowCount()
            table.setRowCount(row+1)
            items = [TickerTableItem() for i in range(columnCount)]
            items[0].setSymbol(sym)
            for col, item in enumerate(items):
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, col, item)
            rows[tid] = items
        for i in range(len(labels)):
            table.resizeColumnToContents(i)

    def __call__(self, message):
        tid = message.tickerId
        try:
            items = self.rows[tid]
        except (KeyError, ):
            print >> sys.__stdout__, 'key error for %s' % (tid, )
        else:
            table = self.table()
            table.setUpdatesEnabled(False)
            index = labelTypes.get(message.field, None)
            if index is not None:
                items[index].setValue(message.value)
            table.setUpdatesEnabled(True)

    def table(self):
        return self.tickerTable


class TickerTableItem(QTableWidgetItem):
    red = QBrush(QColor('red'))
    green = QBrush(QColor('green'))
    blue = QBrush(QColor('blue'))
    
    def __init__(self):
        QTableWidgetItem.__init__(self, self.UserType)
        self.value = 0
        
    def setValue(self, value):
        current = self.value
        if value < current:
            self.setForeground(self.red)
        elif value > current:
            self.setForeground(self.green)                
        else:
            self.setForeground(self.blue)
        self.value = value
        self.setText(str(value))
    
    def setSymbol(self, value):
        icon = QIcon(':images/tickers/%s.png' % (value.lower(), ))
        if not icon.isNull():
            self.setIcon(icon)
        self.setText(value)
