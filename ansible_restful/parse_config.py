# _*_ coding:utf-8 _*_

from ConfigParser import SafeConfigParser

# 读取配置文件
config = SafeConfigParser()
config.read('config.ini')


# broker_url = config.get("Default", "CELERY_BROKER_URL")
# backend = config.get("Default", "CELERY_RESULT_BACKEND")
# task_timeout = int(config.get("Default", "CELERY_TASK_TIMEOUT"))

playbook_root = config.get("Default", "playbook_root")

flask_tcp_ip = config.get("Default", "FLASK_TCP_IP")
flask_tcp_port = int(config.get("Default", "FLASK_TCP_PORT"))