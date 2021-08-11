# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\Media\Downloads\Temp\python_test\updater\updater.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1022, 641)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("res/juice.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.counter = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.counter.sizePolicy().hasHeightForWidth())
        self.counter.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.counter.setFont(font)
        self.counter.setObjectName("counter")
        self.horizontalLayout.addWidget(self.counter)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setStyleSheet("font: 12pt \"幼圆\";\n"
"")
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.refreshButton = QtWidgets.QPushButton(self.centralwidget)
        self.refreshButton.setMinimumSize(QtCore.QSize(60, 60))
        self.refreshButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.refreshButton.setStyleSheet("QPushButton{\n"
"  background-color: transparent;\n"
"  border-radius:30px;\n"
"}\n"
"QPushButton::hover{\n"
"  background-color: rgb(200, 200, 200);\n"
"  border: none;\n"
"}\n"
"QPushButton::pressed{\n"
"  background-color: rgb(170, 170, 170);\n"
"  border: none;\n"
"}")
        self.refreshButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("res/refresh.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.refreshButton.setIcon(icon1)
        self.refreshButton.setIconSize(QtCore.QSize(60, 60))
        self.refreshButton.setFlat(False)
        self.refreshButton.setObjectName("refreshButton")
        self.horizontalLayout.addWidget(self.refreshButton, 0, QtCore.Qt.AlignRight)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.terminalText = QtWidgets.QTextBrowser(self.centralwidget)
        self.terminalText.setMinimumSize(QtCore.QSize(0, 90))
        self.terminalText.setMaximumSize(QtCore.QSize(16777215, 300))
        font = QtGui.QFont()
        font.setFamily("YaHei Consolas Hybrid")
        self.terminalText.setFont(font)
        self.terminalText.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.terminalText.setObjectName("terminalText")
        self.gridLayout.addWidget(self.terminalText, 2, 0, 1, 1)
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setMinimumSize(QtCore.QSize(1000, 400))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(12)
        self.tableWidget.setFont(font)
        self.tableWidget.setStyleSheet("")
        self.tableWidget.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.tableWidget.setShowGrid(False)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(8)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(7, item)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.tableWidget, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1022, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.tableWidget, self.refreshButton)
        MainWindow.setTabOrder(self.refreshButton, self.terminalText)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "果酱的软件更新器"))
        self.counter.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" color:#fe4365;\">0</span></p></body></html>"))
        self.label.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600;\">款软件可升级</span></p></body></html>"))
        self.terminalText.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'YaHei Consolas Hybrid\'; font-size:9.07563pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt;\">[控制台信息]</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9pt;\"><br /></p></body></html>"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "logo"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "name"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "desc"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "local_version"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "latest_version"))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "github_button"))
        item = self.tableWidget.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "path_button"))
        item = self.tableWidget.horizontalHeaderItem(7)
        item.setText(_translate("MainWindow", "update_button"))

