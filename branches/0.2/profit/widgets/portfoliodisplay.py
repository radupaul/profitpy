#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase <troy@gci.net>
# Distributed under the terms of the GNU General Public License v2

from itertools import ifilter

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QFrame, QIcon

from profit.lib import ValueTableItem
from profit.widgets.ui_portfoliodisplay import Ui_PortfolioDisplay


class PortfolioDisplay(QFrame, Ui_PortfolioDisplay):
    def __init__(self, session, parent=None):
        QFrame.__init__(self, parent)
        self.setupUi(self)
        self.portfolioItems = {}
        self.portfolioTable.verticalHeader().hide()
        self.replayRecent(session.messages)
        session.register(self.on_portfolioValue, 'UpdatePortfolio')

    def replayRecent(self, messages):
        isportmsg = lambda m:m.__class__.__name__ == 'UpdatePortfolio'
        symbols = (m.contract.m_symbol for t, m in messages if isportmsg(m))
        for symbol in symbols:
            def pred((time, message)):
                return isportmsg(message) and \
                       message.contract.m_symbol == symbol
            try:
                time, message = ifilter(pred, reversed(messages)).next()
            except (StopIteration, ):
                pass
            else:
                self.on_portfolioValue(message)

    def on_portfolioValue(self, message):
        sym = message.contract.m_symbol
        table = self.portfolioTable
        columnCount = table.columnCount()
        table.setUpdatesEnabled(False)

        try:
            items = self.portfolioItems[sym]
        except (KeyError, ):
            row = table.rowCount()
            table.insertRow(row)
            items = self.portfolioItems[sym] = \
                    [ValueTableItem() for i in range(columnCount)]
            items[0].setSymbol(sym)
            for item in items[1:]:
                item.setValueAlign()
            for col, item in enumerate(items):
                table.setItem(row, col, item)


        items[0].setText(sym)
        items[1].setValue(message.position)
        items[2].setValue(message.marketPrice)
        items[3].setValue(message.marketValue)
        items[4].setValue(message.averageCost)
        items[5].setValue(message.unrealizedPNL)
        items[6].setValue(message.realizedPNL)
        items[7].setText(message.accountName)

        for i in range(columnCount):
            table.resizeColumnToContents(i)
        table.setUpdatesEnabled(True)
