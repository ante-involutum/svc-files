FROM alpine

ENV MINIO_ACCESS_KEY=admin
ENV MINIO_SECRET_KEY=changeme
ENV MINIO_HOST=127.0.0.1:9000
ENV REPORT=/test

WORKDIR /sidecar

EXPOSE 7001

RUN wget https://dl.min.io/client/mc/release/linux-amd64/mc
RUN chmod +x mc
RUN mv mc /usr/local/bin/mc

CMD ["/bin/sh", "-c", "mc alias set atop http://$MINIO_HOST $MINIO_ACCESS_KEY $MINIO_SECRET_KEY; mc mirror --watch --debug --overwrite /data atop/result/$REPORT"]
