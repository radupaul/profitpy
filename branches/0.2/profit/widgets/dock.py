#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDockWidget

class Dock(QDockWidget):
    def __init__(self, title, parent, child, area=Qt.LeftDockWidgetArea,
                 auto=True):
        QDockWidget.__init__(self, title, parent)
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.setFeatures(self.DockWidgetMovable | self.DockWidgetFloatable)
        if callable(child):
            child = child(self)
        self.setWidget(child)
        if auto:
            parent.addDockWidget(area, self)
