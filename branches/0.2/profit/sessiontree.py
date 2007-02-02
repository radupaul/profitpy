#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

import sys
from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem, QWidget

from profit.lib import Signals
from profit.ui_sessiontree import Ui_SessionTree


class SessionTree(QWidget, Ui_SessionTree):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        window = self.window()
        tree = self.tree()
        self.connect(window, Signals.sessionCreated,
                     self.on_sessionCreated)
        self.connect(tree, Signals.itemDoubleClicked,
                     self.on_itemDoubleClicked)
        self.connect(tree, Signals.itemDoubleClicked, window,
                     Signals.sessionItemClicked)
        
    def on_sessionCreated(self, session):
        self.session = session
        widget = self.tree()
        widget.clear()
        for key in sorted(session):
            item = QTreeWidgetItem(widget)
            item.setText(0, key)
            value = session[key]
            if value:
                for v in value:
                    i = QTreeWidgetItem(item)
                    i.setText(0, v)
                    
    def on_itemDoubleClicked(self, item, col):
        pass
        #print >> sys.__stdout__, '###', item.text(0), col

    def tree(self):
        return self.treeWidget
