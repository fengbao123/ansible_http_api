# _*_ coding:utf-8 _*_


from ansible_restful.flask_api import config,app

if __name__ == '__main__':
    app.run(debug=True, host=config.get("Default", "Flask_tcp_ip"), use_reloader=False, port=int(config.get("Default", "Flask_tcp_port")))
