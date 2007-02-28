#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

from PyQt4.QtGui import QIcon, QTreeWidgetItem, QWidget

from profit.lib import Signals
from profit.widgets.ui_sessiontree import Ui_SessionTree


class SessionTreeItem(QTreeWidgetItem):
    """ Shared implementation for SessionTree items

    """
    def __init__(self, parent, *strings):
        """ Constructor.

        @param parent tree widget or other tree item
        @param *strings strings for column(s) text
        """
        QTreeWidgetItem.__init__(self, parent, list(strings))

    def setIcon(self, column, icon):
        """ Overloaded to adjust item size when an icon is set

        @param column integer
        @param icon QIcon instance
        @return None
        """
        QTreeWidgetItem.setIcon(self, column, icon)
        sizehint = self.sizeHint(0)
        sizehint.setHeight(20)
        self.setSizeHint(0, sizehint)


class SessionTreeBasicItem(SessionTreeItem):
    """ Item type that maps SessionTree keys to icons.

    """
    iconNameMap = {
        'account':'identity',
        'connection':'server',
        'messages':'view_text',
        'orders':'klipper_dock',
        'portfolio':'bookcase',
        'strategy':'services',
        'tickers':'view_detailed',
    }

    def __init__(self, parent, *strings):
        """ Constructor.

        @param parent tree widget or other tree item
        @param *strings strings for column(s) text
        """
        SessionTreeItem.__init__(self, parent, *strings)
        try:
            name = self.iconNameMap[strings[0]]
            icon = QIcon(':images/icons/%s.png' % name)
        except (KeyError, IndexError, ):
            style = parent.style()
            icon = style.standardIcon(style.SP_DirIcon)
        self.setIcon(0, icon)



class SessionTreeTickerItem(SessionTreeItem):
    """ Item type that maps its first column text to a ticker icon.

    """
    def __init__(self, parent, *strings):
        """ Constructor.

        @param parent tree widget or other tree item
        @param *strings strings for column(s) text
        """
        SessionTreeItem.__init__(self, parent, *strings)
        try:
            icon = QIcon(':images/tickers/%s.png' % strings[0].lower())
            self.setIcon(0, icon)
        except (IndexError, ):
            pass


class SessionTree(QWidget, Ui_SessionTree):
    """ Tree view of a Session object.

    """
    def __init__(self, parent=None):
        """ Constructor.

        @param parent ancestor of this widget
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        window = self.window()
        tree = self.treeWidget
        connect = self.connect
        connect(window, Signals.sessionCreated, self.on_sessionCreated)
        connect(tree, Signals.itemDoubleClicked, self.on_itemDoubleClicked)
        connect(tree, Signals.itemDoubleClicked,
                window, Signals.itemDoubleClicked)

    def on_sessionCreated(self, session):
        """ signal handler called when new Session object is created

        @param session new Session instance
        @return None
        """
        self.session = session
        tree = self.treeWidget
        tree.clear()
        cls = SessionTreeBasicItem
        for key, values in session.items():
            item = cls(tree, key)
            for value in values:
                subcls = cls if key != 'tickers' else SessionTreeTickerItem
                subcls(item, value)

    def on_itemDoubleClicked(self, item, col):
        """ signal handler called when an item is double clicked

        @param item tree view item
        @param col column number clicked
        @return None
        """
