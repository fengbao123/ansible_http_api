# -*- coding: utf-8 -*-
from distutils.version import LooseVersion
import ansible

class Options(object):
    def __init__(self,args):

        # 设置默认值
        args.setdefault('forks',10)
        args.setdefault('become', None)
        args.setdefault('become_method', None)
        args.setdefault('become_user', None)
        args.setdefault('check', False)

        self.connection = "smart"
        self.forks = args['forks']  # 并发数
        self.check = args['check']
        self.become = args['become']
        self.become_method = args['become_method']
        self.remote_user = None
        self.become_user= args['become_user']

        self.private_key_file=None
        self.ssh_common_args=None
        self.sftp_extra_args=None
        self.scp_extra_args=None
        self.ssh_extra_args=None
        self.verbosity=None

        if LooseVersion(ansible.__version__) > LooseVersion('2.3.0.0'):
            self.tags = ''
            self.skip_tags=''

    def __getattr__(self, name):
        return None