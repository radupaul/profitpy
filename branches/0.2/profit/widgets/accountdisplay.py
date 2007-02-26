#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase <troy@gci.net>
# Distributed under the terms of the GNU General Public License v2

from PyQt4.QtGui import QFrame

from profit.lib import ValueTableItem, disabledUpdates
from profit.widgets.ui_accountdisplay import Ui_AccountDisplay


class AccountDisplay(QFrame, Ui_AccountDisplay):
    """ Table view of an account.

    """
    def __init__(self, session, parent=None):
        """ Constructor.

        @param session instance of Session
        @param parent ancestor of this widget
        """
        QFrame.__init__(self, parent)
        self.setupUi(self)
        self.accountItems = {}
        self.accountValuesTable.verticalHeader().hide()
        session.register(self.on_accountValue, 'UpdateAccountValue')

    @disabledUpdates('accountValuesTable')
    def on_accountValue(self, message):
        """ Signal handler for account messages.

        @param message message instance
        @return None
        """
        key, value, currency, accountName = \
             message.key, message.value, message.currency, message.accountName
        table = self.accountValuesTable
        columnCount = table.columnCount()
        try:
            items = self.accountItems[key]
        except (KeyError, ):
            row = table.rowCount()
            table.insertRow(row)
            items = self.accountItems[key] = \
                    [ValueTableItem() for i in range(columnCount)]
            items[0].setText(key)
            for col, item in enumerate(items):
                table.setItem(row, col, item)
            table.sortItems(0)
        items[1].setValue(value)
        items[2].setText(currency)
        items[3].setText(accountName)
        for i in range(columnCount):
            table.resizeColumnToContents(i)


