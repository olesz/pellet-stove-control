#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created: Tue Feb  7 18:29:20 2017
#	  by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
import sys
from datetime import timedelta
import signal
import re

import tcpclient

UI = None

try:
	_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
	def _fromUtf8(s):
		return s

try:
	_encoding = QtGui.QApplication.UnicodeUTF8
	def _translate(context, text, disambig):
		return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
	def _translate(context, text, disambig):
		return QtGui.QApplication.translate(context, text, disambig)

class Ui_PscdUi(object):

	loadValue = 0
	breakValue = 0
	state = 0

	def setupUi(self, PscdUi):
		self.pscdUi = PscdUi

		# remove title bar
		#self.pscdUi.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		#self.pscdUi.setWindowFlags(QtCore.Qt.CustomizeWindowHint)

		PscdUi.setObjectName(_fromUtf8("PscdUi"))
		PscdUi.resize(320, 240)
		sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(PscdUi.sizePolicy().hasHeightForWidth())
		PscdUi.setSizePolicy(sizePolicy)
		PscdUi.setAnimated(False)
		PscdUi.setTabShape(QtGui.QTabWidget.Triangular)
		self.centralwidget = QtGui.QWidget(PscdUi)
		self.centralwidget.setEnabled(True)
		sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
		self.centralwidget.setSizePolicy(sizePolicy)
		self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
		self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
		self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
		self.onOffBox = QtGui.QGroupBox(self.centralwidget)
		self.onOffBox.setObjectName(_fromUtf8("onOffBox"))
		self.onOffButton = QtGui.QPushButton(self.onOffBox)
		self.onOffButton.setGeometry(QtCore.QRect(10, 20, 141, 41))
		font = QtGui.QFont()
		font.setFamily(_fromUtf8("Courier New"))
		font.setPointSize(30)
		font.setBold(True)
		font.setWeight(75)
		self.onOffButton.setFont(font)
		self.onOffButton.setObjectName(_fromUtf8("onOffButton"))
		self.reverseButton = QtGui.QPushButton(self.onOffBox)
		self.reverseButton.setGeometry(QtCore.QRect(158, 20, 131, 41))
		font = QtGui.QFont()
		font.setFamily(_fromUtf8("Courier New"))
		font.setPointSize(30)
		font.setBold(True)
		font.setWeight(75)
		self.reverseButton.setFont(font)
		self.reverseButton.setObjectName(_fromUtf8("reverseButton"))
		self.verticalLayout_2.addWidget(self.onOffBox)
		self.loadBox = QtGui.QGroupBox(self.centralwidget)
		self.loadBox.setObjectName(_fromUtf8("loadBox"))
		self.increaseLoadButton = QtGui.QPushButton(self.loadBox)
		self.increaseLoadButton.setGeometry(QtCore.QRect(210, 20, 81, 41))
		font = QtGui.QFont()
		font.setFamily(_fromUtf8("Courier New"))
		font.setPointSize(32)
		font.setBold(True)
		font.setWeight(75)
		self.increaseLoadButton.setFont(font)
		self.increaseLoadButton.setObjectName(_fromUtf8("increaseLoadButton"))
		self.decreaseLoadButton = QtGui.QPushButton(self.loadBox)
		self.decreaseLoadButton.setGeometry(QtCore.QRect(8, 20, 81, 41))
		font = QtGui.QFont()
		font.setFamily(_fromUtf8("Courier New"))
		font.setPointSize(32)
		font.setBold(True)
		font.setWeight(75)
		self.decreaseLoadButton.setFont(font)
		self.decreaseLoadButton.setObjectName(_fromUtf8("decreaseLoadButton"))
		self.loadValueEdit = QtGui.QLineEdit(self.loadBox)
		self.loadValueEdit.setGeometry(QtCore.QRect(98, 10, 101, 51))
		font = QtGui.QFont()
		font.setFamily(_fromUtf8("Courier New"))
		font.setPointSize(32)
		font.setBold(True)
		font.setWeight(75)
		self.loadValueEdit.setFont(font)
		self.loadValueEdit.setAlignment(QtCore.Qt.AlignCenter)
		self.loadValueEdit.setObjectName(_fromUtf8("loadValueEdit"))
		self.verticalLayout_2.addWidget(self.loadBox)
		self.breakBox = QtGui.QGroupBox(self.centralwidget)
		self.breakBox.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
		self.breakBox.setObjectName(_fromUtf8("breakBox"))
		self.decreaseBreakButton = QtGui.QPushButton(self.breakBox)
		self.decreaseBreakButton.setGeometry(QtCore.QRect(8, 20, 81, 41))
		font = QtGui.QFont()
		font.setFamily(_fromUtf8("Courier New"))
		font.setPointSize(32)
		font.setBold(True)
		font.setWeight(75)
		self.decreaseBreakButton.setFont(font)
		self.decreaseBreakButton.setObjectName(_fromUtf8("decreaseBreakButton"))
		self.breakValueEdit = QtGui.QLineEdit(self.breakBox)
		self.breakValueEdit.setGeometry(QtCore.QRect(100, 10, 101, 51))
		font = QtGui.QFont()
		font.setFamily(_fromUtf8("Courier New"))
		font.setPointSize(32)
		font.setBold(True)
		font.setWeight(75)
		self.breakValueEdit.setFont(font)
		self.breakValueEdit.setAlignment(QtCore.Qt.AlignCenter)
		self.breakValueEdit.setObjectName(_fromUtf8("breakValueEdit"))
		self.increaseBreakButton = QtGui.QPushButton(self.breakBox)
		self.increaseBreakButton.setGeometry(QtCore.QRect(210, 20, 81, 41))
		font = QtGui.QFont()
		font.setFamily(_fromUtf8("Courier New"))
		font.setPointSize(32)
		font.setBold(True)
		font.setWeight(75)
		self.increaseBreakButton.setFont(font)
		self.increaseBreakButton.setObjectName(_fromUtf8("increaseBreakButton"))
		self.verticalLayout_2.addWidget(self.breakBox)
		PscdUi.setCentralWidget(self.centralwidget)

		self.retranslateUi(PscdUi)
		QtCore.QMetaObject.connectSlotsByName(PscdUi)
		
		self.decreaseBreakButton.clicked.connect(self.timeButtonClicked)
		self.decreaseBreakButton.setAutoRepeat(True)
		self.decreaseBreakButton.setAutoRepeatDelay(1000)
        	self.decreaseBreakButton.setAutoRepeatInterval(1000)
		self.increaseBreakButton.clicked.connect(self.timeButtonClicked)
		self.increaseBreakButton.setAutoRepeat(True)
		self.increaseBreakButton.setAutoRepeatDelay(1000)
        	self.increaseBreakButton.setAutoRepeatInterval(1000)
		
		self.decreaseLoadButton.clicked.connect(self.timeButtonClicked)
		self.decreaseLoadButton.setAutoRepeat(True)
		self.decreaseLoadButton.setAutoRepeatDelay(1000)
        	self.decreaseLoadButton.setAutoRepeatInterval(1000)
		self.increaseLoadButton.clicked.connect(self.timeButtonClicked)
		self.increaseLoadButton.setAutoRepeat(True)
		self.increaseLoadButton.setAutoRepeatDelay(1000)
        	self.increaseLoadButton.setAutoRepeatInterval(1000)
		
		self.onOffButton.clicked.connect(self.controlButtonClicked)
		self.reverseButton.clicked.connect(self.controlButtonClicked)

	def retranslateUi(self, PscdUi):
		PscdUi.setWindowTitle(_translate("PscdUi", "MainWindow", None))
		self.onOffBox.setTitle(_translate("PscdUi", "Be/Ki/Vissza", None))
		self.onOffButton.setText(_translate("PscdUi", "Be", None))
		self.reverseButton.setText(_translate("PscdUi", "Vissza", None))
		self.loadBox.setTitle(_translate("PscdUi", "Töltés", None))
		self.increaseLoadButton.setText(_translate("PscdUi", "+", None))
		self.decreaseLoadButton.setText(_translate("PscdUi", "-", None))
		self.loadValueEdit.setText(_translate("PscdUi", "0m0s", None))
		self.breakBox.setTitle(_translate("PscdUi", "Szünet", None))
		self.decreaseBreakButton.setText(_translate("PscdUi", "-", None))
		self.breakValueEdit.setText(_translate("PscdUi", "0m0s", None))
		self.increaseBreakButton.setText(_translate("PscdUi", "+", None))

	def onOffButtonOff(self):
		self.onOffButton.setText(_translate("PscdUi", "Ki", None))
		self.reverseButton.setText(_translate("PscdUi", "Vissza", None))
		self.reverseButton.setEnabled(False)
	
	def onOffButtonOn(self):
		self.onOffButton.setText(_translate("PscdUi", "Be", None))
		self.reverseButton.setText(_translate("PscdUi", "Vissza", None))
		self.reverseButton.setEnabled(True)
	
	def reverseButtonOn(self):
		self.reverseButton.setText(_translate("PscdUi", "<- STOP", None))
		self.onOffButton.setText(_translate("PscdUi", "Be", None))
		self.onOffButton.setEnabled(False)
	
	def reverseButtonOff(self):
		self.reverseButton.setText(_translate("PscdUi", "Vissza", None))
		self.onOffButton.setText(_translate("PscdUi", "Be", None))
		self.onOffButton.setEnabled(True)

	def setLoadValue(self, value):
		self.loadValue = value
		self.loadValueEdit.setText(self.convertToMinSec(self.loadValue))

	def setBreakValue(self, value):
		self.breakValue = value
		self.breakValueEdit.setText(self.convertToMinSec(self.breakValue))

	def controlButtonClicked(self):
		if self.pscdUi.sender().objectName() == "onOffButton":
			if self.onOffButton.text() == "Be":
				self.onOffButtonOff()
				tcpclient.set_state("START\r\n")
			elif self.onOffButton.text() == "Ki":
				self.onOffButtonOn()
				tcpclient.set_state("STOP\r\n")
		elif self.pscdUi.sender().objectName() == "reverseButton":
			if self.reverseButton.text() == "Vissza":
				self.reverseButtonOn()
				tcpclient.set_state("REVERSE\r\n")
			elif self.reverseButton.text() == "<- STOP":
				self.reverseButtonOff()
				tcpclient.set_state("STOP\r\n")

	def convertToMinSec(self, counter):
		d = timedelta(seconds = counter)
		return QtCore.QString.number(d.seconds/60) + "m" + QtCore.QString.number(d.seconds%60) + "s"

	def timeButtonClicked(self):
		if self.pscdUi.sender().objectName() == "decreaseBreakButton" or self.pscdUi.sender().objectName() == "decreaseLoadButton":
			direction = -1
		elif self.pscdUi.sender().objectName() == "increaseBreakButton" or self.pscdUi.sender().objectName() == "increaseLoadButton":
			direction = 1

		if self.pscdUi.sender().isDown():
       	    		if self.state == 0:
               			self.state = 1
               			self.pscdUi.sender().setAutoRepeatInterval(100)
				delta = direction * 10
            		else:
				delta = direction * 10
       		elif self.state == 1:
            		self.state = 0
       	    		self.pscdUi.sender().setAutoRepeatInterval(1000)
			delta = 0
        	else:
			delta = direction
		
		if self.pscdUi.sender().objectName() == "increaseLoadButton" or self.pscdUi.sender().objectName() == "decreaseLoadButton":
			if (self.loadValue + delta >= 0 and self.loadValue + delta <= 600):
				self.loadValue += delta
				self.loadValueEdit.setText(self.convertToMinSec(self.loadValue))
				
				tcpclient.set_state("LOAD_TIME " + str(self.loadValue) + "\r\n")
				
		elif self.pscdUi.sender().objectName() == "increaseBreakButton" or self.pscdUi.sender().objectName() == "decreaseBreakButton":
			if (self.breakValue + delta >= 0 and self.breakValue + delta <= 600):
				self.breakValue += delta
				self.breakValueEdit.setText(self.convertToMinSec(self.breakValue))
				
				tcpclient.set_state("LOAD_BREAK_TIME " + str(self.breakValue) + "\r\n")

