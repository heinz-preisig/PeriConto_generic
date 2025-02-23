import os
import os
import sys

from graphviz import Digraph

from resources.resources_icons import roundButton
import TreeAutomaton as Tree
import BricksAutomaton as Brick

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

root = os.path.abspath(os.path.join("."))
sys.path.extend([root, os.path.join(root, "resources")])

from PyQt6 import QtGui
from PyQt6.QtWidgets import *

from VisualiseAutomata import Ui_MainWindow




class AutomataGraph(QMainWindow):
  def __init__(self):
    QMainWindow.__init__(self)
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    roundButton(self.ui.pushVisualise, "dot_graph", tooltip="visualise ontology")
    roundButton(self.ui.pushSave, "save", tooltip="save ontology")
    roundButton(self.ui.pushExit, "exit", tooltip="exit")
    roundButton(self.ui.pushMinimise, "min_view", tooltip="minimise", mysize=35)
    roundButton(self.ui.pushMaximise, "max_view", tooltip="maximise", mysize=35)
    roundButton(self.ui.pushNormal, "normal_view", tooltip="normal", mysize=35)
    # roundButton(self.ui.pushExit, "reject", tooltip="exit", mysize=35)

  def on_comboBox_textActivated(self, text):
    if text == "brick-automaton":
      automaton = Brick.UI_state
      pass
    elif text == "tree-automaton":
      automaton = Tree.UI_state
      pass
    pass


  def on_pushVisualise_pressed(self):
    pass

  def on_pushMinimise_pressed(self):
    self.showMinimized()

  def on_pushMaximise_pressed(self):
    self.showMaximized()

  def on_pushNormal_pressed(self):
    self.showNormal()

  def on_pushExit_pressed(self):
    self.close()

if __name__ == "__main__":
  import sys

  app = QApplication(sys.argv)

  icon_f = "task_ontology_foundation.svg"
  icon = os.path.join(os.path.abspath("resources/icons"), icon_f)
  app.setWindowIcon(QtGui.QIcon(icon))

  MainWindow = AutomataGraph()
  MainWindow.show()
  sys.exit(app.exec())