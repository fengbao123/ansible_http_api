# -*- coding: utf-8 -*-

from ansible.plugins.callback import CallbackBase
import time


#get result output
class ResultsCollector(CallbackBase):

    MSG_FORMAT = "%(now)s - %(task)s - %(category)s \n\n"
    TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, *args, **kwargs):
        super(ResultsCollector, self).__init__(*args, **kwargs)

        # 详细信息
        self.detail_info = {}

        # 输出信息
        self.output = {}

        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}
        self.host_result = {}

    def v2_runner_on_ok(self, result,  *args, **kwargs):
        name = result._host.get_name()
        task = result._task.get_name()
        if task == "setup" or task == "Gathering Facts":
            pass
        else:
            self.detail_info.setdefault(name, {})[task] = result._result

            self.host_ok.setdefault(name, {})[task] = result._result
            #self.host_result[name] = result._result

            now = time.strftime(self.TIME_FORMAT, time.localtime())
            self.output[name]= self.output.get(name,"") + self.MSG_FORMAT % dict(now=now,task=task,category='SUCCESS')

    def v2_runner_on_unreachable(self, result, ignore_errors=False):
        name = result._host.get_name()
        task = result._task.get_name()
        self.detail_info.setdefault(name, {})[task] = result._result

        #self.host_unreachable[name] = result._result
        self.host_unreachable.setdefault(name, {})[task] = result._result

        #self.host_result[name] = result._result
        now = time.strftime(self.TIME_FORMAT, time.localtime())
        self.output[name] = self.output.get(name, "") + self.MSG_FORMAT % dict(now=now, task=task, category='UNREACHABLE')

    def v2_runner_on_failed(self, result,   *args, **kwargs):
        name = result._host.get_name()
        task = result._task.get_name()

        # 过滤掉忽略掉的错误信息
        if result._result['_ansible_parsed'] == True:
            self.detail_info.setdefault(name, {})[task] = result._result

            #self.host_result[name] = result._result
            now = time.strftime(self.TIME_FORMAT, time.localtime())
            self.output[name] = self.output.get(name, "") + self.MSG_FORMAT % dict(now=now, task=task, category='INGORE')
            self.host_ok.setdefault(name, {})[task] = result._result

        else:
            # self.host_failed[name] = result._result
            now = time.strftime(self.TIME_FORMAT, time.localtime())
            self.output[name] = self.output.get(name, "") + self.MSG_FORMAT % dict(now=now, task=task, category='FAILED')
            self.host_failed.setdefault(name, {})[task] = result._result



class AnsibleReturn(object):
    def __init__(self,callback):
        self._host_ok = callback.host_ok
        self._host_failed = callback.host_failed
        self._host_unreachable = callback.host_unreachable

        self._output = callback.output
        self._detail_info = callback.detail_info


        self.result = {}

        self.result['return_code'] = self._get_retrun_code()
        self.result['output'] = self._output
        self.result['host_ok'] = callback.host_ok
        self.result['host_failed'] = callback.host_failed
        self.result['host_unreachable'] = callback.host_unreachable

    def _filter(self):
        pass

    def _get_retrun_code(self):

        if self._host_ok and not self._host_failed and not self._host_unreachable:
            #全部成功
            return 0
        elif not self._host_ok:
            # 全部失败
            return 1
        else:
            # 部分失败
            return 2