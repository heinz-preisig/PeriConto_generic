from PyQt6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QPushButton


class TreeWidgetExample(QWidget):
  def __init__(self):
    super().__init__()

    self.tree = QTreeWidget()
    self.tree.setColumnCount(1)
    self.tree.setHeaderLabels(["Items"])

    # Adding sample items
    for i in range(3):
      parent = QTreeWidgetItem(self.tree, [f"Parent {i}"])
      if i == 1:
        self.toplevelitem = parent
      for j in range(2):
        child = QTreeWidgetItem(parent, [f"Child {i}.{j}"])

      parent.setExpanded(i % 2 == 0)  # Expand alternate parents

    # Buttons to store and restore expanded state
    self.save_button = QPushButton("Save Expanded State")
    self.save_button.clicked.connect(self.save_expanded_state)

    self.restore_button = QPushButton("Restore Expanded State")
    self.restore_button.clicked.connect(self.restore_expanded_state)

    # Layout setup
    layout = QVBoxLayout(self)
    layout.addWidget(self.tree)
    layout.addWidget(self.save_button)
    layout.addWidget(self.restore_button)

    self.expanded_state = {}  # Dictionary to store expanded states

  def save_expanded_state(self):
    """Stores the expanded state of all items in the tree."""
    self.expanded_state = {}
    self._iterate_tree(self.tree.invisibleRootItem(), save=True)
    # self._iterate_tree(self.toplevelitem, save=True)

  def restore_expanded_state(self):
    """Restores the expanded state of all items in the tree."""
    self._iterate_tree(self.tree.invisibleRootItem(), save=False)
    # self._iterate_tree(self.toplevelitem, save=False)

  def _iterate_tree(self, item, save=True):
    """Helper function to iterate through tree items recursively."""
    for i in range(item.childCount()):
      child = item.child(i)
      key = child.text(0)  # Using item text as a unique key

      if save:
        self.expanded_state[key] = child.isExpanded()
      else:
        if key in self.expanded_state:
          child.setExpanded(self.expanded_state[key])

      self._iterate_tree(child, save)


if __name__ == "__main__":
  app = QApplication([])
  window = TreeWidgetExample()
  window.show()
  app.exec()
