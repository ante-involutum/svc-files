# files

```shell
k3d cluster create two-node-cluster --agents 2

helm upgrade --install apisix apisix/apisix --version 1.3.1  --create-namespace --namespace apisix --set gateway.http.nodePort=31690 --set dashboard.enabled=true --set ingress-controller.enabled=true --set ingress-controller.config.apisix.serviceNamespace=apisix

curl http://127.0.0.1:9180/apisix/admin/consumers \
-H 'X-API-KEY: edd1c9f034335f136f87ad84b625c8f1' -X PUT -d '
{
    "username": "admin",
    "plugins": {
        "key-auth": {
            "key": "admin",
            "header": "Authorization"

        }
    }
}'
```
