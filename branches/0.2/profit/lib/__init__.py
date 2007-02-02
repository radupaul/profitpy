#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

from PyQt4.QtCore import QPoint, QSettings, QSize, QVariant, SIGNAL, SLOT


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
