# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'svg_generator_dialog_base.ui'
#
# Created: Mon Jun 19 01:47:09 2017
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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

class Ui_SvgBubblDialogBase(object):
    def setupUi(self, SvgBubblDialogBase):
        SvgBubblDialogBase.setObjectName(_fromUtf8("SvgBubblDialogBase"))
        SvgBubblDialogBase.resize(400, 300)
        self.button_box = QtGui.QDialogButtonBox(SvgBubblDialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.button_box.setObjectName(_fromUtf8("button_box"))
        self.comboBox = QtGui.QComboBox(SvgBubblDialogBase)
        self.comboBox.setGeometry(QtCore.QRect(120, 10, 161, 22))
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.label = QtGui.QLabel(SvgBubblDialogBase)
        self.label.setGeometry(QtCore.QRect(30, 10, 61, 21))
        self.label.setObjectName(_fromUtf8("label"))
        self.mFieldExpressionWidget = QgsFieldExpressionWidget(SvgBubblDialogBase)
        self.mFieldExpressionWidget.setGeometry(QtCore.QRect(110, 50, 200, 27))
        self.mFieldExpressionWidget.setObjectName(_fromUtf8("mFieldExpressionWidget"))

        self.retranslateUi(SvgBubblDialogBase)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("accepted()")), SvgBubblDialogBase.accept)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("rejected()")), SvgBubblDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(SvgBubblDialogBase)

    def retranslateUi(self, SvgBubblDialogBase):
        SvgBubblDialogBase.setWindowTitle(_translate("SvgBubblDialogBase", "Svg Image Generator", None))
        self.label.setText(_translate("SvgBubblDialogBase", "select layer", None))

from qgis.gui import QgsFieldExpressionWidget
