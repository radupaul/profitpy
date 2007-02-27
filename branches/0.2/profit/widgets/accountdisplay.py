#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase <troy@gci.net>
# Distributed under the terms of the GNU General Public License v2

from itertools import ifilter

from PyQt4.QtGui import QFrame

from profit.lib import ValueTableItem, disabledUpdates, nameIn
from profit.widgets.ui_accountdisplay import Ui_AccountDisplay


def replayAccount(messages, callback):
    ismsg = nameIn('UpdateAccountValue')
    keys = (m.key for t, m in messages if ismsg(m))
    for key in set(keys):
        def pred((t, m)):
            return ismsg(m) and m.key==key
        for time, message in ifilter(pred, reversed(messages)):
            callback(message)
            break


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
        replayAccount(session.messages, self.on_session_UpdateAccountValue)
        session.registerMeta(self)

    @disabledUpdates('accountValuesTable')
    def on_session_UpdateAccountValue(self, message):
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


