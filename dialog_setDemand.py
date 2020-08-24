# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog_setDemand.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dialog_setDemand(object):
    def setupUi(self, dialog_setDemand):
        dialog_setDemand.setObjectName("dialog_setDemand")
        dialog_setDemand.resize(470, 384)
        self.verticalLayout = QtWidgets.QVBoxLayout(dialog_setDemand)
        self.verticalLayout.setObjectName("verticalLayout")
        self.demand_dialog_verticalLayout = QtWidgets.QVBoxLayout()
        self.demand_dialog_verticalLayout.setObjectName("demand_dialog_verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtWidgets.QLabel(dialog_setDemand)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.dialog_setDemand_fixed_lineEdit = QtWidgets.QLineEdit(dialog_setDemand)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.dialog_setDemand_fixed_lineEdit.setFont(font)
        self.dialog_setDemand_fixed_lineEdit.setObjectName("dialog_setDemand_fixed_lineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.dialog_setDemand_fixed_lineEdit)
        self.label_3 = QtWidgets.QLabel(dialog_setDemand)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.dialog_setDemand_variable_lineEdit = QtWidgets.QLineEdit(dialog_setDemand)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.dialog_setDemand_variable_lineEdit.setFont(font)
        self.dialog_setDemand_variable_lineEdit.setObjectName("dialog_setDemand_variable_lineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.dialog_setDemand_variable_lineEdit)
        self.dialog_setDemand_plotButton = QtWidgets.QPushButton(dialog_setDemand)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.dialog_setDemand_plotButton.setFont(font)
        self.dialog_setDemand_plotButton.setObjectName("dialog_setDemand_plotButton")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.dialog_setDemand_plotButton)
        self.demand_dialog_verticalLayout.addLayout(self.formLayout)
        spacerItem = QtWidgets.QSpacerItem(0, 12, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.demand_dialog_verticalLayout.addItem(spacerItem)
        self.line = QtWidgets.QFrame(dialog_setDemand)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.demand_dialog_verticalLayout.addWidget(self.line)
        self.dialog_setDemand_buttonBox = QtWidgets.QDialogButtonBox(dialog_setDemand)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.dialog_setDemand_buttonBox.setFont(font)
        self.dialog_setDemand_buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close|QtWidgets.QDialogButtonBox.Ok)
        self.dialog_setDemand_buttonBox.setObjectName("dialog_setDemand_buttonBox")
        self.demand_dialog_verticalLayout.addWidget(self.dialog_setDemand_buttonBox)
        self.verticalLayout.addLayout(self.demand_dialog_verticalLayout)

        self.retranslateUi(dialog_setDemand)
        QtCore.QMetaObject.connectSlotsByName(dialog_setDemand)

    def retranslateUi(self, dialog_setDemand):
        _translate = QtCore.QCoreApplication.translate
        dialog_setDemand.setWindowTitle(_translate("dialog_setDemand", "Dialog"))
        self.label_2.setText(_translate("dialog_setDemand", "Fixed demand"))
        self.label_3.setText(_translate("dialog_setDemand", "Variable change"))
        self.dialog_setDemand_plotButton.setText(_translate("dialog_setDemand", "Plot"))

