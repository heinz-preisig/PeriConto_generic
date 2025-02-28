import sys

from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QGridLayout
from PyQt6.QtWidgets import QDialog
from PyQt6.QtWidgets import QDialogButtonBox
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QRadioButton
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QSpacerItem

from resources.resources_icons import roundButton


class RadioButtonDialog(QDialog):
  def __init__(self, options, title=None, parent=None):
    super().__init__(parent)

    self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
    layout = QVBoxLayout(self)

    if title:
      label2 = QLabel("%s"%title)
      layout.addWidget(label2)
      layout.addSpacing(20)

    self.radio_buttons = []
    for option in options:
      radio_button = QRadioButton(option)
      self.radio_buttons.append(radio_button)
      layout.addWidget(radio_button)

    box = QHBoxLayout()
    button_accept = QPushButton("accept")
    button_reject = QPushButton("reject")
    box.addWidget(button_accept)
    box.addWidget(button_reject)

    layout.addSpacing(20)
    layout.addLayout(box)

    roundButton(button_accept, "accept", tooltip="accept")
    roundButton(button_reject, "reject", tooltip="reject")

    button_accept.clicked.connect(self.accept)
    button_reject.clicked.connect(self.reject)


  def get_selected_option(self):
    for radio_button in self.radio_buttons:
      if radio_button.isChecked():
        return radio_button.text()
    return None


# Example usage
if __name__ == "__main__":
  app = QApplication(sys.argv)
  options = ["Option 1", "Option 2", "Option 3", "Option 4"]
  dialog = RadioButtonDialog(options)#, title="gugus")
  if dialog.exec():
    print("Selected option:", dialog.get_selected_option())
  else:
    print("No option selected.")
