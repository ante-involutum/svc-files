APPVERSION := $(shell helm show chart chart | awk '/^appVersion:/ {print $$2}')
CHART_NAME := $(shell helm show chart chart | awk '/^name:/ {print $$2}')

.DEFAULT_GOAL := run

clean:
	rm -f $(CHART_NAME)*

run:
	uvicorn src.main:app --reload --port=8004 --host=0.0.0.0

test:
	pipenv run pytest

coverage:
	@if [ ! -f coverage.out ]; then echo "Coverage profile file not found"; exit 1; fi
	go tool cover -html=coverage.out

install:
	pipenv install

docker:
	docker buildx build -f Dockerfile --platform linux/amd64 -t no8ge/$(CHART_NAME):$(APPVERSION) . --push

chart:
	helm package chart 
	helm push $(CHART_NAME)-*.tgz  oci://registry-1.docker.io/no8ge

.PHONY: build clean run fmt test coverage deps docker chart