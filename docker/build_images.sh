#!/bin/bash

PROJ_DIR="$(dirname $)/../"

#docker build -t windj007/docato-base -f $PROJ_DIR/docker/Dockerfile.base $PROJ_DIR && \
docker build -t windj007/docato-wui -f $PROJ_DIR/docker/Dockerfile.wui $PROJ_DIR && \
docker build -t windj007/docato-preproc -f $PROJ_DIR/docker/Dockerfile.preproc $PROJ_DIR
