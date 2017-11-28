# _*_ coding:utf-8 _*_
from ConfigParser import SafeConfigParser

from celery import Celery
from flask import Flask
from flask_restful import Api
from flask_restful_swagger import swagger

from ansible_restful import log

# 读取配置文件
config = SafeConfigParser()
config.read('config.ini')

app = Flask(__name__)


log = log.Log().getlog()

# 读取celery配置参数
app.config['broker_url'] = config.get("Default", "CELERY_BROKER_URL")
app.config['result_backend'] = config.get("Default", "CELERY_RESULT_BACKEND")
task_timeout = int(config.get("Default", "CELERY_TASK_TIMEOUT"))

api = swagger.docs(Api(app), apiVersion='0.1')

celery = Celery(app.name, broker=app.config['broker_url'], backend=app.config['result_backend'])
celery.conf.update(app.config)

import deploy
import runner
import playbook


#from deploy import Deploy
#from playbook import Playbook