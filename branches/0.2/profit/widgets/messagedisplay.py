#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase <troy@gci.net>
# Distributed under the terms of the GNU General Public License v2

"""
todo:
    enable search filtering
    add pause/resume
"""
from itertools import count
from time import ctime

from PyQt4.QtCore import Qt, SIGNAL, pyqtSignature
from PyQt4.QtGui import QIcon, QFrame, QMenu

from ib.opt.message import registry

from profit.lib import ValueTableItem
from profit.widgets.ui_messagedisplay import Ui_MessageDisplay


def registry_type_names():
    return set([t.__name__ for t in registry.values()])

keeparound = set()

def nogc(f):
    keeparound.add(f)
    return f

class MessageDisplay(QFrame, Ui_MessageDisplay):
    def __init__(self, session, parent=None):
        QFrame.__init__(self, parent)
        self.setupUi(self)
        self.messageTable.verticalHeader().hide()
        self.counter = count(1)
        self.paused = False
        self.setupDisplayButton()
        session.registerAll(self.updateTable)

    @pyqtSignature('bool')
    def on_pauseButton_clicked(self, checked=False):
        self.paused = checked
        self.pauseButton.setText('Resume' if checked else 'Pause')
        iconname = 'play.png' if checked else 'pause.png'
        self.pauseButton.setIcon(QIcon(':/images/icons/player_'+iconname))
        if not self.paused:
            self.updateRowsFromDisplay()

    def setupDisplayButton(self):
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
            @nogc
            def target(action=action):
                self.displayActionTriggered(action)
            self.connect(action, SIGNAL('triggered()'), target)
        allAction.setChecked(True)

    def displayActionTriggered(self, action):
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
        self.updateRowsFromDisplay()

    def updateTable(self, message):
        typename = message.__class__.__name__
        table = self.messageTable
        row = table.rowCount()
        table.setUpdatesEnabled(False)
        table.insertRow(row)
        items = [ValueTableItem() for i in range(table.columnCount())]
        items[0].setText(str(self.counter.next()))
        items[1].setText(ctime())
        items[2].setText(typename)
        text = str.join(', ', ['%s=%s' % (k, v) for k, v in message.items()])
        items[3].setText(text)
        for col, item in enumerate(items):
            table.setItem(row, col, item)
            table.resizeColumnToContents(col)
        table.setRowHidden(row, (typename not in self.displayTypes) or self.paused)
        table.scrollToItem(items[0])
        table.setUpdatesEnabled(True)

    def updateRowsFromDisplay(self):
        types = self.displayTypes
        table = self.messageTable
        for row, items in enumerate(table.iterrows()):
            table.setRowHidden(row, str(items[2].text()) not in types)
