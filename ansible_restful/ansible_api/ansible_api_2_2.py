#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.inventory import Inventory
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.plugins import callback_loader
from ansible.plugins.callback import CallbackBase
from ansible.vars import VariableManager
import os


loader = DataLoader()
variable_manager = VariableManager()

myinventory = os.path.dirname(os.path.realpath(__file__)) + '../myinventory/mysql_inventory.py'

#inventory = Inventory(loader=loader, variable_manager=variable_manager,host_list=myinventory)

inventory = Inventory(loader=loader, variable_manager=variable_manager)

# myinventory = Inventory(loader=loader, variable_manager=variable_manager,host_list='/etc/ansible/hosts')
variable_manager.set_inventory(inventory)

#get result output
class ResultsCollector(CallbackBase):
    def __init__(self, *args, **kwargs):
        super(ResultsCollector, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}
        self.host_result = {}

    # def v2_runner_on_unreachable(self, result, ignore_errors=False):
    #     name = result._host.get_name()
    #     task = result._task.get_name()
    #     #ansible_log(result)
    #     #self.host_unreachable[result._host.get_name()] = result
    #     self.host_result.setdefault(name, {})[task]  = result._result
    #
    # def v2_runner_on_ok(self, result,  *args, **kwargs):
    #     name = result._host.get_name()
    #     task = result._task.get_name()
    #     if task == "setup":
    #         pass
    #     elif "Info" in task:
    #         self.host_result.setdefault(name, {})[task]  = result._result
    #     else:
    #         #ansible_log(result)
    #         #self.host_result[name] = (dict(task=task, result=result._result))
    #         self.host_result.setdefault(name,{})[task] =result._result
    #
    # def v2_runner_on_failed(self, result,   *args, **kwargs):
    #     name = result._host.get_name()
    #     task = result._task.get_name()
    #     #ansible_log(result)
    #     self.host_result.setdefault(name, {})[task]  = result._result

    def v2_runner_on_ok(self, result,  *args, **kwargs):
        name = result._host.get_name()
        task = result._task.get_name()
        #self.host_result.setdefault(name,{})[task] =result._result
        #self.host_ok.setdefault(name, {})[task] = result._result
        #self.host_ok[name] = result
        if task == "setup":
            pass
        else:
            self.host_ok.setdefault(name, {})[task] = result._result
            self.host_result[name] = result._result

    def v2_runner_on_unreachable(self, result, ignore_errors=False):
        name = result._host.get_name()
        task = result._task.get_name()
        #self.host_unreachable.setdefault(name, {})[task]  = result._result
        self.host_unreachable[name] = result._result
        self.host_result[name] = result._result

    def v2_runner_on_failed(self, result,   *args, **kwargs):
        name = result._host.get_name()
        task = result._task.get_name()
        #self.host_failed.setdefault(name, {})[task]  = result._result
        self.host_failed[name] = result._result
        self.host_result[name] = result._result

# class Options(object):
#     def __init__(self):
#         self.connection = "smart"
#         self.forks = 100
#         self.check = False
#         self.become = None
#         self.become_method = None
#         self.remote_user = None
#         self.become_user= None
#         self.private_key_file=None
#         self.ssh_common_args=None
#         self.sftp_extra_args=None
#         self.scp_extra_args=None
#         self.ssh_extra_args=None
#         self.verbosity=None
#     def __getattr__(self, name):
#         return None
#
# options = Options()

#调用模块接口
def run_modules(host,module,args,options):

    task_list = [
        dict(action=dict(module='%s' % module,
                         args='%s' % args)),
    ]

    play_source = dict(
        name="Ansible Ad-Hoc",
        hosts=host,
        gather_facts="no",
        tasks=task_list
    )

    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
    tqm = None
    callback = ResultsCollector()

    try:
        tqm = TaskQueueManager(
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            options=options,
            passwords=None,
            run_tree=False,
        )
        tqm._stdout_callback = callback
        result = tqm.run(play)
        return callback

    finally:
        if tqm is not None:
            tqm.cleanup()

#调用playbook接口
def run_playbook(books,extra_vars,options):
    #results_callback = callback_loader.get('json')
    playbooks = [books]

    variable_manager.extra_vars=extra_vars
    callback = ResultsCollector()


    pd = PlaybookExecutor(
        playbooks=playbooks,
        inventory=inventory,
        variable_manager=variable_manager,
        loader=loader,
        options=options,
        passwords=None,

        )
    pd._tqm._stdout_callback = callback

    try:
        pd.run()

        result_all = {'success': {}, 'failed': {}, 'unreachable': {}}

        for host, result in callback.host_ok.items():
            result_all['success'][host] = result

        for host, result in callback.host_failed.items():
            # 忽略掉的错误信息不记录日志
            if result['_ansible_parsed'] == True:
                pass
            else:
                result_all['failed'][host] = result['msg']




        for host, result in callback.host_unreachable.items():
            result_all['unreachable'][host] = result['msg']

        # for i in result_all['success'].keys():
        #     return result_all
        return result_all
        #return callback.host_failed

    except Exception as e:
        print e