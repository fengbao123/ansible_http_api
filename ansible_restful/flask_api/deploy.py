# _*_ coding:utf-8 _*_

from flask_restful import reqparse

from ModelClasses import AansibleDeployModel, AnsibleRequestResultModel
from ansible_restful.flask_api import swagger,api,playbook


class Deploy(playbook.Playbook):

    def __init__(self):
        self.name = "deploy"

    def parse_params(self):
        parser = reqparse.RequestParser()

        parser.add_argument('hosts', type=str, help='need to specify hosts', required=True)
        parser.add_argument('cmd', type=str, help='cmd = install|uninstall/start/stop', required=True)
        parser.add_argument('component', type=str, help="component's name", required=False)
        parser.add_argument('extra_vars', type=dict, help='extra_vars', required=False)
        parser.add_argument('forks', type=dict, help='extra_vars', required=False)

        args = parser.parse_args()

        return args

    @swagger.operation(
        notes='Deploy component',
        nickname='deploy',
        responseClass=AnsibleRequestResultModel.__name__,
        parameters=[
            {
                "name": "body",
                "description": "Inut object: cmd=",
                "required": True,
                "allowMultiple": False,
                "dataType": AansibleDeployModel.__name__,
                "paramType": "body"
            }
        ],
        responseMessages=[
            {
                "code": 200,
                "message": "Ansible playbook started"
            },
            {
                "code": 400,
                "message": "Invalid input"
            }
        ]
    )
    def post(self):
        return self.run_playbook()

api.add_resource(Deploy, '/deploy')


