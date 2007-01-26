#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>
import os
import sys

from PyQt4.QtCore import Qt, pyqtSignature
from PyQt4.QtGui import QMainWindow, QFrame

from profit.dock import Dock
from profit.outputwidget import OutputWidget
from profit.sessiontree import SessionTree
from profit.shell import PythonShell
from profit.ui_mainwindow import Ui_MainWindow


__about__ = {
    'date':'$Date$',
    'revision':'$Rev$',
    'author':'$Author$',
    'url':'$URL$',
    'id':'$Id$',
    }


class MainWindow(QMainWindow, Ui_MainWindow):
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.accountDock = Dock('Account', self, QFrame)
        self.sessionDock = Dock('Session', self, SessionTree)
        self.tabifyDockWidget(self.sessionDock, self.accountDock)

        self.stdoutDock = Dock('Output', self, OutputWidget,
                               Qt.BottomDockWidgetArea)
        self.stderrDock = Dock('Error', self, OutputWidget,
                               Qt.BottomDockWidgetArea)
        def makeShell(parent):
            return PythonShell(parent,
                               stdout=self.stdoutDock.widget(),
                               stderr=self.stderrDock.widget())
        self.shellDock = Dock('Shell', self, makeShell,
                              Qt.BottomDockWidgetArea)
        self.tabifyDockWidget(self.shellDock, self.stdoutDock)        
        self.tabifyDockWidget(self.stdoutDock, self.stderrDock)

    @pyqtSignature('bool')
    def on_actionNewSession_triggered(self, checked=False):
        pid = os.spawnlp(os.P_NOWAIT, *sys.argv)
        if not pid:
            # handle error
            pass
        else:
            print 'spawned pid %s' % (pid, )
        

    @pyqtSignature('bool')
    def on_actionOpenSession_triggered(self, checked=False):
        print '### open session', checked

    @pyqtSignature('bool')
    def on_actionClearRecentMenu_triggered(self, checked=False):
        print '### clear recent menu', checked

    @pyqtSignature('bool')
    def on_actionSave_triggered(self, checked=False):
        print '### save session', checked

    @pyqtSignature('bool')
    def on_actionSaveSessionAs_triggered(self, checked=False):
        print '### save session as', checked

    @pyqtSignature('bool')    
    def on_actionCloseSession_triggered(self, checked=False):
        self.close()
