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
sudo docker run -p 6333:6333 -d --name qdrant qdrant/qdrant
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


## 本地访问
- 浏览器打开 http://localhost:8000/ 显示 {"Hello":"World"}