def get_initial_state():
	global UI

	status = tcpclient.get_state()
	print "aaa - " + str(status)
	analyze_status(status)

def status_changed(state):

	print UI
	print "x" + state + "x"
	pattern_data_id = re.compile('^NOTIFY-(.*)$')

	# get the id part and call analyze
	analyze_status(pattern_data_id.match(state).group(1))

def analyze_status(state):
	global UI

	print UI

	pattern_status_analyze = re.compile('STATUS ([A-Z_]+) ([0-9]+) ([0-9]+) ([A-Za-z0-9_]*)')
	
	state_group = pattern_status_analyze.match(state)

	UI.setLoadValue(int(state_group.group(2)))
	UI.setBreakValue(int(state_group.group(3)))

	if state_group.group(1) == "STOP":
		UI.onOffButtonOn()
		# if here an error notification have to be thrown
		# which cannot be dismissed just by a reboot
	elif state_group.group(1) == "RUN_FORWARD":
		UI.onOffButtonOff()
	elif state_group.group(1) == "RUN_FORWARD_BREAK":
		UI.onOffButtonOff()
	elif state_group.group(1) == "RUN_BACKWARD":
		UI.reverseButtonOn()
	elif state_group.group(1) == "ERROR":
		pass
		# here an error notification have to be thrown
		# which cannot be dismissed just by a reboot
	

def app_exit():
	tcpclient.unsubscribe()
	tcpclient.stop_socket()
	QtGui.QApplication.quit()

def sigint_handler(*args):
	app_exit()	

if __name__ == "__main__":
	signal.signal(signal.SIGINT, sigint_handler)
	app = QtGui.QApplication(sys.argv)
	
	timer = QtCore.QTimer()
	timer.start(500)  # You may change this if you wish.
	timer.timeout.connect(lambda: None)
	
	tcpclient.start_socket('127.0.0.1', 5005)
	
	pscdUi = QtGui.QMainWindow()
	pscdUi.setWindowFlags(QtCore.Qt.FramelessWindowHint)

	UI = Ui_PscdUi()
	UI.setupUi(pscdUi)
	
	get_initial_state()

	#tcpclient.subscribe()
	
	pscdUi.show()

	app.exec_()
	
	app_exit()
	
	

