# 用作启动容器用的脚本
import multiprocessing

bind = "0.0.0.0:5050"

workers = multiprocessing.cpu_count() * 2 + 1

# 运行脚本的方式
# gunicorn -c gunicorn.py manage:app