# _*_ coding:utf-8 _*_

from ansible_restful.ansible_api import ansible_api
from flask_restful import Resource
from flask_restful import reqparse
from flask_restful_swagger import swagger

from ModelClasses import AnsibleCommandModel, AnsibleRequestResultModel
from ansible_restful.ansible_api import ansible_options
from ansible_restful.flask_api import api
from ansible_restful.flask_api import log
import json


class Runner(Resource):
    @swagger.operation(
        notes='Run ad-hoc Ansible command',
        nickname='ansiblecommand',
        responseClass=AnsibleRequestResultModel.__name__,
        parameters=[
            {
                "name": "body",
                "description": "Inut object",
                "required": True,
                "allowMultiple": False,
                "dataType": AnsibleCommandModel.__name__,
                "paramType": "body"
            }
        ],
        responseMessages=[
            {
                "code": 200,
                "message": "Ansible command started"
            },
            {
                "code": 400,
                "message": "Invalid input"
            }
        ]
    )
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('hosts', type=str, help='need to specify hosts', required=True,action='append')
        parser.add_argument('module', type=str, help='module name', required=True)
        parser.add_argument('module_args', type=str, help='module_args', required=False)
        parser.add_argument('forks', type=int, help='forks', required=False)
        parser.add_argument('become', type=bool, help='run with become', required=False)
        parser.add_argument('become_method', type=str, help='become method', required=False)
        parser.add_argument('become_user', type=str, help='become user', required=False)

        args = json.loads(parser.parse_args())


        hosts = args['hosts']

        module = args['module']
        extra_vars = args['module_args']

        options = ansible_options.Options(args)

        runner = ansible_api.run_modules(hosts, module, extra_vars,options)

        log.info("[runner] hosts: %s, module: %s, args: %s, result: %s" % (hosts,module,args,runner))
        return runner


api.add_resource(Runner, '/runner')