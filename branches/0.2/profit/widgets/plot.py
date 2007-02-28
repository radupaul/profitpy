#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase <troy@gci.net>
# Distributed under the terms of the GNU General Public License v2

from PyQt4.QtGui import QFrame
from PyQt4.Qwt5 import QwtPlotCurve

from profit.widgets.ui_plot import Ui_Plot


class Plot(QFrame, Ui_Plot):
    """ Plot container.

    """
    def __init__(self, session, symbol, tickerId, parent=None, *indexes):
        """ Constructor.

        @param session instance of Session
        @param parent ancestor of this widget
        """
        QFrame.__init__(self, parent)
        self.setupUi(self)
        session.registerMeta(self)

        curve = QwtPlotCurve('Curve 1')
        y = session.tickerCollection.tickers[tickerId].series[1] # bid
        x = range(len(y))
        curve.setData(x, y)
        curve.attach(self.plotWidget)
        self.plotWidget.replot()

    def foo_on_session_UpdateAccountValue(self, message):
        """ Signal handler for account messages.

        @param message message instance
        @return None
        """
        key, value, currency, accountName = \
             message.key, message.value, message.currency, message.accountName
        table = self.accountValuesTable
        idx = (key, currency)
        try:
            items = self.accountItems[idx]
        except (KeyError, ):
            items = self.accountItems[idx] = table.newItemsRow()
            table.sortItems(0)
            table.resizeColumnToContents(0)
            table.resizeRowsToContents()
        items[0].setText(key)
        items[1].setValue(value)
        items[2].setText(currency)
        items[3].setText(accountName)
        for i in range(table.columnCount()):
            table.resizeColumnToContents(i)

