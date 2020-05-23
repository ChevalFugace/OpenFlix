from flask import Blueprint, request, current_app

from inspect import isclass
from functools import update_wrapper
from http import HTTPStatus as status
from functools import wraps

from pyutils.common import token, get_err


# global test
# def test():
#     return jsonify({"haha": "ohoh"}), status.OK

class Interface:

    def __init__(self, name, **kwargs):

        kwargs.setdefault("url_prefix", "/")
        self._blueprint = Blueprint(name, self.__class__.__name__)

        if hasattr(self, "__expose__"):

            _, options = getattr(self, "__expose__")

            options.setdefault("methods", current_app.config["api_methods"])

            group = options.get("group", current_app.cfg["admin_group"])

            group_dec = current_app.group_access(group)
            route_dec = self._blueprint.route("/<name>", **options)
            wrapper = group_dec(self._interface)
            route_dec(update_wrapper(wrapper, self._interface))

        for member_name in dir(self):
            method = getattr(self, member_name)

            if not callable(method):  # or not hasattr(method, "__expose__"):
                continue

            if hasattr(method, "__expose__"):
                rule, options = getattr(method, "__expose__")
                options["methods"] = ("POST",)
                group = options.get("group", current_app.config["admin_group"])
                method = self.gen_wrapper(method)

            elif hasattr(method, "__route__"):
                rule, options = getattr(method, "__route__")
                group = options.get("group", None)  # current_app.config["guest_group"])

            else:
                continue

            if group:
                method = current_app.group_access(group)(method)

            self._blueprint.add_url_rule(rule, view_func=method, **options)

        current_app.register_blueprint(self._blueprint, **kwargs)

    def gen_wrapper(self, method):

        @wraps(method)
        def _wrapper():

            try:
                if request.data:
                    args = request.json
                else:
                    args = dict()
                return str(method(**args)) + "\n", status.OK
            except TypeError as e:
                return get_err(e), status.BAD_REQUEST

        return _wrapper

    def _interface(self, name):

        try:
            member = getattr(self, name)

            if ((callable(member) and hasattr(member, "__expose__"))
                    or name == "_interface"):
                raise AttributeError()

            if request.method == "POST":
                if request.data:
                    args = request.json
                else:
                    args = dict()
                return str(member(**args)) + "\n", status.OK

            elif request.method == "GET":
                return str(member) + "\n", status.OK

            elif request.method == "PUT":
                setattr(self, name, token(request.data))

            elif request.method == "DELETE":
                delattr(self, name)

        except TypeError as e:
            return get_err(e), status.BAD_REQUEST
        except AttributeError as e:
            return get_err(e), status.BAD_REQUEST

        return "", status.OK


def expose(rule, **options):

    def factory(func):
        setattr(func, "__expose__", (rule, options))
        return func

    if callable(rule) or isclass(rule):
        func = rule
        rule = "/" + rule.__name__.lower()
        return factory(func)

    return factory

    # if hasattr(method, "__blueprint_route__"):

    #     member_rule, options = getattr(method, "__blueprint_route__")

    #     # group_dec = app.group_access(group)
    #     route_dec = self._blueprint.route(member_rule, **options)

    #     setattr(self, member_name, route_dec(group_dec(method)))
