# Specify a base image: Use the newest version of Ubuntu
FROM ubuntu:latest as base

# Install Python 3.10.8 and pip
RUN apt-get update && apt-get install -y python3.10 python3-pip jq curl

# Copy the project files into the container
WORKDIR /harmonic


# Minimize the number of layers: Run pip install to install the dependencies
COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
# Run all of the apps we will need for the process
CMD rm -f $INGESTION_PIPE && mkfifo $INGESTION_PIPE && \
        uvicorn api.main:fast_api --port $API_PORT --reload & \
        python3 services/ingest.py
        

# Tag the image with a name and version: Specify the tag name and version
ARG VERSION=1.0.7
LABEL version=$VERSION
LABEL maintainer="Hank Bond<yo@harrisonbond.com>"
LABEL description="A Dockerfile to run the Harmonic Submission"
