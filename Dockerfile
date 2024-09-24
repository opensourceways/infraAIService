# 使用 openEuler 22.03 基础镜像
FROM openeuler/openeuler:22.03

# 设置工作目录为 /app
WORKDIR /app

# 更新系统并安装必要的软件包
RUN yum update -y && \
    yum install -y \
    python3 \
    python3-pip \
    python3-devel \
    gcc \
    make \
    && yum clean all

# 创建符号链接，仅为 python 创建
RUN ln -s /usr/bin/python3 /usr/bin/python

# 复制 requirements.txt 到容器中
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制当前目录下的所有文件到容器中
COPY . .

# 按照模块安装
RUN pip install .

# 暴露容器的8000端口
EXPOSE 8000

# 启动FastAPI应用
CMD ["python", "infra_ai_service/server.py"]