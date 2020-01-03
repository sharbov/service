#!/usr/bin/env bash
# Use this script to run build related commands in docker environment
cd /mnt/c/work/service
docker build -f Dockerfile.build -t builder --build-arg docker_host=tcp://host.docker.internal:2375 . && \
docker run -it --rm --net="host" --name build \
-e HOST_PWD=/c/work/service \
-e SERVICE_HOST=host.docker.internal \
-v /var/run/docker.sock:/var/run/docker.sock \
-v /c/work/service:/service builder $@
