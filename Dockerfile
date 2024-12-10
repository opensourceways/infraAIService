# 使用 openEuler 22.03 基础镜像
FROM openeuler/openeuler:22.03

RUN groupadd -g 1000 infra_ai_service && \
    useradd -u 1000 -g infra_ai_service -d /home/infra_ai_service -m -s /bin/bash infra_ai_service

# 设置工作目录为 /home/infra_ai_service
WORKDIR /home/infra_ai_service

# 更新系统并安装必要的软件包
RUN yum update -y && \
    yum install -y \
    python3 \
    python3-pip \
    python3-devel \
    gcc \
    make \
    rpmdevtools* \
    wget \
    && yum clean all \
    && dnf install -y debootstrap \
    && mkdir -p /mnt/debian \
    && debootstrap buster /mnt/debian https://mirrors.huaweicloud.com/debian/ \
    && echo "chroot /mnt/debian /bin/bash -c 'apt update && apt install -y devscripts'" > /setup_chroot.sh \
    && chmod +x /setup_chroot.sh \
    && /setup_chroot.sh

RUN wget https://github.com/BurntSushi/ripgrep/releases/download/14.1.1/ripgrep-14.1.1-x86_64-unknown-linux-musl.tar.gz && \
    tar -zxvf ripgrep-14.1.1-x86_64-unknown-linux-musl.tar.gz && \
    mv ripgrep*/rg /usr/local/bin/ && \
    rg --version

# 创建符号链接，仅为 python 创建
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN pip install pgcli

# 复制 requirements.txt 到容器中
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt
# 复制当前目录下的所有文件到容器中

COPY --chown=infra_ai_service . .

# 按照模块安装
RUN pip install .

# 暴露容器的8000端口
EXPOSE 8000

USER infra_ai_service

RUN echo '#!/bin/sh' > /home/infra_ai_service/entrypoint.sh && \
    echo 'cp /app/.env /home/infra_ai_service/.env' >> /home/infra_ai_service/entrypoint.sh && \
    echo 'python infra_ai_service/server.py' >> /home/infra_ai_service/entrypoint.sh && \
    chmod +x /home/infra_ai_service/entrypoint.sh

# 启动FastAPI应用
CMD ["/home/infra_ai_service/entrypoint.sh"]