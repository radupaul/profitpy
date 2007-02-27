#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase <troy@gci.net>
# Distributed under the terms of the GNU General Public License v2

from functools import partial
from itertools import ifilter
from time import strftime, strptime

from PyQt4.QtCore import QEventLoop, QTimer, Qt
from PyQt4.QtGui import QApplication, QFrame, QIcon

from profit.lib import Signals, ValueTableItem, disabledUpdates, nameIn, nogc
from profit.widgets.ui_executionsdisplay import Ui_ExecutionsDisplay


def replayExecutions(messages, callback):
    ismsg = nameIn('ExecDetails')
    def pred((t, m)):
        return ismsg(m)
    flags = QEventLoop.AllEvents | QEventLoop.WaitForMoreEvents
    for time, message in ifilter(pred, messages):
        callback(message)
        QApplication.processEvents(flags)


class ExecutionsDisplay(QFrame, Ui_ExecutionsDisplay):
    dayFormatOut = '%a %d %b %Y'
    dayFormatIn = '%Y%m%d'

    def __init__(self, session, parent=None):
        QFrame.__init__(self, parent)
        self.setupUi(self)
        self.executionsItems = {}
        self.executionsTable.verticalHeader().hide()
        QTimer.singleShot(500,
                          nogc(partial(replayExecutions,
                                       messages=session.messages,
                                       callback=self.on_session_ExecDetails)))
        session.registerMeta(self)


    @disabledUpdates('executionsTable')
    def on_session_ExecDetails(self, message):
        table = self.executionsTable
        items = table.newItemsRow()

        contract = message.contract
        execution = message.execution
        mdate, mtime = execution.m_time.split()
        mdate = strftime(self.dayFormatOut, strptime(mdate, self.dayFormatIn))

        items[0].setValue(execution.m_side)
        items[1].setValue(execution.m_shares)
        items[1].setValueAlign()

        items[2].setSymbol(contract.m_symbol)
        items[3].setValue(execution.m_price)
        items[3].setValueAlign()

        items[4].setValue(contract.m_currency)
        items[5].setValue(execution.m_exchange)

        items[6].setText(mdate)
        items[6].setValueAlign()

        items[7].setValue(mtime)
        items[7].setValueAlign()

        items[8].setText(str(execution.m_permId))
        items[8].setValueAlign()
        items[9].setText(str(execution.m_orderId))
        items[9].setValueAlign()

        table = self.executionsTable
        #for col in range(table.columnCount()):
        #    table.resizeColumnToContents(col)
        table.resizeRowsToContents()
