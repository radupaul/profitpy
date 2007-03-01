#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase <troy@gci.net>
# Distributed under the terms of the GNU General Public License v2

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QColor, QColorDialog, QFrame, QPen, QTreeWidgetItem
from PyQt4.Qwt5 import QwtPlotCurve

from ib.ext.TickType import TickType

from profit.lib import colorIcon
from profit.widgets.ui_plot import Ui_Plot


class ControlTreeItem(QTreeWidgetItem):
    """ Control tree widget item.

    """
    def __init__(self, parent, text, icon, color):
        """ Constructor.

        @param parent tree widget or tree widget item
        @param text string for first column
        @param icon QIcon instance for first column
        @param color QColor instance
        """
        QTreeWidgetItem.__init__(self, parent)
        self.setCheckState(0, Qt.Unchecked)
        self.setText(0, text)
        self.setIcon(0, icon)
        self.color = color


class Plot(QFrame, Ui_Plot):
    """ Plot container.

    """
    def __init__(self, parent=None):
        """ Constructor.

        @param parent ancestor of this widget
        """
        QFrame.__init__(self, parent)
        self.setupUi(self)
        self.curves = {}

    def setSession(self, session, tickerId, *indexes):
        """ Associate a session with this instance.

        @param session Session instance
        @param tickerId id of ticker as integer
        @param *indexes unused
        @return None
        """
        self.session = session
        self.tickerId = tickerId
        self.setupControls()
        session.registerMeta(self)

    def setupControls(self):
        """ Configure the controls tree for this instance.

        @return None
        """
        tree = self.controlTree
        tree.headerItem().setHidden(True)
        ticker = self.session.tickerCollection[self.tickerId]
        curves = self.curves
        for key, series in sorted(ticker.series.items()):
            color = QColor('red')
            icon = colorIcon(color)
            item = ControlTreeItem(tree, TickType.getField(key), icon, color)
            item.y = series
            curves[item] = QwtPlotCurve()
            for index in series.indexes:
                color = QColor('blue')
                icon = colorIcon(color)
                subitem = ControlTreeItem(item, index.name, icon, color)
                subitem.y = index
                curves[subitem] = QwtPlotCurve()
        for col in range(tree.columnCount()):
            tree.resizeColumnToContents(col)
        self.plotSplitter.setSizes([100, 600])

    def on_session_TickPrice_TickSize(self, message):
        """ Signal handler for TickPrice and TickSize session messages.

        @param message Message instance
        @return None
        """
        if message.tickerId != self.tickerId:
            return
        for item, curve in self.curves.items():
            if not curve.isVisible():
                continue
            y = item.y
            x = range(len(y))
            curve.setData(x, y)
        self.plotWidget.replot()

    def on_controlTree_itemDoubleClicked(self, item, column):
        """ Signal handler for control tree double click.

        @param item clicked tree widget item
        @param column clicked tree widget column
        @return None
        """
        try:
            itemcolor = item.color
        except (AttributeError, ):
            pass
        else:
            color = QColorDialog.getColor(itemcolor, self)
            if color.isValid():
                item.color = color
                item.setIcon(column, colorIcon(color))
                try:
                    curve = self.curves[item]
                except (KeyError, ):
                    pass
                else:
                    curve.setPen(QPen(color))
                    if curve.isVisible:
                        self.plotWidget.replot()

    def on_controlTree_itemChanged(self, item, column):
        """ Signal handler for all changes to control tree items.

        @param item changed tree widget item
        @param column changed tree widget column
        @return None
        """
        state = item.checkState(column)
        self.enableCurve(item, enable=state==Qt.Checked)

    def enableCurve(self, item, enable=True):
        """ Sets the visibility and style of a plot curve.

        @param item tree widget item
        @param enabled if True, curve is configured and enabled,
                       otherwise curve is set invisible
        @return None
        """
        try:
            curve = self.curves[item]
        except (KeyError, ):
            return
        if enable:
            curve.setStyle(QwtPlotCurve.Lines)
            collection = self.session.tickerCollection
            y = item.y
            x = range(len(y))
            plot = self.plotWidget
            curve.setData(x, y)
            curve.attach(plot)
            curve.setVisible(True)
            curve.setPen(QPen(item.color))
        else:
            curve.setVisible(False)
        plot = self.plotWidget
        plot.updateLayout()
        plot.replot()
