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



# def post(self):
    #     parser = reqparse.RequestParser()
    #
    #     parser.add_argument('hosts', type=str, help='need to specify hosts', required=True)
    #     parser.add_argument('cmd', type=str, help='cmd = install|uninstall/start/stop', required=True)
    #     parser.add_argument('component', type=str, help="component's name", required=False)
    #     parser.add_argument('extra_vars', type=dict, help='extra_vars', required=False)
    #
    #     args = parser.parse_args()
    #     hosts = args['hosts']
    #     playbook = config.get("Default", "playbook_root") + "/"  + args['cmd'] +"_" + args['component'] + ".yml"
    #
    #     print playbook
    #     print hosts
    #
    #     extra_vars = args['extra_vars']
    #
    #     extra_vars['hosts'] = hosts
    #
    #     runner = ansible_api.run_playbook(playbook, extra_vars)
    #     print  runner
    #
    #     return runner
    #     #return  json.dumps(runner, indent=4)

# @app.route('/deploy',methods=['POST'])
# def deploy():
#
#     if not request.json or not 'cmd' in request.json or not 'component' in request.json or not 'hosts' in request.json:
#         error_log = jsonify({'error': 'you must check cmd & component & hosts are existing?'})
#         resp = app.make_response(error_log)
#
#         log.error("[deploy] params json syntax error! %s " % request.json)
#         return resp
#
#     cmd = request.json['cmd']
#     component = request.json['component']
#     extra_vars = request.json['extra_vars']
#     extra_vars['hosts'] = request.json['hosts']
#
#     playbook = config.get("Default", "playbook_root") +"/" +  cmd + "_" +component + ".yml"
#
#
#     if not os.path.exists(playbook):
#         #resp = app.make_response(str.format("Playbook not found in folder. Path does not exist: {0}" , playbook),404)
#
#         error_log = jsonify({'error': 'Playbook not found in folder. Path does not exist: %s' % playbook})
#         resp = app.make_response(error_log)
#
#         log.error("[deploy] the playbook: %s is not exists!" % (playbook))
#
#         return resp
#
#     runner = ansible_api.run_playbook(playbook, extra_vars)
#
#     log.info("[deploy] hosts: %s, playbook: %s, extra_vars: %s, result: %s" % (extra_vars['hosts'], playbook, extra_vars, runner))
#
#     return json.dumps(runner, indent=4)

# from playbook import Playbook
#
# class Deploy(Playbook):
#
#     def __init__(self):
#         self.name = 'deploy'
#         self.url_path = "/deploy"
#
#     def get_playbook(self,request):
#         playbook = config.get("Default", "playbook_root") + "/" + request.json['cmd'] + "_" + request.json['component'] + ".yml"
#         return playbook
#
#     def check_params_syntax(self,request):
#         if not request.json or not 'cmd' in request.json or not 'component' in request.json or not 'hosts' in request.json:
#
#             error_log = jsonify({'error': 'you must check cmd & component & hosts are existing?'})
#             resp = app.make_response(error_log)
#
#             log.error("[%s] params json syntax error! %s " % (self.name,request.json))
#             return resp



