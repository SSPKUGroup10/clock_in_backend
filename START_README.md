# 启动项目的流程

重新部署以后
1. python manage.py db upgrade
2. gunicorn -c gunicorn.py manage:app