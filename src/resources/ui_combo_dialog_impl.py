#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 GUI resource for inputting a string to be not part of a constraining list
===============================================================================



"""

__project__ = "PeriConto"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2024-12-17"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from PyQt6 import QtCore
from PyQt6 import QtWidgets


# from ui_string_dialog import  Ui_Dialog
from ui_combo_dialog import  Ui_ComboDialog
from resources_icons import roundButton

class UI_ComboDialog(QtWidgets.QDialog):

  """
  user interface for to select from a list

  usage :
  ui_ask = UI_String("give new model name or type exit ", "model name or exit", acceptance_list)
      ui_ask.exec_()
      model_name = ui_ask.getText()
  """

  def __init__(self, prompt, theList, fokus=True):
    QtWidgets.QDialog.__init__(self, parent=None)
    self.ui = Ui_ComboDialog()
    self.ui.setupUi(self)
    roundButton(self.ui.pushAccept, "accept", tooltip="accept")
    roundButton(self.ui.pushReject, "reject", tooltip="reject")
    self.ui.pushAccept.hide()

    self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
    self.ui.label.setText(prompt)
    self.ui.comboBox.addItems(theList)

    self.selection = theList[0]

    self.exec()
    self.show()

  def on_comboBox_currentTextChanged(self, v):
    # print("debugging", v)
    self.selection = v
    self.ui.pushAccept.show()

  def on_pushAccept_pressed(self):
    self.close()


  def on_pushReject_pressed(self):
    self.selection = None
    self.close()

  def getSelection(self):
    return self.selection





if __name__ == '__main__':


  a = QtWidgets.QApplication([])

  w = UI_ComboDialog("select", ["jacob","give name", "name"])
  w.setModal(True)
  w.show()
  r = w.getSelection()
  print("got:", r)
  # a.exec()