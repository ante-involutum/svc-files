# files

## install minio

```shell
helm install data-kakax-minio --set auth.rootUser=minio-admin --set auth.rootPassword=minio-secret-password bitnami/minio
```
