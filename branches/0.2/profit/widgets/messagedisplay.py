#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase <troy@gci.net>
# Distributed under the terms of the GNU General Public License v2

from functools import partial
from itertools import count
from time import ctime

from PyQt4.QtCore import Qt, QVariant, SIGNAL, pyqtSignature
from PyQt4.QtGui import QBrush, QColor, QColorDialog, QIcon, QFrame, QMenu
from PyQt4.QtGui import QPixmap

from ib.opt.message import registry

from profit.lib import ValueTableItem, disabledUpdates, nogc
from profit.widgets.ui_messagedisplay import Ui_MessageDisplay


def registry_type_names():
    return set([t.__name__ for t in registry.values()])


class MessageDisplay(QFrame, Ui_MessageDisplay):
    """ Table view of received messages.

    """
    pauseButtonIcons = {
        True:':/images/icons/player_play.png',
        False:':/images/icons/player_pause.png',
    }

    pauseButtonText = {
        True:'Resume',
        False:'Pause',
    }

    def __init__(self, session, parent=None):
        """ Constructor.

        @param session instance of Session
        @param parent ancestor of this widget
        """
        QFrame.__init__(self, parent)
        self.setupUi(self)
        self.messageTable.verticalHeader().hide()
        self.counter = count(1)
        self.paused = False
        self.setupColorButton()
        self.setupDisplayButton()

        self.setVisible(False)
        session.resendAll(self.reloadFast)
        self.updateRows()
        self.setVisible(True)

        session.registerAll(self.on_sessionMessage)

    def colorIcon(self, color, width=10, height=10):
        """ Creates an icon filled with color.

        @param color QColor instance
        @param width width of icon in pixels
        @param height of icon in pixels
        @return QIcon instance
        """
        pixmap = QPixmap(width, height)
        pixmap.fill(color)
        return QIcon(pixmap)

    def setupColorButton(self):
        """ Configures the color highlight button.

        @return None
        """
        self.colorPop = pop = QMenu(self.colorButton)
        self.colorButton.setMenu(pop)
        self.colorTypes = registry_type_names()
        self.colorActions = actions = \
            [pop.addAction(v) for v in sorted(self.colorTypes)]
        for action in actions:
            action.color = color = QColor(0,0,0)
            action.setIcon(self.colorIcon(color))
            target = nogc(partial(self.on_colorChange, action=action))
            self.connect(action, SIGNAL('triggered()'), target)
        self.brushMap = \
            dict([(str(a.text()), QBrush(a.color)) for a in actions])

    def setupDisplayButton(self):
        """ Configures the display types button.

        @return None
        """
        self.displayPop = pop = QMenu(self.displayButton)
        self.displayButton.setMenu(pop)
        self.displayActions = actions = []
        self.displayTypes = registry_type_names()
        allAction = pop.addAction('All')
        actions.append(allAction)
        pop.addSeparator()
        actions.extend([pop.addAction(v) for v in sorted(self.displayTypes)])
        for action in actions:
            action.setCheckable(True)
            target = nogc(partial(self.on_displayChange, action=action))
            self.connect(action, SIGNAL('triggered()'), target)
        allAction.setChecked(True)

    def on_colorChange(self, action):
        """ Signal handler for color change actions.

        @param QAction instance
        @return None
        """
        color = QColorDialog.getColor(action.color, self)
        if color.isValid():
            action.color = color
            action.setIcon(self.colorIcon(color))
            self.brushMap[str(action.text())] = QBrush(color)
        self.updateRows()

    def on_displayChange(self, action):
        """ Signal handler for display types actions.

        @param QAction instance
        @return None
        """
        index = self.displayActions.index(action)
        allAction = self.displayActions[0]
        allChecked = allAction.isChecked()
        actionChecked = action.isChecked()
        if allChecked and action is not allAction:
            allAction.setChecked(False)
            self.displayTypes = set()
            self.displayTypes.add(str(action.text()))
        elif allChecked and action is allAction:
            self.displayTypes = registry_type_names()
            for act in self.displayActions[1:]:
                act.setChecked(False)
        elif not allChecked and action is allAction:
            self.displayTypes = set()
        elif not allChecked and action is not allAction:
            text = str(action.text())
            if actionChecked:
                self.displayTypes.add(text)
            else:
                self.displayTypes.discard(text)
        self.updateRows()

    @pyqtSignature('bool')
    def on_pauseButton_clicked(self, checked=False):
        """ Signal handler for pause button.

        @param checked toggled state of button
        @return None
        """
        self.paused = checked
        self.pauseButton.setText(self.pauseButtonText[checked])
        self.pauseButton.setIcon(QIcon(self.pauseButtonIcons[checked]))
        if not checked:
            self.updateRows()

    def reloadFast(self, message):
        typename = message.__class__.__name__
        table = self.messageTable
        row = table.rowCount()
        table.insertRow(row)
        items = [ValueTableItem() for i in range(table.columnCount())]
        items[0].setText(str(self.counter.next()))
        items[1].setText(ctime())
        items[2].setText(typename)
        text = str.join(', ', ['%s=%s' % (k, v) for k, v in message.items()])
        items[3].setText(text)
        brushes = self.brushMap
        for col, item in enumerate(items):
            table.setItem(row, col, item)

    @disabledUpdates('messageTable')
    def on_sessionMessage(self, message):
        """ Signal handler for incoming messages.

        @param message message instance
        @return None
        """
        typename = message.__class__.__name__
        table = self.messageTable
        row = table.rowCount()
        table.insertRow(row)
        items = [ValueTableItem() for i in range(table.columnCount())]
        items[0].setText(str(self.counter.next()))
        items[1].setText(ctime())
        items[2].setText(typename)
        text = str.join(', ', ['%s=%s' % (k, v) for k, v in message.items()])
        items[3].setText(text)
        brushes = self.brushMap
        for col, item in enumerate(items):
            table.setItem(row, col, item)
            table.resizeColumnToContents(col)
            item.setForeground(brushes[typename])
        hidden = self.paused or (typename not in self.displayTypes)
        table.setRowHidden(row, hidden)
        table.scrollToItem(items[0])

    def updateRows(self):
        """ Changes row visibility and color based on instance settings.

        @return None
        """
        types = self.displayTypes
        table = self.messageTable
        brushes = self.brushMap
        for row, items in enumerate(table.iterrows()):
            typename = str(items[2].text())
            table.setRowHidden(row, typename not in types)
            brush = brushes[typename]
            for item in items:
                item.setForeground(brush)
