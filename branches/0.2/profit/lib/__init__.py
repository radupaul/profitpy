#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>


from PyQt4.QtCore import SIGNAL, SLOT

class Signals:
    lastWindowClosed = SIGNAL('lastWindowClosed()')
    sessionCreated = SIGNAL('sessionCreated(PyQt_PyObject)')
    sessionItemClicked = itemDoubleClicked = SIGNAL('itemDoubleClicked(QTreeWidgetItem *,int)')


class Keys:
    main = 'MainWindow'
    org = 'ProfitPy'
    app = 'ProfitDevice'
    size = 'size'
    pos = 'pos'
    maximized = 'maximized'
    
