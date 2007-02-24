#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem, QWidget

from profit.lib import Signals
from profit.widgets.ui_sessiontree import Ui_SessionTree


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
        for key, values in session.items():
            item = QTreeWidgetItem(tree, [key, ])
            for value in values:
                QTreeWidgetItem(item, [value, ])

    def on_itemDoubleClicked(self, item, col):
        #print >> sys.__stdout__, '###', item.text(0), col
        pass


