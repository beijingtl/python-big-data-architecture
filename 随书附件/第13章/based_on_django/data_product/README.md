

# 命令

```bash
docker container run -dit -p 8000:8000 -w /home/based_on_django --name based_on_django python:3.8.5

# 安装配置
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install django==3.2.3

# 1. 创建项目
django-admin startproject data_product

# 2. 创建应用
python manage.py startapp example

# 3. 启动服务
python manage.py runserver

# 4. 请求服务 
curl -X GET http://localhost:8000/example/api/v1/counter/
```