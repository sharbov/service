#!/usr/bin/env bash
# Use this script to run build related commands in docker environment
docker build -f Dockerfile.build -t builder . && \
docker run -it --rm --net="host" --name build \
-e HOST_PWD=$PWD \
-v /var/run/docker.sock:/var/run/docker.sock \
-v $PWD:/service builder $@