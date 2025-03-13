import os

from PyQt6 import QtCore
from PyQt6 import QtGui

from resources.pop_up_message_box import makeMessageBox

# ===========================================  icons ==============================
ICONS = {}
ICONS["+"] = "plus-icon.png"
ICONS["-"] = "minus-icon.png"
ICONS["->"] = "right-icon.png"
ICONS["<-"] = "left-icon.png"
ICONS["^"] = "up-icon.png"
ICONS["v"] = "down-icon.png"
ICONS["load"] = "load_button_hap.svg"
ICONS["exit"] = "exit_button_hap.svg"
ICONS["info"] = "info_button_hap.svg"
ICONS["accept"] = "accept_button_hap.svg"
ICONS["reject"] = "reject_button_hap.svg"
ICONS["back"] = "back_button_hap.svg"
ICONS["new"] = "new_button_hap.svg"
ICONS["dot_graph"] = "dot_graph_button_hap.svg"
ICONS["save"] = "save_button_hap.svg"
ICONS["delete"] = "delete_button_hap.svg"
ICONS["reset"] = "reset_button_hap.svg"
ICONS["screen_shot"] = "screen_shot_button_hap.svg"
ICONS["save_as"] = "save_as_button_hap.svg"
ICONS["plus"] = "plus_button_hap.svg"
ICONS["minus"] = "minus_button_hap.svg"
ICONS["max_view"] = "plus_button_hap.svg"
ICONS["min_view"] = "minus_button_hap.svg"
ICONS["normal_view"] = "normal_view_button_hap.svg"
ICONS["update"] = "update_button_hap.svg"
ICONS["next"] = "next_button_hap.svg"
ICONS["expand"] ="expand_tree_button_hap.svg"
ICONS["collaps"] = "collaps_tree_button_hap.svg"
ICONS["bricks"] = "bricks_button_hap.svg"
ICONS["build_tree"] = "build_tree_hap.svg"
ICONS["instantiate_tree"] = "instantiate_tree_hap.svg"
ICONS["LED_green"] = "LED_green.svg"
ICONS["LED_red"] = "LED_red.svg"


class roundButton:


  def __init__(self, button, what, tooltip=None, mysize=None):
    defaultsize = 52
    if mysize:
      size=mysize
    else:
      size = defaultsize

    BUTTON_ICON_SIZE = QtCore.QSize(size, size)
    round = 'border-radius: %spx; ' % (size / 2)
    BUTTON_ICON_STYLE_ROUND = 'background-color: white; '
    BUTTON_ICON_STYLE_ROUND += 'border-style: outset; '
    BUTTON_ICON_STYLE_ROUND += 'border-width: 2px; '
    BUTTON_ICON_STYLE_ROUND += round
    BUTTON_ICON_STYLE_ROUND += 'border-color: white;    '
    BUTTON_ICON_STYLE_ROUND += 'font: bold 14px;   '
    BUTTON_ICON_STYLE_ROUND += 'padding: 6px;'

    button.setText("")
    button.setFixedSize(size,size)
    icon = self.getIcon(what)
    button.setIcon(icon) #getIcon(what))
    button.setStyleSheet(BUTTON_ICON_STYLE_ROUND)
    button.setIconSize(BUTTON_ICON_SIZE)
    button.setToolTip(tooltip)
    self.button = button


  def getIcon(self,what):
    try:
      what in ICONS.keys()
    except:
      makeMessageBox("assertation error %s is not in the icon dictionary %s\n I exit" % what, ["OK"])
      os.exit()

    f_name = os.path.join(os.getcwd(), 'resources', "icons", ICONS[what])
    # print("debugging .....", f_name)
    if os.path.exists(f_name):
      # pm = QtGui.QPixmap(f_name)
      icon = QtGui.QIcon(f_name)

      return icon #QtGui.QIcon(pm)
    else:
      makeMessageBox("no such file : %s"%f_name, ["OK"])
      pass

  def changeIcon(self, what):
    icon = self.getIcon(what)
    self.button.setIcon(icon)
