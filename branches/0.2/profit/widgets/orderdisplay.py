#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase <troy@gci.net>
# Distributed under the terms of the GNU General Public License v2

from PyQt4.QtGui import QFrame

from profit.lib import ValueTableItem
from profit.widgets.ui_orderdisplay import Ui_OrderDisplay


class OrderDisplay(QFrame, Ui_OrderDisplay):
    def __init__(self, session, parent=None):
        QFrame.__init__(self, parent)
        self.setupUi(self)
        self.orderItems = {}
        self.orderTable.verticalHeader().hide()
        session.register(self.on_openOrder, 'OpenOrder')
        session.register(self.on_orderStatus, 'OrderStatus')
        session.register(self.on_contractDetails, 'ContractDetails')
        session.register(self.on_execution, 'Execution')

    def on_openOrder(self, message):
        print '#### open order message', message
        return
        key, value, currency, accountName = \
             message.key, message.value, message.currency, message.accountName
        table = self.accountValuesTable
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


    def on_orderStatus(self, message):
        print '### order status message', message
        class __message:
            __slots__ = ('orderId', 'message', 'filled', 'remaining',
                     'permId', 'parentId', 'lastFillPrice',
                     'avgFillPrice', 'clientId')

    def on_contractDetails(self, message):
        print '#### contract details', message
        class detail:
            __slots__ = ('details', )

    def on_execution(self, message):
        print '#### execution', message
        class __message:
            __slots__ = ('orderId', 'contract', 'details', )


class OrderTableItem(ValueTableItem):
    pass
