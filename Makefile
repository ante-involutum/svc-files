APPVERSION := $(shell helm show chart chart | awk '/^appVersion:/ {print $$2}')
CHART_NAME := $(shell helm show chart chart | awk '/^name:/ {print $$2}')

.DEFAULT_GOAL := build

clean:
	rm -f $(CHART_NAME)*

buildx:
	docker buildx build -f Dockerfile --platform linux/amd64 -t no8ge/$(CHART_NAME):$(APPVERSION) . --push

build:
	docker buildx build -f Dockerfile --platform linux/amd64 -t dockerhub.qingcloud.com/qingtest/$(CHART_NAME):$(APPVERSION) . --push

package:
	helm package chart 
	helm push $(CHART_NAME)-*.tgz  oci://registry-1.docker.io/no8ge
	rm -f $(CHART_NAME)-*.tgz

.PHONY: build clean package