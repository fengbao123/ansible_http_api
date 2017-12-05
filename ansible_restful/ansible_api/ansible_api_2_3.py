# -*- coding: utf-8 -*-
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.inventory import Inventory
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.vars import VariableManager
import os

from ansible_result import ResultsCollector,AnsibleReturn


loader = DataLoader()
variable_manager = VariableManager()

myinventory = os.path.dirname(os.path.realpath(__file__)) + '../myinventory/mysql_inventory.py'

#inventory = Inventory(loader=loader, variable_manager=variable_manager,host_list=myinventory)

inventory = Inventory(loader=loader, variable_manager=variable_manager)

# myinventory = Inventory(loader=loader, variable_manager=variable_manager,host_list='/etc/ansible/hosts')
variable_manager.set_inventory(inventory)

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
        tqm.run(play)
        return AnsibleReturn(callback).result

    finally:
        if tqm is not None:
            tqm.cleanup()

#调用playbook接口
def run_playbook(books,extra_vars,options):

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

        return AnsibleReturn(callback).result

    except Exception as e:
        print e