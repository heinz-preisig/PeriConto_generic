FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-pyqt6 \
    graphviz \
    libgl1 \
    libegl1 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxcb-shape0 \
    libxcb-shm0 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libsm6 \
    libice6 \
    x11-utils \
    dbus \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for running the application
RUN useradd -m appuser

# Create app directory structure
RUN mkdir -p /app/src
WORKDIR /app

# Copy the application
COPY src/ /app/src/
RUN chmod +x /app/src/BricksSchemata.py /app/src/TreeSchemata.py

# Set ownership to the non-root user
RUN chown -R appuser:appuser /app

# Install Python dependencies using apt for better compatibility with system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pyqt6 \
    python3-pyqt6.qtwebengine \
    python3-pyqt6.qtwebchannel \
    python3-pyqt6.qtsvg \
    python3-graphviz \
    python3-rdflib \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Switch to the non-root user
USER appuser

# Set environment variables for X11 forwarding
ENV DISPLAY=:0
ENV QT_X11_NO_MITSHM=1
ENV QT_QPA_PLATFORM=xcb

# Run the application
WORKDIR /app/src
# Default to running BricksSchemata.py, but can be overridden in the run command
# CMD ["python3", "TreeSchemata.py"]
