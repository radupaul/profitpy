#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

# todo:
#    search bar for tickers, orders, account, etc.
#    complete account dock widget
#    executions display
#    orders display
#    plots
#    add config dialog and session builder class setting
#    add "new empty row" function to localtable; cleanup table displays
#    add prompts to close/quit if connected
#    add position/value display to ticker table
#    add setting saves for message colors
#    message count high - use tree view in messages display

from functools import partial
from os import P_NOWAIT, getpgrp, killpg, popen, spawnvp
from signal import SIGQUIT
from sys import argv

from PyQt4.QtCore import Qt, pyqtSignature
from PyQt4.QtGui import QApplication, QFrame, QMainWindow
from PyQt4.QtGui import QFileDialog, QMessageBox, QProgressDialog

from profit.lib import Signals, Settings, nogc
from profit.session import Session
from profit.widgets import profit_rc
from profit.widgets.dock import Dock
from profit.widgets.output import OutputWidget
from profit.widgets.sessiontree import SessionTree
from profit.widgets.shell import PythonShell
from profit.widgets.ui_mainwindow import Ui_MainWindow


def svn_revision():
    return popen('svnversion|cut -f 2 -d :|cut -f 1 -d M').read().strip()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setupLeftDock()
        self.setupBottomDock()
        self.createSession()
        self.readSettings()
        if len(argv) > 1:
            self.on_actionOpenSession_triggered(filename=argv[1])


    def setupLeftDock(self):
        self.accountDock = Dock('Account', self, QFrame)
        self.sessionDock = Dock('Session', self, SessionTree)
        self.tabifyDockWidget(self.sessionDock, self.accountDock)

    def setupBottomDock(self):
        area = Qt.BottomDockWidgetArea
        self.stdoutDock = Dock('Output', self, OutputWidget, area)
        self.stderrDock = Dock('Error', self, OutputWidget, area)
        makeShell = partial(PythonShell,
                            stdout=self.stdoutDock.widget(),
                            stderr=self.stderrDock.widget())
        self.shellDock = Dock('Shell', self, makeShell, area)
        self.tabifyDockWidget(self.shellDock, self.stdoutDock)
        self.tabifyDockWidget(self.stdoutDock, self.stderrDock)

    def setWindowTitle(self, text):
        text = '%s 0.2 (alpha) (r %s)' % (text, svn_revision())
        QMainWindow.setWindowTitle(self, text)

    def createSession(self):
        ## lookup builder and pass instance here
        self.session = Session()
        self.emit(Signals.sessionCreated, self.session)

    @pyqtSignature('bool')
    def on_actionNewSession_triggered(self, checked=False):
        if len(argv) > 1:
            argv.remove(argv[1])
        pid = spawnvp(P_NOWAIT, argv[0], argv)

    @pyqtSignature('')
    def on_actionOpenSession_triggered(self, filename=None):
        if not filename:
            filename = QFileDialog.getOpenFileName(self)
        if filename:
            showmsg = self.statusBar().showMessage
            loadit = self.session.load(str(filename))
            try:
                count = loadit.next()
                last = count - 1
            except (StopIteration, ):
                showmsg('Warning session not loaded from "%s"' % filename)
            else:
                progress = QProgressDialog(
                    'Load Session Progress', 'Abort', 0, last, self
                )
                progress.setWindowModality(Qt.WindowModal)
                progress.setWindowTitle('Loading...')
                progress.show()
                msgid = -1
                for msgid in loadit:
                    QApplication.processEvents()
                    progress.setValue(msgid)
                    if progress.wasCanceled():
                        progress.close()
                        break
                if msgid == last:
                    msg = 'Loaded %s messages from file "%s"'
                    msg %= (count, filename)
                else:
                    msg = 'Load aborted; loaded %s messages of %s'
                    msg %= (msgid+1, count)
                showmsg(msg)


    @pyqtSignature('bool')
    def on_actionClearRecentMenu_triggered(self, checked=False):
        print '### clear recent menu', checked

    @pyqtSignature('')
    def on_actionSaveSession_triggered(self):
        if self.session.filename is None:
            self.actionSaveSessionAs.trigger()
        else:
            self.session.save()

    @pyqtSignature('')
    def on_actionSaveSessionAs_triggered(self):
        filename = QFileDialog.getSaveFileName(self)
        if filename:
            self.session.filename = str(filename)
            self.actionSaveSession.trigger()


    @pyqtSignature('')
    def on_actionCloseSession_triggered(self):
        if self.session.isModified:
            buttons = QMessageBox.Save|QMessageBox.Discard|QMessageBox.Cancel
            msg = QMessageBox.question(self, 'ProfitPy',
                                       'This session has been modified.\n'
                                       'Do you want to save your changes?',
                                       buttons,
                                       QMessageBox.Save)
            if msg == QMessageBox.Discard:
                self.close()
            elif msg == QMessageBox.Cancel:
                pass
            elif msg == QMessageBox.Save:
                self.actionSaveSession.trigger()
                ## this shouldn't work but it seems to... maybe should force
                ## a disconnect just to be sure?  might want to check for
                ## a connected session, too.
                self.actionCloseSession.trigger()
        else:
            self.close()

    @pyqtSignature('')
    def on_actionQuit_triggered(self):
        try:
            killpg(getpgrp(), SIGQUIT)
        except (AttributeError, ):
            self.close()

    def closeEvent(self, event):
        self.writeSettings()
        event.accept()

    def readSettings(self):
        settings = Settings()
        settings.beginGroup(settings.keys.main)
        size = settings.value(settings.keys.size,
                              settings.defaultSize).toSize()
        pos = settings.value(settings.keys.position,
                             settings.defaultPosition).toPoint()
        maxed = settings.value(settings.keys.maximized, False).toBool()
        settings.endGroup()
        self.resize(size)
        self.move(pos)
        if maxed:
            self.showMaximized()

    def writeSettings(self):
        settings = Settings()
        settings.beginGroup(settings.keys.main)
        settings.setValue(settings.keys.size, self.size())
        settings.setValue(settings.keys.position, self.pos())
        settings.setValue(settings.keys.maximized, self.isMaximized())
        settings.endGroup()
