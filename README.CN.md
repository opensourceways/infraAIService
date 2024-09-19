# 注意事项

## 前置条件
- 需要安装qdrant本地服务
```shell
# docker环境准备
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
# 安装
docker run -p 6333:6333 -d --name qdrant qdrant/qdrant
# 测试
curl http://localhost:6333
```

## 本地启动
```shell
# 安装依赖
cd infra_ai_service/
pip install -r requirements.txt
# 测试
pytest .
# 启动
python infra_ai_service/server.py
```

# 容器化部署
```shell
# 构建容器
docker build -t ai_service .
# 运行ai_service服务
docker run -p 8001:8000 -d --name ai_service_imp ai_service

```

## 访问spec-repair API

服务启动后可使用如下命令访问服务
```shell
curl -X POST http://localhost:8000/api/v1/spec-repair/ -F err_spec_file=@/path/repair.spec -F err_log_file=@/path/error.log
```
响应格式:
```python
{  
    'suggestions': 'suggestions(str)',  
    'repair_status': 'is_repaired(bool)',  
    'repair_spec': 'repaired_spec_lines(str)',  
    'log': 'log_content(str)'  
}
```

## 本地访问
- 浏览器打开 http://localhost:8000/ 显示 {"Hello":"World"}
