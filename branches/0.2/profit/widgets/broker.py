#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

from os import getpid
from os.path import abspath, dirname, join
from subprocess import Popen, PIPE

from PyQt4.QtCore import pyqtSignature
from PyQt4.QtGui import QFrame, QMessageBox
from profit.widgets.ui_brokerwidget import Ui_BrokerWidget


host, port, client = 'localhost', '7496', str(getpid())


def commandStrings():
    keyCmd = join(dirname(abspath(__file__)), 'bin', 'login_helper')
    keyCmd += ' -v'
    brokerCmd = join(dirname(abspath(__file__)), 'bin', 'ib_tws')
    hasXterm = bool(Popen(['which', 'xterm'], stdout=PIPE).communicate()[0].strip())
    if hasXterm:
        commandFs = 'xterm -title %s -e %s'
        keyCmd = commandFs % ('helper', keyCmd, )
        brokerCmd = commandFs % ('ibtws', brokerCmd, )
    return keyCmd, brokerCmd


class BrokerWidget(QFrame, Ui_BrokerWidget):
    def __init__(self, session, parent=None):
        QFrame.__init__(self, parent)
        self.setupUi(self)
        self.session = session
        self.connection = None
        self.hostNameEdit.setText(host)
        self.portNumberEdit.setText(port)
        self.clientIdEdit.setText(client)
        keyHelperCommand, brokerCommand = commandStrings()        
        self.keyHelperCommandEdit.setText(keyHelperCommand)
        self.brokerCommandEdit.setText(brokerCommand)
        self.pids = {'broker':[], 'helper':[]}

    @pyqtSignature('')
    def on_connectButton_clicked(self):
        clientId = self.clientId()
        if clientId is None:
            return
        portNo = self.portNo()
        if portNo is None:
            return
        hostName = str(self.hostNameEdit.text())
        session = self.session
        try:
            self.connection = connection = \
                              session.connectTWS(hostName, portNo, clientId)
        except (Exception, ), exc:
            QMessageBox.critical(self, 'Connection Error', str(exc))
            return
        if connection.active():
            self.setEnabledButtons(False, True)
            try:
                connection.requestTickers()
            except (Exception, ), ex:
                print ex
                raise
        else:
            self.setEnabledButtons(True, False)            
            
            
    @pyqtSignature('')
    def on_disconnectButton_clicked(self):
        if self.connection and self.connection.active():
            self.connection.disconnect()
            self.setEnabledButtons(True, False)
            self.setNextClientId()

    def clientId(self):
        try:
            clientId = int(self.clientIdEdit.text())
        except (ValueError, ), exc:
            clientId = None
            QMessageBox.critical(self, 'Client Id Error', str(exc))
        return clientId

    def portNo(self):
        try:
            portNo = int(self.portNumberEdit.text())
        except (ValueError, ), exc:
            portNo = None
            QMessageBox.critical(self, 'Port Number Error', str(exc))
        return portNo
    
    def setEnabledButtons(self, connect, disconnect):
        self.connectButton.setEnabled(connect)
        self.disconnectButton.setEnabled(disconnect)
        self.clientIdEdit.setReadOnly(disconnect)
        self.portNumberEdit.setReadOnly(disconnect)
        self.hostNameEdit.setReadOnly(disconnect)
            

    def setNextClientId(self):
        try:
            value = int(self.clientIdEdit.text())
        except (ValueError, ):
            pass
        else:
            self.clientIdEdit.setText(str(value+1))
        

    @pyqtSignature('')
    def on_keyHelperCommandRunButton_clicked(self):
        args = str(self.keyHelperCommandEdit.text()).split()
        try:
            proc = Popen(args)
        except (OSError, ), exc:
            QMessageBox.critical(self, 'Key Helper Command Error', str(exc))
        else:
            pid = proc.pid
            self.pids['helper'].append(pid)
            
    
    @pyqtSignature('')
    def on_brokerCommandRunButton_clicked(self):
        args = str(self.brokerCommandEdit.text()).split()
        try:
            proc = Popen(args)
        except (OSError, ), exc:
            QMessageBox.critical(self, 'Broker Command Error', str(exc))
        else:
            pid = proc.pid
            self.pids['broker'].append(pid)

