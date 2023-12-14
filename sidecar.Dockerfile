FROM ubuntu:20.04

ENV MINIO_ACCESS_KEY=admin
ENV MINIO_SECRET_KEY=changeme
ENV MINIO_HOST=files-minio:9000
ENV REPORT=/test

WORKDIR /sidecar

EXPOSE 7001

RUN apt-get update
RUN apt-get install -y git curl wget sudo vim
RUN wget https://dl.min.io/client/mc/release/linux-amd64/mc
RUN chmod +x mc
RUN sudo mv mc /usr/local/bin/mc

CMD ["mc","mirror","--watch","--debug","--overwrite","/data","atop/result/$REPORT"]
