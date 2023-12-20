# files

文件服务，管理 [`plugin`](https://github.com/no8ge/plugins "plugin") 生成的测试报告(对象)

## 要求

- Kubernetes

## 快速开始

### 构建 plugin

> 参考 [`plugin`](https://github.com/no8ge/plugins "plugin")

### 部署环境

> 参考 [`快速开始`](https://github.com/no8ge/atop?tab=readme-ov-file#%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B)

### 创建测试

> 参考 [`快速开始`](https://github.com/no8ge/tink?tab=readme-ov-file#%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B)

#### 查看报告

```shell
# request
curl -X GET -H "Content-Type: application/json" -H "Authorization: admin" http://192.168.228.5:31690/files/v1.0/report -d '
{
  "type":"pytest",
  "uid":"278a0e0f-08a4-47b1-a4a8-582b21fcf694",
  "path":"/demo/report"
}'

# response
{
    "url":"http://192.168.228.5:31690/files/share/result/278a0e0f-08a4-47b1-a4a8-582b21fcf694/index.html"
}

# 浏览器打开 
open http://192.168.228.5:31690/files/share/result/278a0e0f-08a4-47b1-a4a8-582b21fcf694/index.html  
```
