# Stage 1: Build environment
FROM ubuntu:22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

# Install only the packages needed for building
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install PyQt5 in the virtual environment
RUN pip3 install --no-cache-dir PyQt5

# Stage 2: Runtime environment
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Set environment variables for virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Install only runtime dependencies including Graphviz
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libxext6 \
    libx11-6 \
    libxkbcommon-x11-0 \
    libsm6 \
    libice6 \
    libxcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-shm0 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libx11-xcb1 \
    libglib2.0-0 \
    libdbus-1-3 \
    libxkbcommon0 \
    ibus \
    python3-minimal \
    graphviz \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set Qt plugin path and other environment variables
ENV QT_QPA_PLATFORM_PLUGIN_PATH=/opt/venv/lib/python3.10/site-packages/PyQt5/Qt5/plugins
ENV QT_XCB_GL_INTEGRATION=none
ENV QT_IM_MODULE=ibus
ENV XMODIFIERS=@im=ibus
ENV GTK_IM_MODULE=ibus

# Create workspace
WORKDIR /app

# Copy your test application
COPY graphviz_test.py /app/

# Set display for X11 forwarding
ENV DISPLAY=:0

# Command to run the test application
CMD ["python3", "graphviz_test.py"]
