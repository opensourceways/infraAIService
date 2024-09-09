# 注意事项


## 前置条件
- 需要安装本地psql数据库
```shell
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl status postgresql
sudo -u postgres psql
ALTER USER postgres PASSWORD 'postgres';
# 建立数据库（db）
CREATE DATABASE db;
```

## 本地启动
```shell
cd infra_ai_service/
pip install -r requirements.txt
# 迁移数据
alembic revision --autogenerate -m "Example model"
alembic upgrade head
pytest .
# 启动
python infra_ai_service/server.py
```


## 本地访问
- 浏览器打开 http://localhost:8000/ 显示 {"Hello":"World"}
