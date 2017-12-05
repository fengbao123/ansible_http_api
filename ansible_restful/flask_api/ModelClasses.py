from flask_restful_swagger import swagger
from flask_restful import fields


@swagger.model
class AnsibleExtraArgsModel:
    resource_fields = {
        'arg_name' : fields.String,
        'arg_value' : fields.String,
        }

@swagger.model
class AnsibleCommandModel:
    resource_fields = {
        'hosts': fields.List,
        'module': fields.String,
        'module_args': fields.String,
        'forks' : fields.Integer,
        'become': fields.Boolean,
        'become_method': fields.String,
        'become_user': fields.String,
    }

@swagger.model
class AnsiblePlaybookModel:
    resource_fields = {
        'hosts': fields.List,
        'playbook': fields.String,
        'extra_vars': fields.String,
        'forks' : fields.Integer,
    }

@swagger.model
class AansibleDeployModel:
    resource_fields = {
        'hosts': fields.List,
        'cmd': fields.String,
        'component': fields.String,
        'extra_vars': fields.String,
        'forks' : fields.Integer,
    }

@swagger.model
class AnsibleRequestResultModel:
    def __init__(self, task_id):
        pass