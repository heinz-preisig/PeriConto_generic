# Form implementation generated from reading ui file 'BricksSchemata_gui.ui'
#
# Created by: PyQt6 UI code generator 6.6.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(963, 963)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(parent=self.centralwidget)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(560, 0, 351, 51))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.pushMinimise = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_2)
        self.pushMinimise.setObjectName("pushMinimise")
        self.horizontalLayout_2.addWidget(self.pushMinimise)
        self.pushMaximise = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_2)
        self.pushMaximise.setObjectName("pushMaximise")
        self.horizontalLayout_2.addWidget(self.pushMaximise)
        self.pushNormal = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_2)
        self.pushNormal.setObjectName("pushNormal")
        self.horizontalLayout_2.addWidget(self.pushNormal)
        self.horizontalLayoutWidget_3 = QtWidgets.QWidget(parent=self.centralwidget)
        self.horizontalLayoutWidget_3.setGeometry(QtCore.QRect(20, 84, 891, 51))
        self.horizontalLayoutWidget_3.setObjectName("horizontalLayoutWidget_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_3)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushOntologyCreate = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_3)
        self.pushOntologyCreate.setObjectName("pushOntologyCreate")
        self.horizontalLayout_3.addWidget(self.pushOntologyCreate)
        self.pushOntologyLoad = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_3)
        self.pushOntologyLoad.setObjectName("pushOntologyLoad")
        self.horizontalLayout_3.addWidget(self.pushOntologyLoad)
        self.pushExit = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_3)
        self.pushExit.setObjectName("pushExit")
        self.horizontalLayout_3.addWidget(self.pushExit)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.pushTreeVisualise = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_3)
        self.pushTreeVisualise.setObjectName("pushTreeVisualise")
        self.horizontalLayout_3.addWidget(self.pushTreeVisualise)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.pushOntologySave = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_3)
        self.pushOntologySave.setObjectName("pushOntologySave")
        self.horizontalLayout_3.addWidget(self.pushOntologySave)
        self.pushOntologySaveAs = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_3)
        self.pushOntologySaveAs.setObjectName("pushOntologySaveAs")
        self.horizontalLayout_3.addWidget(self.pushOntologySaveAs)
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 10, 231, 31))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.brickTree = QtWidgets.QTreeWidget(parent=self.centralwidget)
        self.brickTree.setGeometry(QtCore.QRect(250, 330, 341, 411))
        self.brickTree.setAutoExpandDelay(1)
        self.brickTree.setColumnCount(0)
        self.brickTree.setObjectName("brickTree")
        self.brickTree.header().setVisible(False)
        self.brickTree.header().setCascadingSectionResizes(False)
        self.verticalLayoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(250, 200, 160, 128))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushBrickAddItem = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.pushBrickAddItem.setObjectName("pushBrickAddItem")
        self.verticalLayout.addWidget(self.pushBrickAddItem)
        self.pushBrickAddPrimitive = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.pushBrickAddPrimitive.setObjectName("pushBrickAddPrimitive")
        self.verticalLayout.addWidget(self.pushBrickAddPrimitive)
        self.pushBrickItemOrPrimitiveRename = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.pushBrickItemOrPrimitiveRename.setObjectName("pushBrickItemOrPrimitiveRename")
        self.verticalLayout.addWidget(self.pushBrickItemOrPrimitiveRename)
        self.pushBrickRemoveItem = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.pushBrickRemoveItem.setObjectName("pushBrickRemoveItem")
        self.verticalLayout.addWidget(self.pushBrickRemoveItem)
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(parent=self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(20, 200, 171, 111))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.pushBrickCreate = QtWidgets.QPushButton(parent=self.verticalLayoutWidget_2)
        self.pushBrickCreate.setObjectName("pushBrickCreate")
        self.verticalLayout_2.addWidget(self.pushBrickCreate)
        self.pushBrickRemove = QtWidgets.QPushButton(parent=self.verticalLayoutWidget_2)
        self.pushBrickRemove.setObjectName("pushBrickRemove")
        self.verticalLayout_2.addWidget(self.pushBrickRemove)
        self.pushBrickRename = QtWidgets.QPushButton(parent=self.verticalLayoutWidget_2)
        self.pushBrickRename.setObjectName("pushBrickRename")
        self.verticalLayout_2.addWidget(self.pushBrickRename)
        self.listBricks = QtWidgets.QListWidget(parent=self.centralwidget)
        self.listBricks.setGeometry(QtCore.QRect(20, 330, 171, 411))
        self.listBricks.setObjectName("listBricks")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushMinimise.setText(_translate("MainWindow", "min"))
        self.pushMaximise.setText(_translate("MainWindow", "max"))
        self.pushNormal.setText(_translate("MainWindow", "norm"))
        self.pushOntologyCreate.setText(_translate("MainWindow", "create"))
        self.pushOntologyLoad.setText(_translate("MainWindow", "load"))
        self.pushExit.setText(_translate("MainWindow", "exit"))
        self.pushTreeVisualise.setText(_translate("MainWindow", "visualise"))
        self.pushOntologySave.setText(_translate("MainWindow", "save"))
        self.pushOntologySaveAs.setText(_translate("MainWindow", "save as"))
        self.label.setText(_translate("MainWindow", "Ontology Bricks"))
        self.pushBrickAddItem.setText(_translate("MainWindow", "add item"))
        self.pushBrickAddPrimitive.setText(_translate("MainWindow", "add primitive"))
        self.pushBrickItemOrPrimitiveRename.setText(_translate("MainWindow", "rename"))
        self.pushBrickRemoveItem.setText(_translate("MainWindow", "remove item|primitive"))
        self.pushBrickCreate.setText(_translate("MainWindow", "create"))
        self.pushBrickRemove.setText(_translate("MainWindow", "remove brick"))
        self.pushBrickRename.setText(_translate("MainWindow", "rename"))
