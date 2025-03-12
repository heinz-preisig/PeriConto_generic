FROM ubuntu:22.04


MAINTAINER heinz <heinz.preisig@chemeng.ntnu.no>

ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3, PyQt6
RUN apt-get update && apt-get install -qq -y \
	python3-pyqt6 \
	python3-babel \
	python3-graphviz \
	python3-pyparsing\
	rdflib\
   && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
#RUN pip install -r requirements.txt

#WORKDIR /src
#COPY ./src

WORKDIR /src

#CMD ["bash", "task.sh"]