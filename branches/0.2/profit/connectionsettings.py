#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

from PyQt4.QtGui import QFrame
from profit.ui_connectionsettings import Ui_ConnectionSettings



class ConnectionSettings(QFrame, Ui_ConnectionSettings):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.setupUi(self)

        
    def on_connectButton_toggled(self, checked):
        print '### connect', checked
        
        
