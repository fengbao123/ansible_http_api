# _*_ coding:utf-8 _*_

import os,json

from ansible_restful.ansible_api import ansible_api
from flask import jsonify
from flask_restful import reqparse,Resource

from ModelClasses import AnsiblePlaybookModel, AnsibleRequestResultModel
from ansible_restful.ansible_api import ansible_options
from ansible_restful.flask_api import app,log,swagger,api
from ansible_restful import parse_config


class Playbook(Resource):
    def __init__(self):
        self.name = "playbook"

    def get_playbook(self,args):

        if self.name == 'deploy':
            playbook = parse_config.playbook_root + "/" + args['cmd'] + "_" + args['component'] + ".yml"
        else:
            playbook = args['playbook']
        return playbook

    def parse_params(self):
        parser = reqparse.RequestParser()
        parser.add_argument('hosts', type=str, help='need to specify hosts', required=True)
        parser.add_argument('playbook', type=str, help="playbook's path", required=True)
        parser.add_argument('extra_vars', type=dict, help='extra_vars', required=False)

        args = parser.parse_args()

        return  args

    def run_playbook(self):
        # 解析参数
        args = self.parse_params()

        options = ansible_options.Options(args)

        # 获取playbook
        playbook = self.get_playbook(args)

        # 检查playbook是否存在
        if not os.path.exists(playbook):
            error_log = jsonify({'message': 'Playbook not found in folder. Path does not exist: %s' % playbook})
            resp = app.make_response(error_log, 404)
            log.error("[%s] the playbook: %s is not exists!" % (self.name, playbook))
            return resp

        # extra_vars类型为str，需要转换成disk
        extra_vars = json.loads(args['extra_vars'])
        extra_vars['hosts'] = args['hosts']

        runner = ansible_api.run_playbook(playbook, extra_vars,options)

        log.info("[%s] hosts: %s, playbook: %s, extra_vars: %s, result: %s" % (
        self.name, extra_vars['hosts'], playbook, extra_vars, runner))

        return runner
        # return  json.dumps(runner, indent=4)

    @swagger.operation(
        notes='Run Ansible Playbook',
        nickname='ansibleplaybook',
        responseClass=AnsibleRequestResultModel.__name__,
        parameters=[
            {
                "name": "body",
                "description": "Inut object",
                "required": True,
                "allowMultiple": False,
                "dataType": AnsiblePlaybookModel.__name__,
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


api.add_resource(Playbook, '/playbook')

    # @app.route('%s' % self.url_path  ,methods=['POST'])
    # def playbook(self):
    #
    #     self.check_params_syntax(request)
    #
    #     extra_vars = request.json['extra_vars']
    #     extra_vars['hosts'] = request.json['hosts']
    #
    #     playbook = self.get_playbook(request)
    #
    #
    #     if not os.path.exists(playbook):
    #         error_log = jsonify({'error': 'Playbook not found in folder. Path does not exist: %s' % playbook})
    #         resp = app.make_response(error_log)
    #
    #         log.error("[%s] the playbook: %s is not exists!" % (self.name,playbook))
    #
    #         return resp
    #
    #     runner = ansible_api.run_playbook(playbook, extra_vars)
    #
    #     log.info("[%s] hosts: %s, playbook: %s, extra_vars: %s, result: %s" % (self.name,extra_vars['hosts'], playbook, extra_vars, runner))
    #
    #     return json.dumps(runner, indent=4)