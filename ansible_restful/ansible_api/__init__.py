# _*_ coding:utf-8 _*_
from distutils.version import LooseVersion

import ansible

from  ansible_restful.flask_api import log

log.info("ansible version is %s" % ansible.__version__)

if LooseVersion(ansible.__version__) > LooseVersion('2.2.0.0') and LooseVersion(ansible.__version__) < LooseVersion('2.3.0.0'):
    import ansible_api_2_2 as ansible_api
elif LooseVersion(ansible.__version__) > LooseVersion('2.3.0.0') and LooseVersion(ansible.__version__) < LooseVersion('2.4.0.0'):
    import ansible_api_2_3 as ansible_api
elif LooseVersion(ansible.__version__) > LooseVersion('2.4.0.0') and LooseVersion(ansible.__version__) < LooseVersion('2.5.0.0'):
    import ansible_api_2_4 as ansible_api