#!/bin/bash
docker buildx build -f sidecar.Dockerfile --platform linux/amd64 -t no8ge/sidecar:1.0 . --push
