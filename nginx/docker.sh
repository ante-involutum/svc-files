#!/bin/bash
docker buildx build -f dockerfile --platform linux/amd64 -t no8ge/files-nginx:1.0 . --push
