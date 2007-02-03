#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import QFrame, QIcon, QTableWidgetItem

from profit.lib import ValueTableItem
from profit.widgets.ui_accountdisplay import Ui_AccountDisplay


labels = [
    'Item',
    'Value',
    'Currency',
    'Account',
    'Color',
    ]


class AccountDisplay(QFrame, Ui_AccountDisplay):
    def __init__(self, session, parent=None):
        QFrame.__init__(self, parent)
        self.setupUi(self)
        self.accountItems = {}
        self.setupAccountTable()        
        session.register('AccountValue', self.on_accountValue)

    def setupAccountTable(self):
        table = self.accountTable()
        table.setColumnCount(len(labels))
        table.setHorizontalHeaderLabels(labels)
        table.setSelectionMode(table.SingleSelection)
        table.setSelectionBehavior(table.SelectItems)
        table.verticalHeader().hide()
        
    def on_accountValue(self, message):
        key, value, currency, accountName = \
             message.key, message.value, message.currency, message.accountName
        table = self.accountTable()
        columnCount = table.columnCount()
        table.setUpdatesEnabled(False)
        try:
            items = self.accountItems[key]
        except (KeyError, ):
            row = table.rowCount()
            table.insertRow(row)
            items = self.accountItems[key] = \
                    [AccountTableItem() for i in range(columnCount)]
            items[0].setText(key)
            for col, item in enumerate(items):
                table.setItem(row, col, item)
            table.sortItems(0)
        items[1].setValue(value)
        items[2].setText(currency)
        items[3].setText(accountName)
        for i in range(columnCount):
            table.resizeColumnToContents(i)
        table.setUpdatesEnabled(True)
        
    def accountTable(self):
        return self.accountValuesTable


class AccountTableItem(ValueTableItem):
    pass
