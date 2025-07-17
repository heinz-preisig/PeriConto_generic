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
__modified__ = "2025-02-18 added validation"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from PyQt6 import QtCore
from PyQt6 import QtGui
from PyQt6 import QtWidgets

from Utilities import camelCase
from pop_up_message_box import makeMessageBox
from resources_icons import roundButton
# from ui_string_dialog import  Ui_Dialog
from ui_string_dialog import Ui_Dialog


class UI_String(QtWidgets.QDialog):
  '''
  user interface for defining a string
  designed to be either used with the signal mechanism or reading the result

  usage :
  ui_ask = UI_String("give new model name or type exit ", "model name or exit", limiting_list = acceptance_list)
      ui_ask.exec_()
      model_name = ui_ask.getText()
  '''

  # aborted = QtCore.pyqtSignal()
  accepted = QtCore.pyqtSignal(str)

  def __init__(self, prompt, value=None, placeholdertext="", limiting_list=[], fokus=True, validator=None):
    """
    Serves the purpose of defining a string allowing for accepting or rejecting the result
    :param prompt: displayed in the window title
    :param placeholdertext: place holder shown in the line edit
    :param accept: method/function reference
    :param reject: method/function reference
    :param validator in [integer, decimal, readl, bool]
    """
    # TODO: add validator
    QtWidgets.QDialog.__init__(self, parent=None)
    self.ui = Ui_Dialog()
    self.ui.setupUi(self)

    self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
    self.placeholdertext = placeholdertext
    self.limiting_list = limiting_list
    self.validator = validator
    self.text = None

    roundButton(self.ui.pushAccept, "accept", tooltip="accept")
    roundButton(self.ui.pushReject, "reject", tooltip="reject")
    self.ui.pushAccept.hide()

    self.ui.pushAccept.clicked.connect(self.__accept)
    self.ui.pushReject.clicked.connect(self.closeMe)
    self.ui.lineEdit.textEdited.connect(self.__changedText)
    self.ui.lineEdit.returnPressed.connect(self.returnPressed)

    self.ui.lineEdit.textChanged.connect(self.newText)
    # self.ui.pushReject.setFocus()
    self.ui.lineEdit.setFocus()

    val=None
    if placeholdertext:
      self.ui.lineEdit.setPlaceholderText(placeholdertext)
    elif validator:
      self.ui.lineEdit.setPlaceholderText(validator)

    # self.adjust = None
    if validator:
      if validator == "integer":
        val = r"^[-+]?\d+$"
      elif validator == "decimal":
        val = r"-?(\d*\.\d+|\d+\.\d*)"
      elif validator == "real":
        val = r"^([-+]?\d*\.?\d+)(?:[eE]([-+]?\d+))?$"
      elif validator == "boolean":
        val = r"^(?:(1|y(?:es)?|t(?:rue)?|on)|(0|n(?:o)?|f(?:alse)?|off))$"
      elif validator == "camel":
        val = r"^([a-zA-Z][a-zA-Z0-9]+\s)*$"
      elif validator == "name":
        val = r"^[a-zA-Z][a-zA-Z0-9]*$"
      elif validator == "name_upper":
        # val = r"^[a-zA-Z][a-zA-Z0-9]*$"
        val = r"^([a-zA-Z][a-zA-Z0-9]+\s)*$"
        # self.adjust = r"^[A-Z][A-Z0-9-]*$"
      elif validator == "url":
        val = r"^[A-Z][A-Z0-9-]*$"
      elif validator == "comment":
        val = r""
      elif validator == "string":
        val = r""
      else:
        makeMessageBox(">>>> should not come here, wrong validator %s"%validator, ["OK"])



      v = QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(val))
      self.ui.lineEdit.setValidator(v)
      if value:
        self.ui.lineEdit.setText(value)
        self.ui.pushAccept.show()
    self.exec()

    if fokus:
      self.ui.lineEdit.setFocus()

  def setText(self, txt):
    self.ui.lineEdit.setText(str(txt))

  def __changedText(self, Qtext):
    text = Qtext
    self.text = self.ui.lineEdit.text()
    if len(text) == 0:
      return

    if self.validator == "camel":
      text = camelCase(text)
      # self.ui.lineEdit.setText(text) # note: that defeats the purpose

    elif self.validator == "name_upper":
      text = text.upper().replace(" ","-")
      # text = text.replace(" ","-")
      self.ui.lineEdit.setText(text)

    elif self.validator == "name":
      text = text.lower()
      self.ui.lineEdit.setText(text)

    elif self.validator == "url":
      text = text.lower()
      self.ui.lineEdit.setText(text)

    if (text in self.limiting_list) or (text[0] == " "):
      self.ui.lineEdit.setStyleSheet("color: red; background-color: white")
      self.ui.pushAccept.hide()
    else:
      self.ui.lineEdit.setStyleSheet("color: black; background-color: white")
      self.ui.pushAccept.show()

  def __accept(self):
    self.accepted.emit(self.ui.lineEdit.text())
    self.text = self.ui.lineEdit.text()
    self.close()

  def __reject(self):
    self.text = None
    self.close()

  # def on_lineEdit_returnPressed(self):
  #   self.__accept()

  def returnPressed(self):
    # print("return pressed")
    self.__accept()
    return

  def getText(self):
    text = self.ui.lineEdit.text()
    if text in self.limiting_list:
      text = None
    return text

  def newText(self, txt):
    # print("changed text:", txt, len(txt))
    if len(txt) == 0:
      # self.ui.pushReject.setFocus()
      self.ui.lineEdit.setPlaceholderText(self.placeholdertext)
      self.ui.pushAccept.hide()
    else:
      self.ui.pushAccept.setFocus()
      self.ui.lineEdit.setFocus()

  def closeMe(self):
    self.ui.lineEdit.clear()
    self.close()


# ============================ testing ======================
#
#
def changing(txt):
  print("changing:", txt)


if __name__ == '__main__':
  # from resource.resource_initialisation import DIRECTORIES

  from PyQt6 import QtCore
  from PyQt6 import QtWidgets

  a = QtWidgets.QApplication([])
  # val_int = r"^[-+]?\d+$"
  # val_real = r"-?(\d*\.\d+|\d+\.\d*)"
  # var_exp = r"^([-+]?\d*\.?\d+)(?:[eE]([-+]?\d+))?$"
  # var_bool = r"^(?:(1|y(?:es)?|t(?:rue)?|on)|(0|n(?:o)?|f(?:alse)?|off))$"
  # var_url = r"^(?:(1|y(?:es)?|t(?:rue)?|on)|(0|n(?:o)?|f(?:alse)?|off))$"
  w = UI_String("give name", placeholdertext="name", limiting_list=["1"], validator="name_upper")
  w.show()
  s = w.text
  print(s)
  # z = camelCase(s) # s.title().replace(" ","")
  # print(z)
