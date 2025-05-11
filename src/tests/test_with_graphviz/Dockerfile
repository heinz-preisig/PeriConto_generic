FROM python:3.11-slim

# Install system dependencies including X11, Qt dependencies and Graphviz
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libegl1 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libdbus-1-3 \
    xvfb \
    graphviz \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY ./requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY ./graphviz_demo.py /app/graphviz_demo.py

# Set environment variable for display
ENV DISPLAY=:99

# Set entry command using JSON array format
# Use a bash script to start Xvfb and then run the application
CMD ["bash", "-c", "Xvfb :99 -screen 0 1024x768x16 & python /app/graphviz_demo.py"]
