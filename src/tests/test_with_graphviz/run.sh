#!/bin/bash
# Script to set up and run the PyQt5 + Graphviz application

# Check if graphviz_test.py exists
if [ ! -f "graphviz_test.py" ]; then
    echo "Creating graphviz_test.py..."
    cat > graphviz_test.py << 'EOF'
#!/usr/bin/env python3
"""
PyQt5 application that demonstrates Graphviz integration.
This app allows users to input DOT language code and visualize the resulting graph.
"""
import sys
import os
import tempfile
import subprocess
from PyQt5 import QtWidgets, QtGui, QtCore

class GraphvizDemo(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('PyQt5 + Graphviz Demo')
        self.setGeometry(100, 100, 1000, 800)
        
        # Create central widget and layout
        central_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout(central_widget)
        
        # Create splitter for resizable panes
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left side - DOT code editor
        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        
        # DOT code editor
        label = QtWidgets.QLabel("DOT Graph Code:")
        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setFont(QtGui.QFont("Courier", 10))
        
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
        render_button = QtWidgets.QPushButton("Render Graph")
        render_button.clicked.connect(self.render_graph)
        
        # Add widgets to left layout
        left_layout.addWidget(label)
        left_layout.addWidget(self.text_edit)
        left_layout.addWidget(render_button)
        
        # Right side - Graph visualization
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        
        # Graph display
        graph_label = QtWidgets.QLabel("Graph Visualization:")
        self.graph_view = QtWidgets.QLabel("Click 'Render Graph' to visualize")
        self.graph_view.setAlignment(QtCore.Qt.AlignCenter)
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
            pixmap = QtGui.QPixmap(img_file_path)
            
            # Scale pixmap if it's too large
            if pixmap.width() > self.graph_view.width() or pixmap.height() > self.graph_view.height():
                pixmap = pixmap.scaled(
                    self.graph_view.width(), 
                    self.graph_view.height(),
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                )
                
            self.graph_view.setPixmap(pixmap)
            self.statusBar().showMessage('Graph rendered successfully')
            
            # Clean up temporary files
            os.unlink(dot_file_path)
            os.unlink(img_file_path)
            
        except Exception as e:
            self.statusBar().showMessage(f'Error: {str(e)}')

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = GraphvizDemo()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
EOF
    chmod +x graphviz_test.py
fi

# Determine the OS and set appropriate display variable
if [ "$(uname)" == "Darwin" ]; then
    # macOS with XQuartz
    DISPLAY_ENV="host.docker.internal:0"
    echo "macOS detected - Make sure XQuartz is running and you've executed: xhost + 127.0.0.1"
elif [ "$(uname)" == "Linux" ]; then
    # Linux
    DISPLAY_ENV="$DISPLAY"
    echo "Linux detected - Enabling X11 access for Docker..."
    xhost +local:docker
else
    # Windows/other (assuming using X server like VcXsrv)
    DISPLAY_ENV="host.docker.internal:0"
    echo "Windows detected - Make sure your X server is running with 'Disable access control' checked"
fi

# Check if Docker Compose is installed
if command -v docker-compose &> /dev/null; then
    # Use Docker Compose
    echo "Running with Docker Compose..."
    DISPLAY=$DISPLAY_ENV docker-compose up --build
else
    # Use regular Docker commands
    echo "Building Docker image..."
    docker build -t pyqt-graphviz -f Dockerfile .
    
    echo "Running Docker container with display: $DISPLAY_ENV"
    docker run --rm -it \
        -e DISPLAY=$DISPLAY_ENV \
        -v /tmp/.X11-unix:/tmp/.X11-unix \
        -v "$(pwd)":/app \
        pyqt-graphviz
fi

# Clean up X11 access (Linux only)
if [ "$(uname)" == "Linux" ]; then
    echo "Resetting X11 access..."
    xhost -local:docker
fi
