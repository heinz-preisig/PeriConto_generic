#!/bin/bash
# Script to run the PyQt5 application with proper X11 forwarding

# Set image name and paths
IMAGE_NAME="periconto"
LOCAL_ONTOLOGY_REPOSITORY="/home/heinz/1_Gits/OntoBuild/PeriConto-Ontologies"
DOKER_ONTOLOGY_REPOSITORY="/PeriConto-Ontologies"

# Default command (BricksSchemata.py)
CMD=("python3" "/app/src/TreeSchemata.py")

# Check for different run modes
case "$1" in
    "bash")
        # Start an interactive bash shell
        CMD=("/bin/bash")
        ;;
    "bricks")
        # Run BricksSchemata.py
        CMD=("python3" "/app/src/BricksSchemata.py")
        ;;
    *)
        # Any other arguments will be passed to TreeSchemata.py
        if [ -n "$1" ]; then
            CMD=("python3" "/app/src/TreeSchemata.py" "$@")
        fi
        ;;
esac

# Enable X11 access for Docker (Linux only)
if [ "$(uname)" == "Linux" ]; then
  echo "Enabling X11 access for Docker..."
  xhost +local:docker
fi

# Determine correct DISPLAY setting based on OS
if [ "$(uname)" == "Darwin" ]; then
  # macOS with XQuartz
  DISPLAY_ENV="host.docker.internal:0"
  IP=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
  echo "Make sure XQuartz is running and you've run: xhost + $IP"
elif [ "$(uname)" == "Linux" ]; then
  # Linux
  DISPLAY_ENV="$DISPLAY"
else
  # Windows/other (assuming using X server like VcXsrv)
  DISPLAY_ENV="host.docker.internal:0"
  echo "Make sure your X server is running with 'Disable access control' checked"
fi

# Run the docker container
echo "Running container with display: $DISPLAY_ENV"
echo "Command: ${CMD[*]}"
docker run --rm -it \
  -e DISPLAY=$DISPLAY_ENV \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v "$LOCAL_ONTOLOGY_REPOSITORY:$DOKER_ONTOLOGY_REPOSITORY" \
  -u 1000:1000 \
  --network="host" \
  "$IMAGE_NAME" "${CMD[@]}"

# Cleanup X11 access (Linux only)
if [ "$(uname)" == "Linux" ]; then
  echo "Resetting X11 access..."
  xhost -local:docker
fi
