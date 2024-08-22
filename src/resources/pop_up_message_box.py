#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 Ontology design facility
===============================================================================

This program is part of the ProcessModelling suite

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "11.11.2019"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "5.04"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import sys

from PyQt6 import QtWidgets, QtCore

# QtWidgets.QMessageBox.StandardButton.OK
BUTTONS = {
        "OK"             : QtWidgets.QMessageBox.StandardButton.Ok,
        "NO"             : QtWidgets.QMessageBox.StandardButton.No,
        "YES"             : QtWidgets.QMessageBox.StandardButton.Yes,
        "open"           : QtWidgets.QMessageBox.StandardButton.Open,
        "save"           : QtWidgets.QMessageBox.StandardButton.Save,
        "cancel"         : QtWidgets.QMessageBox.StandardButton.Cancel,
        "close"          : QtWidgets.QMessageBox.StandardButton.Close,
        "discard"        : QtWidgets.QMessageBox.StandardButton.Discard,
        "apply"          : QtWidgets.QMessageBox.StandardButton.Apply,
        "reset"          : QtWidgets.QMessageBox.StandardButton.Reset,
        "restore_default": QtWidgets.QMessageBox.StandardButton.RestoreDefaults,
        "help"           : QtWidgets.QMessageBox.StandardButton.Help,
        "save_all"       : QtWidgets.QMessageBox.StandardButton.SaveAll,
        "yes"            : QtWidgets.QMessageBox.StandardButton.Yes,
        "yes_to_all"     : QtWidgets.QMessageBox.StandardButton.YesToAll,
        "no"             : QtWidgets.QMessageBox.StandardButton.No,
        "no_to_all"      : QtWidgets.QMessageBox.StandardButton.NoToAll,
        "abort"          : QtWidgets.QMessageBox.StandardButton.Abort,
        "retry"          : QtWidgets.QMessageBox.StandardButton.Retry,
        "ignore"         : QtWidgets.QMessageBox.StandardButton.Ignore,
        "no button"      : QtWidgets.QMessageBox.StandardButton.NoButton,
        }


def makeMessageBox(message, buttons=["cancel", "OK"], infotext=""):
  """
  Buttons[0] is set as default
  """
  msg_box = QtWidgets.QMessageBox()
  msg_box.setText(message)
  msg_box.setInformativeText(infotext)
  msg_box.setWindowTitle("dialog")
  # msg_box.setWindowFlags( QtCore.Qt.CustomizeWindowHint |QtCore.Qt.Popup)
  msg_box.setWindowFlags(QtCore.Qt.WindowType.Popup)
  # save = QtWidgets.QMessageBox.Save
  # discard = QtWidgets.QMessageBox.Discard
  # cancel = QtWidgets.QMessageBox.Cancel
  mybuttons = BUTTONS[buttons[0]]
  for buts in buttons:
    mybuttons = mybuttons | BUTTONS[buts]

  msg_box.setStandardButtons(mybuttons)  # discard | save | cancel);
  msg_box.setDefaultButton(BUTTONS[buttons[0]])
  msg_box.show()
  r = msg_box.exec()

  for i in BUTTONS:
    if r == BUTTONS[i]:
      return i

  return None


if __name__ == '__main__':
  a = QtWidgets.QApplication(sys.argv)
  s = makeMessageBox("hello this is a very long message  even longer than one expcts \n hello",
                     infotext="gugus")
  print(s)
  sys.exit()
