#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

from PyQt4.QtGui import QIcon, QTreeWidget, QTreeWidgetItem, QWidget

from profit.lib import Signals
from profit.widgets.ui_sessiontree import Ui_SessionTree




class SessionTreeItem(QTreeWidgetItem):
    def __init__(self, parent, *strings):
        QTreeWidgetItem.__init__(self, parent, list(strings))

    def setIcon(self, column, icon):
        QTreeWidgetItem.setIcon(self, column, icon)
        sizehint = self.sizeHint(0)
        sizehint.setHeight(20)
        self.setSizeHint(0, sizehint)


class SessionTreeBasicItem(SessionTreeItem):
    iconNameMap = {
        'account':'identity',
        'connection':'server',
        'messages':'view_text',
        'orders':'klipper_dock',
        'portfolio':'bookcase',
        'strategy':'services',
        'tickers':'view_detailed',
    }

    def __init__(self, parent, *strings):
        SessionTreeItem.__init__(self, parent, *strings)
        try:
            name = self.iconNameMap[strings[0]]
            self.setIcon(0, QIcon(':images/icons/%s.png' % name))
        except (KeyError, IndexError, ):
            pass


class SessionTreeTickerItem(SessionTreeItem):
    def __init__(self, parent, *strings):
        SessionTreeItem.__init__(self, parent, *strings)
        try:
            icon = QIcon(':images/tickers/%s.png' % strings[0].lower())
            self.setIcon(0, icon)
        except (IndexError, ):
            pass


class SessionTree(QWidget, Ui_SessionTree):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        window = self.window()
        tree = self.treeWidget
        connect = self.connect
        connect(window, Signals.sessionCreated, self.on_sessionCreated)
        connect(tree, Signals.itemDoubleClicked, self.on_itemDoubleClicked)
        connect(tree, Signals.itemDoubleClicked,
                window, Signals.sessionItemClicked)

    def on_sessionCreated(self, session):
        self.session = session
        tree = self.treeWidget
        tree.clear()
        cls = SessionTreeBasicItem
        for key, values in session.items():
            item = cls(tree, key)
            for value in values:
                subcls = cls if key != 'tickers' else SessionTreeTickerItem
                subcls(item, value)

    def on_itemDoubleClicked(self, item, col):
        #print >> sys.__stdout__, '###', item.text(0), col
        pass


