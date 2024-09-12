# 注意事项

## 前置条件
- 需要安装数据库postgresql及其pgvector插件
- 需要新增.env文件，将数据库配置，外部服务配置等添加，并将MODEL_NAME设置为multi-qa-MiniLM-L6-cos-v1

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
docker build -t infra_ai_service .
# 运行ai_service服务
docker run -p 8001:8000 -d --name infra_ai_service_imp ai_service

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

## 访问feature-insert API

服务启动后可使用如下命令访问服务
```shell
curl -X POST http://localhost:8000/api/v1/feature-insert/ \
     -H "Content-Type: application/json" \
     -d '{"src_rpm_url":"https://repo.openeuler.org/ansible-lint-4.2.0.src.rpm","os_version":"openEuler-24.03"}'
```
响应格式:
```python
{  
    'status': 'success'
}
```

## 本地访问
- 浏览器打开 http://localhost:8000/ 显示 {"Hello":"World"}
