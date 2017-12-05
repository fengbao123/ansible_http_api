# _*_ coding:utf-8 _*_


from ansible_restful.flask_api import app
from ansible_restful import parse_config

if __name__ == '__main__':
    app.run(debug=True,
            host=parse_config.flask_tcp_ip,
            use_reloader=False,
            port=parse_config.flask_tcp_port)
