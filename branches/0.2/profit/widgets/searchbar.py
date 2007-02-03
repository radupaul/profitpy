#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase <troy@gci.net>
# Distributed under the terms of the GNU General Public License v2

from PyQt4.QtGui import QWidget
from profit.widgets.ui_searchbar import Ui_SearchBar

class SearchBar(QWidget, Ui_SearchBar):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
