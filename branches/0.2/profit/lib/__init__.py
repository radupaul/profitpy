#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

from PyQt4.QtCore import QPoint, QSettings, QSize, QVariant, Qt, SIGNAL, SLOT
from PyQt4.QtGui import QBrush, QColor, QTableWidgetItem

class Signals:
    lastWindowClosed = SIGNAL('lastWindowClosed()')
    sessionCreated = SIGNAL('sessionCreated(PyQt_PyObject)')
    sessionItemClicked = itemDoubleClicked = SIGNAL('itemDoubleClicked(QTreeWidgetItem *,int)')


class SettingKeys:
    main = 'MainWindow'
    session = 'Session'    
    org = 'ProfitPy'
    app = 'ProfitDevice'
    size = 'size'
    pos = 'pos'
    maximized = 'maximized'


class Settings(QSettings):
    keys = SettingKeys()
    defSize = QSize(400, 400)
    defPos = QPoint(200, 200)
    
    def __init__(self):
        QSettings.__init__(self, self.keys.org, self.keys.app)

    def setValue(self, key, value):
        return QSettings.setValue(self, key, QVariant(value))

    def value(self, key, default):
        default = QVariant(default)
        return QSettings.value(self, key, default)


def importName(name):
    """ importName(name) -> import and return a module by name in dotted form

        Copied from the Python lib docs.
    """
    mod = __import__(name)
    for comp in name.split('.')[1:]:
        mod = getattr(mod, comp)
    return mod


def importItem(name):
    """ importItem(name) -> import an item from a module by dotted name

    """
    names = name.split('.')
    modname, itemname = names[0:-1], names[-1]
    mod = importName(str.join('.', modname))
    return getattr(mod, itemname)


class ValueTableItem(QTableWidgetItem):
    red = QBrush(QColor('red'))
    green = QBrush(QColor('green'))
    blue = QBrush(QColor('blue'))
    
    def __init__(self):
        QTableWidgetItem.__init__(self, self.UserType)
        self.setFlags(self.flags() & ~Qt.ItemIsEditable)        
        self.value = None

    def setValue(self, value):
        try:
            value = float(value)
        except (ValueError, ):
            self.setText(value)
            return
        current = self.value
        if current is None:
            self.value = value
            self.setText(str(value))
            return
        if value < current:
            self.setForeground(self.red)
        elif value > current:
            self.setForeground(self.green)                
        else:
            self.setForeground(self.blue)
        self.value = value
        self.setText(str(value))
    
