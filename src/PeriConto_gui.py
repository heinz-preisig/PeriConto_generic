# Form implementation generated from reading ui file 'PeriConto_gui.ui'
#
# Created by: PyQt6 UI code generator 6.6.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1593, 808)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBoxTree = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.groupBoxTree.setGeometry(QtCore.QRect(300, 140, 761, 621))
        self.groupBoxTree.setObjectName("groupBoxTree")
        self.treeClass = QtWidgets.QTreeWidget(parent=self.groupBoxTree)
        self.treeClass.setGeometry(QtCore.QRect(10, 31, 521, 401))
        self.treeClass.setAutoExpandDelay(1)
        self.treeClass.setColumnCount(0)
        self.treeClass.setObjectName("treeClass")
        self.treeClass.header().setVisible(False)
        self.treeClass.header().setCascadingSectionResizes(False)
        self.groupBoxEditor = QtWidgets.QGroupBox(parent=self.groupBoxTree)
        self.groupBoxEditor.setGeometry(QtCore.QRect(10, 450, 951, 171))
        self.groupBoxEditor.setObjectName("groupBoxEditor")
        self.gridLayoutWidget = QtWidgets.QWidget(parent=self.groupBoxEditor)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 40, 731, 80))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.pushAddPrimitive = QtWidgets.QPushButton(parent=self.gridLayoutWidget)
        self.pushAddPrimitive.setObjectName("pushAddPrimitive")
        self.gridLayout.addWidget(self.pushAddPrimitive, 0, 2, 1, 1)
        self.pushRemovePrimitive = QtWidgets.QPushButton(parent=self.gridLayoutWidget)
        self.pushRemovePrimitive.setObjectName("pushRemovePrimitive")
        self.gridLayout.addWidget(self.pushRemovePrimitive, 2, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 1, 1, 1)
        self.pushAddSubclass = QtWidgets.QPushButton(parent=self.gridLayoutWidget)
        self.pushAddSubclass.setObjectName("pushAddSubclass")
        self.gridLayout.addWidget(self.pushAddSubclass, 0, 0, 1, 1)
        self.pushAddExistingClass = QtWidgets.QPushButton(parent=self.gridLayoutWidget)
        self.pushAddExistingClass.setObjectName("pushAddExistingClass")
        self.gridLayout.addWidget(self.pushAddExistingClass, 0, 6, 1, 1)
        self.pushRemoveClass = QtWidgets.QPushButton(parent=self.gridLayoutWidget)
        self.pushRemoveClass.setObjectName("pushRemoveClass")
        self.gridLayout.addWidget(self.pushRemoveClass, 2, 8, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 7, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout.addItem(spacerItem2, 0, 10, 1, 1)
        self.pushRemoveSubClass = QtWidgets.QPushButton(parent=self.gridLayoutWidget)
        self.pushRemoveSubClass.setObjectName("pushRemoveSubClass")
        self.gridLayout.addWidget(self.pushRemoveSubClass, 2, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout.addItem(spacerItem3, 0, 5, 1, 1)
        self.pushRemoveClassLink = QtWidgets.QPushButton(parent=self.gridLayoutWidget)
        self.pushRemoveClassLink.setObjectName("pushRemoveClassLink")
        self.gridLayout.addWidget(self.pushRemoveClassLink, 2, 6, 1, 1)
        self.pushAddNewClass = QtWidgets.QPushButton(parent=self.gridLayoutWidget)
        self.pushAddNewClass.setObjectName("pushAddNewClass")
        self.gridLayout.addWidget(self.pushAddNewClass, 0, 8, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout.addItem(spacerItem4, 1, 0, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout.addItem(spacerItem5, 1, 2, 1, 1)
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout.addItem(spacerItem6, 1, 6, 1, 1)
        spacerItem7 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout.addItem(spacerItem7, 1, 8, 1, 1)
        self.groupBoxClassList = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.groupBoxClassList.setGeometry(QtCore.QRect(20, 140, 261, 471))
        self.groupBoxClassList.setObjectName("groupBoxClassList")
        self.listClasses = QtWidgets.QListWidget(parent=self.groupBoxClassList)
        self.listClasses.setGeometry(QtCore.QRect(5, 30, 251, 401))
        self.listClasses.setObjectName("listClasses")
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(parent=self.centralwidget)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(100, 20, 951, 80))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushLoad = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_2)
        self.pushLoad.setObjectName("pushLoad")
        self.horizontalLayout_2.addWidget(self.pushLoad)
        self.pushCreate = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_2)
        self.pushCreate.setObjectName("pushCreate")
        self.horizontalLayout_2.addWidget(self.pushCreate)
        self.pushVisualise = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_2)
        self.pushVisualise.setObjectName("pushVisualise")
        self.horizontalLayout_2.addWidget(self.pushVisualise)
        self.pushSave = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_2)
        self.pushSave.setObjectName("pushSave")
        self.horizontalLayout_2.addWidget(self.pushSave)
        self.pushSaveAs = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_2)
        self.pushSaveAs.setObjectName("pushSaveAs")
        self.horizontalLayout_2.addWidget(self.pushSaveAs)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem8)
        self.pushMinimise = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_2)
        self.pushMinimise.setObjectName("pushMinimise")
        self.horizontalLayout_2.addWidget(self.pushMinimise)
        self.pushMaximise = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_2)
        self.pushMaximise.setObjectName("pushMaximise")
        self.horizontalLayout_2.addWidget(self.pushMaximise)
        self.pushNormal = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_2)
        self.pushNormal.setObjectName("pushNormal")
        self.horizontalLayout_2.addWidget(self.pushNormal)
        self.pushExit = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_2)
        self.pushExit.setObjectName("pushExit")
        self.horizontalLayout_2.addWidget(self.pushExit)
        self.groupElucidation = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.groupElucidation.setGeometry(QtCore.QRect(1079, 140, 461, 621))
        self.groupElucidation.setObjectName("groupElucidation")
        self.pushAddElucidation = QtWidgets.QPushButton(parent=self.groupElucidation)
        self.pushAddElucidation.setGeometry(QtCore.QRect(20, 490, 101, 23))
        self.pushAddElucidation.setObjectName("pushAddElucidation")
        self.textElucidation = QtWidgets.QPlainTextEdit(parent=self.groupElucidation)
        self.textElucidation.setGeometry(QtCore.QRect(10, 30, 441, 401))
        self.textElucidation.setObjectName("textElucidation")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBoxTree.setTitle(_translate("MainWindow", "ontology tree"))
        self.groupBoxEditor.setTitle(_translate("MainWindow", "ontology editor"))
        self.pushAddPrimitive.setText(_translate("MainWindow", "add primitive"))
        self.pushRemovePrimitive.setText(_translate("MainWindow", "remove primitive"))
        self.pushAddSubclass.setText(_translate("MainWindow", "add item"))
        self.pushAddExistingClass.setText(_translate("MainWindow", "add existing class"))
        self.pushRemoveClass.setText(_translate("MainWindow", "remove class"))
        self.pushRemoveSubClass.setText(_translate("MainWindow", "remove item"))
        self.pushRemoveClassLink.setText(_translate("MainWindow", "remove class link"))
        self.pushAddNewClass.setText(_translate("MainWindow", "add new class"))
        self.groupBoxClassList.setTitle(_translate("MainWindow", "class path"))
        self.pushLoad.setText(_translate("MainWindow", "PushButton"))
        self.pushCreate.setText(_translate("MainWindow", "PushButton"))
        self.pushVisualise.setText(_translate("MainWindow", "PushButton"))
        self.pushSave.setText(_translate("MainWindow", "PushButton"))
        self.pushSaveAs.setText(_translate("MainWindow", "PushButton"))
        self.pushMinimise.setText(_translate("MainWindow", "min"))
        self.pushMaximise.setText(_translate("MainWindow", "max"))
        self.pushNormal.setText(_translate("MainWindow", "norm"))
        self.pushExit.setText(_translate("MainWindow", "exit"))
        self.groupElucidation.setTitle(_translate("MainWindow", "selection elucidation"))
        self.pushAddElucidation.setText(_translate("MainWindow", "add changes"))
