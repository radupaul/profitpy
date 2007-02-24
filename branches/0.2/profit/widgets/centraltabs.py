#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

from PyQt4.QtCore import Qt, pyqtSignature
from PyQt4.QtGui import QPushButton, QTabWidget, QWidget

from profit.lib import Signals
from profit.widgets.accountdisplay import AccountDisplay
from profit.widgets.connectiondisplay import ConnectionDisplay
from profit.widgets.messagedisplay import MessageDisplay
from profit.widgets.orderdisplay import OrderDisplay
from profit.widgets.portfoliodisplay import PortfolioDisplay
from profit.widgets.tickerdisplay import TickerDisplay


class CentralTabs(QTabWidget):
    def __init__(self, parent=None):
        QTabWidget.__init__(self, parent)
        self.connect(self.window(), Signals.sessionItemClicked,
                     self.on_sessionItemClicked)
        self.session = None
        self.closeTabButton = closeTabButton = QPushButton('Close Tab', self)
        self.closeTabButton.setFlat(True)

        self.setCornerWidget(closeTabButton, Qt.TopRightCorner)

        connect = self.connect
        connect(closeTabButton, Signals.clicked, self.on_closeTabButton_clicked)
        connect(self, Signals.currentChanged, self.on_currentChanged)
        connect(self.window(), Signals.sessionCreated, self.on_sessionCreated)

    def canClose(self, index):
        title = str(self.tabText(self.currentIndex()))
        if title in ('connection', ):
            if self.session and self.session.isConnected:
                return False
        return True

    def on_currentChanged(self, index):
        self.closeTabButton.setEnabled(self.canClose(index))

    def on_session_connectedTWS(self):
        self.on_currentChanged(self.currentIndex())

    def on_session_disconnectedTWS(self):
        self.closeTabButton.setEnabled(True)

    @pyqtSignature('')
    def on_closeTabButton_clicked(self):
        index = self.currentIndex()
        widget = self.widget(index)
        self.removeTab(index)
        widget.close()

    def on_sessionCreated(self, session):
        self.session = session
        connect = self.connect
        connect(session, Signals.connectedTWS, self.on_session_connectedTWS)
        connect(session, Signals.disconnectedTWS, self.on_session_disconnectedTWS)

    def on_sessionItemClicked(self, item, col):
        value = str(item.text(0))
        try:
            call = getattr(self, 'on_session%sClicked' % value.capitalize())
            call(item)
        except (AttributeError, TypeError, ):
            pass

    def on_sessionAccountClicked(self, item):
        idx = self.addTab(AccountDisplay(self.session, self), item.text(0))
        self.setCurrentIndex(idx)

    def on_sessionConnectionClicked(self, item):
        items = [(str(self.tabText(i)), i) for i in range(self.count())]
        items = dict(items)
        text = str(item.text(0))
        if text in items:
            idx = items[text]
        else:
            idx = self.addTab(ConnectionDisplay(self.session, self), text)
        self.setCurrentIndex(idx)

    def on_sessionOrdersClicked(self, item):
        idx = self.addTab(OrderDisplay(self.session, self), item.text(0))
        self.setCurrentIndex(idx)

    def on_sessionTickersClicked(self, item):
        idx = self.addTab(TickerDisplay(self.session, self), item.text(0))
        self.setCurrentIndex(idx)

    def on_sessionMessagesClicked(self, item):
        idx = self.addTab(MessageDisplay(self.session, self), item.text(0))
        self.setCurrentIndex(idx)

    def on_sessionPortfolioClicked(self, item):
        idx = self.addTab(PortfolioDisplay(self.session, self), item.text(0))
        self.setCurrentIndex(idx)
