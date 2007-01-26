#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

from PyQt4.QtGui import QTreeWidget
from profit.ui_sessiontree import Ui_SessionTree

class SessionTree(QTreeWidget, Ui_SessionTree):
    def __init__(self, parent=None):
        QTreeWidget.__init__(self, parent)
        self.setupUi(self)
