# 注意事项

## 前置条件
- 需要安装数据库postgresql及其pgvector插件
- 需要新增.env文件，将数据库配置，外部服务配置等添加

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
- 构建并本地运行
```shell
# 构建容器
docker build -t infra_ai_service .
# 配置本地.env
DB_HOST=host.docker.internal
MODEL_NAME=multi-qa-MiniLM-L6-cos-v1
HOST=0.0.0.0
# 运行ai_service服务（需要替代实际路径：.env文件的绝对路径）
docker run --rm -p 8001:8000 --name infra_ai_service_imp -v [.env文件的绝对路径]:/app/.env infra_ai_service
# 查看日志
docker logs -name infra_ai_service_imp
```
- 本地验证
```shell
# 测试启动（需要替代实际路径：.env文件的绝对路径）
docker run --rm --entrypoint sleep -p 8001:8000 --name infra_ai_service_imp -v [.env文件的绝对路径]:/app/.env infra_ai_service 999999999
# 测试查看
docker exec -it infra_ai_service_imp bash
# 启动
python infra_ai_service/server.py
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
