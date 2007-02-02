#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

from os import getpid

from PyQt4.QtCore import pyqtSignature
from PyQt4.QtGui import QFrame, QMessageBox
from profit.widgets.ui_connectionsettings import Ui_ConnectionSettings

host, port, client = 'localhost', '7496', str(getpid())


class ConnectionSettings(QFrame, Ui_ConnectionSettings):
    def __init__(self, session, parent=None):
        QFrame.__init__(self, parent)
        self.setupUi(self)
        self.session = session
        self.connection = None
        self.hostNameEdit.setText(host)
        self.portNumberEdit.setText(port)
        self.clientIdEdit.setText(client)

    @pyqtSignature('')
    def on_connectButton_clicked(self):
        clientId = self.clientId()
        if clientId is None:
            return
        portNo = self.portNo()
        if portNo is None:
            return
        hostName = str(self.hostNameEdit.text())
        try:
            self.connection = connection = self.session.connectTWS(hostName, portNo, clientId)
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
        
