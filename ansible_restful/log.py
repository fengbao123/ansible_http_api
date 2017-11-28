# _*_ coding:utf-8 _*_

import logging, time,os
import logging.handlers

rq = time.strftime('%Y%m%d', time.localtime(time.time()))
class Log(object):
    '''指定保存日志的文件路径，日志级别，以及调用文件将日志存入到指定的文件中 '''
    def __init__(self,):


        # 创建logger
        self.logger = logging.getLogger()

        #控制日志文件中记录级别
        self.logger.setLevel(logging.INFO)

        #控制输出到控制台日志格式、级别
        self.ch = logging.StreamHandler()
        #self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s[line:%(lineno)d] - %(message)s')
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s[line:%(lineno)d] - %(message)s')
        self.ch.setFormatter(self.formatter)

        #控制输出写入到日志文件
        # 定义日志存放路径
        self.path = os.path.dirname(os.path.realpath(__file__)) + '/../'
        self.log_name = self.path + rq + '.log'

        #日志保留10天,一天保存一个文件
        self.fh = logging.handlers.TimedRotatingFileHandler(self.log_name, 'D', 1, 10)


        self.fh.setFormatter(self.formatter)


        self.logger.addHandler(self.fh)
        self.logger.addHandler(self.ch)

    def getlog(self):
        return self.logger