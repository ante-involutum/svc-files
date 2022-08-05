FROM python:3.9.12-slim

ENV URL=192.168.100.10:30320
ENV USER=admin
ENV PASSWORD=changeme
ENV BUCKET_NAME=jmx
ENV PREFIX=hpc

WORKDIR /boxter
COPY scripts/init_containers.py /boxter/

RUN pip install minio

CMD ["python","init_containers.py"]