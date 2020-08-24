# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'grid_coordinates_test.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.topleft = QtWidgets.QLabel(Form)
        self.topleft.setObjectName("topleft")
        self.gridLayout.addWidget(self.topleft, 0, 0, 1, 1)
        self.topright = QtWidgets.QLabel(Form)
        self.topright.setObjectName("topright")
        self.gridLayout.addWidget(self.topright, 0, 1, 1, 1)
        self.bottomleft = QtWidgets.QLabel(Form)
        self.bottomleft.setObjectName("bottomleft")
        self.gridLayout.addWidget(self.bottomleft, 1, 0, 1, 1)
        self.bottomright = QtWidgets.QLabel(Form)
        self.bottomright.setObjectName("bottomright")
        self.gridLayout.addWidget(self.bottomright, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.topleft.setText(_translate("Form", "TextLabel"))
        self.topright.setText(_translate("Form", "TextLabel"))
        self.bottomleft.setText(_translate("Form", "TextLabel"))
        self.bottomright.setText(_translate("Form", "TextLabel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

