import sys
import os
import logging

from configparser import ConfigParser, ExtendedInterpolation

from pyutils.initialzation import main, parse_args

from flask import Flask
from flask_socketio import SocketIO
from pyutils.common import token


class Config(ConfigParser):

    def __init__(self, config_file):
        super().__init__(interpolation=ExtendedInterpolation())

        self.add_section("env")
        self.set("env", "module", os.path.dirname(__file__))
        self.set("env", "cwd", os.getcwd())

        # for k, v in os.environ.items():
        #     self.set("env", k, v)

        self.read(config_file)

    def get_section(self, section):

        ret = dict()

        if self.has_section(section):
            for k, v in self.items(section):
                ret[k] = token(v)

        return ret


def route(rule, **options):

    def factory(func):
        setattr(func, "__route__", (rule, options))
        return func

    if callable(rule):
        func = rule
        rule = "/" + rule.__name__.lower()
        return factory(func)

    return factory


def load_routes(obj, bind_obj=None):

    if not bind_obj:
        bind_obj = obj

    for member_name in dir(obj):

        method = getattr(obj, member_name)

        if not callable(method) or not hasattr(method, "__route__"):
            continue

        rule, options = getattr(method, "__route__")

        try:
            bind_obj.add_url_rule(rule, view_func=method, **options)
        except Exception as e:
            print(e)
            logging.error(e)


def main_app(app):

    if issubclass(app, Flask):
        module = sys.modules[app.__module__]
        app = main(**parse_args(sys.argv))(app)
        setattr(module, "app", app)
        setattr(module, "socketio", SocketIO())
    return app


