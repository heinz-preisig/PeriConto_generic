#!/usr/bin/env python3
"""
PyQt6 application that demonstrates Graphviz integration.
This app allows users to input DOT language code and visualize the resulting graph.
"""
import sys
import os
import tempfile
import subprocess
# Import only the specific modules needed to avoid OpenGL dependencies
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                           QSplitter, QLabel, QTextEdit, QPushButton, QApplication)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt

class GraphvizDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('PyQt6 + Graphviz Demo')
        self.setGeometry(100, 100, 1000, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panes
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left side - DOT code editor
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # DOT code editor
        label = QLabel("DOT Graph Code:")
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Courier", 10))
        
        # Default graph example
        default_graph = """digraph G {
    node [shape=box];
    A -> B -> C;
    B -> D;
    D -> A;
    A [label="Start", color=green];
    D [label="End", color=red];
}"""
        self.text_edit.setText(default_graph)
        
        # Render button
        render_button = QPushButton("Render Graph")
        render_button.clicked.connect(self.render_graph)
        
        # Add widgets to left layout
        left_layout.addWidget(label)
        left_layout.addWidget(self.text_edit)
        left_layout.addWidget(render_button)
        
        # Right side - Graph visualization
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Graph display
        graph_label = QLabel("Graph Visualization:")
        self.graph_view = QLabel("Click 'Render Graph' to visualize")
        self.graph_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.graph_view.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        
        # Add widgets to right layout
        right_layout.addWidget(graph_label)
        right_layout.addWidget(self.graph_view)
        
        # Add left and right widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 600])
        
        # Set the central widget
        self.setCentralWidget(central_widget)
        
        # Status bar for messages
        self.statusBar().showMessage('Ready')
        
        # Render the default graph when starting
        self.render_graph()
        
    def render_graph(self):
        """Render the DOT code as a graph using Graphviz and display it"""
        try:
            dot_code = self.text_edit.toPlainText()
            
            # Create temporary files for the DOT source and the rendered image
            with tempfile.NamedTemporaryFile(suffix='.dot', delete=False) as dot_file:
                dot_file_path = dot_file.name
                dot_file.write(dot_code.encode('utf-8'))
            
            img_file_path = dot_file_path + '.png'
            
            # Use Graphviz's dot command to render the graph
            result = subprocess.run(
                ['dot', '-Tpng', dot_file_path, '-o', img_file_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.statusBar().showMessage(f'Error: {result.stderr}')
                return
                
            # Load and display the rendered image
            pixmap = QPixmap(img_file_path)
            
            # Scale pixmap if it's too large
            view_size = self.graph_view.size()
            if pixmap.width() > view_size.width() or pixmap.height() > view_size.height():
                pixmap = pixmap.scaled(
                    view_size.width(), 
                    view_size.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                
            self.graph_view.setPixmap(pixmap)
            self.statusBar().showMessage('Graph rendered successfully')
            
            # Clean up temporary files
            os.unlink(dot_file_path)
            os.unlink(img_file_path)
            
        except Exception as e:
            self.statusBar().showMessage(f'Error: {str(e)}')

def main():
    app = QApplication(sys.argv)
    window = GraphvizDemo()
    window.show()
    sys.exit(app.exec())  # Note: exec() not exec_() in PyQt6

if __name__ == '__main__':
    main()
