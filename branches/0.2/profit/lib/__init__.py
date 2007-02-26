#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

from PyQt4.QtCore import QPoint, QSettings, QSize, QVariant, Qt, SIGNAL, SLOT
from PyQt4.QtGui import QBrush, QColor, QIcon, QTableWidgetItem


class Signals:
    """ Contains SIGNAL attributes for easy and consistent reference.

    """
    lastWindowClosed = SIGNAL('lastWindowClosed()')
    sessionCreated = SIGNAL('sessionCreated(PyQt_PyObject)')
    itemDoubleClicked = SIGNAL('itemDoubleClicked(QTreeWidgetItem *,int)')
    connectedTWS = SIGNAL('connectedTWS')
    disconnectedTWS = SIGNAL('disconnectedTWS')
    clicked = SIGNAL('clicked()')
    currentChanged = SIGNAL('currentChanged(int)')


class Settings(QSettings):
    """ Convenient replacement for QSettings.

    """
    class keys:
        """ Attributes are setting keys.

        """
        main = 'MainWindow'
        session = 'Session'
        org = 'ProfitPy'
        app = 'ProfitDevice'
        size = 'Size'
        position = 'Position'
        maximized = 'Maximized'

    defaultSize = QSize(400, 400)
    defaultPosition = QPoint(200, 200)

    def __init__(self):
        """ Constructor.

        """
        QSettings.__init__(self, self.keys.org, self.keys.app)

    def setValue(self, key, value):
        """ Sets value of setting

        @param key setting key as string
        @param value anything supported by QVariant constructor
        @return None
        """
        QSettings.setValue(self, key, QVariant(value))

    def value(self, key, default):
        """ Returns value for key, or default if key doesn't exist.

        @param key setting key as string
        @param default value returned if key does not exist
        @return value of key or default
        """
        default = QVariant(default)
        return QSettings.value(self, key, default)


def importName(name):
    """ import and return a module by name in dotted form

    Copied from the Python lib docs.

    @param name module name as string
    @return module object
    """
    mod = __import__(name)
    for comp in name.split('.')[1:]:
        mod = getattr(mod, comp)
    return mod


def importItem(name):
    """ import an item from a module by dotted name

    @param name module and attribute string, i.e., foo.bar.baz
    @return value of name from module
    """
    names = name.split('.')
    modname, itemname = names[0:-1], names[-1]
    mod = importName(str.join('.', modname))
    return getattr(mod, itemname)


class ValueTableItem(QTableWidgetItem):
    """ Table item that changes colors based on value changes.

    """
    red = QBrush(QColor('red'))
    green = QBrush(QColor('green'))
    blue = QBrush(QColor('blue'))

    def __init__(self):
        """ Constructor.

        """
        QTableWidgetItem.__init__(self, self.UserType)
        self.setFlags(self.flags() & ~Qt.ItemIsEditable)
        self.value = None

    def setValue(self, value):
        """ Sets value of item and updates text color (if possible).

        @param string or number to set
        @return None
        """
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

    def setSymbol(self, symbol):
        """ Sets the text and icon for a symbol-based item.

        @param symbol ticker symbol as string
        @return None
        """
        icon = QIcon(':images/tickers/%s.png' % (symbol.lower(), ))
        self.setIcon(icon)
        self.setText(symbol)

    def setValueAlign(self, alignment=Qt.AlignRight|Qt.AlignVCenter):
        """ Sets the text alignment of this item.

        @param alignment Qt alignment flags
        @return None
        """
        self.setTextAlignment(alignment)

##
# Set for the nogc function/function decorator.
extra_references = set()


def nogc(obj):
    """ Prevents garbage collection. Usable as a decorator.

    @param obj any object
    @return obj
    """
    extra_references.add(obj)
    return obj


def disabledUpdates(name):
    """ Creates decorator to wrap table access with setUpdatesEnabled calls

    @param name name of table attribute
    @return decorator function
    """
    def disableDeco(meth):
        """ Wraps method with table update disable-enable calls.

        @param meth method to wrap
        @return replacement method
        """
        def method(self, *a, **b):
            table = getattr(self, name)
            table.setUpdatesEnabled(False)
            try:
                meth(self, *a, **b)
            finally:
                table.setUpdatesEnabled(True)
        return method
    return disableDeco
