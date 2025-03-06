#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 GUI resourece for inputing a string to be not part of a constraing list
===============================================================================



"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2017. 09. 25"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from PyQt6 import QtCore
from PyQt6 import QtWidgets


# from ui_string_dialog import  Ui_Dialog
from ui_single_list_selector import  Ui_Dialog
from resources_icons import roundButton

class UI_stringSelector(QtWidgets.QDialog):

  '''
  user interface for defining a string
  designed to be either used with the signal mechanism or reading the result

  usage :
  ui_ask = UI_String("give new model name or type exit ", "model name or exit", limiting_list = acceptance_list)
      ui_ask.exec_()
      model_name = ui_ask.getText()
  '''

  def __init__(self, prompt, theList, fokus=True):
    QtWidgets.QDialog.__init__(self, parent=None)
    self.ui = Ui_Dialog()
    self.ui.setupUi(self)
    roundButton(self.ui.pushAccept, "accept", tooltip="accept")
    roundButton(self.ui.pushReject, "reject", tooltip="reject")
    self.ui.pushAccept.hide()


    self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)


    self.ui.listWidget.addItems(theList)

    self.selection = None
    self.exec()
    self.show()

    # self.ui.pushAccept.clicked.connect(self.__accept)
    # self.ui.pushReject.clicked.connect(self.closeMe)

  def on_listWidget_itemClicked(self, v):
    # print("debugging", v.text())
    self.selection = v.text()
    self.ui.pushAccept.show()

  def on_pushAccept_pressed(self):
    self.close()


  def on_pushReject_pressed(self):
    self.close()

  def getSelection(self):
    return self.selection





if __name__ == '__main__':


  a = QtWidgets.QApplication([])

  w = UI_stringSelector("select", ["jacob","give name", "name"])
  w.setModal(True)
  w.show()
  r = w.getSelection()
  print(r)
  # a.exec()