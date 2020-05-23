
# __package__ = None

import os
import logging
from http import HTTPStatus as status
from string import hexdigits
from functools import wraps

from pyutils.common import get_err

from flask import Flask, abort, request

# from werkzeug.security import generate_password_hash, check_password_hash

from . import openflix_config as config
from .interface import Interface, expose


class OpenFlix(Flask, Interface):

    def __init__(self, **options):
        Flask.__init__(self, "OpenFlix")

        self.load_config(options)
        self.init_logger()
        self.load_keys()

        with self.app_context():
            Interface.__init__(self, "server")

    def init_logger(self):

        logging.basicConfig(
            filename=self.config["log_file"],
            level=self.config["log_level"],
            format="%(asctime)s - %(message)s",
            datefmt="%m/%d/%Y %I:%M:%S %p"
        )

    def get_key(self, name, id=0):

        keys = self._keys.get(name)
        if keys and id < len(keys):
            return keys[id]

    def load_keys(self):

        keys_dir = self.config["keys_dir"]

        self._keys = dict()

        try:
            for key_file in os.listdir(keys_dir):

                key_path = os.path.join(keys_dir, key_file)
                name, _ = os.path.splitext(key_file)

                with open(key_path, "r") as file:
                    for key in file.readlines():
                        self._keys.setdefault(name, list())
                        self._keys[name].append(key.rstrip())

        except OSError as e:
            print(e)
            logging.warn(get_err(e))

    def load_config(self, conf):

        conf.setdefault("key_length",   config.DEFAULT_KEYLENGTH)
        conf.setdefault("keys_dir",     config.DEFAULT_KEYDIR)
        conf.setdefault("database",     config.DEFAULT_DATABASE)
        conf.setdefault("admin_group",  config.DEFAULT_ADMIN_GROUP)
        conf.setdefault("guest_group",  config.DEFAULT_GUEST_GROUP)
        conf.setdefault("log_file",     config.DEFAULT_LOGFILE)
        conf.setdefault("log_level",    config.DEFAULT_LOGLEVEL)
        conf.setdefault("sql_dir",      config.DEFAULT_SQL_DIR)
        conf.setdefault("api_methods",  config.DEFAULT_API_METHODS)
        
        self.config.update(**conf)

        # fix uppercase configs for flask
        for key in list(self.config.keys()):
            if key not in ("key_length", "keys_dir", "database", "api_methods",
                           "admin_group", "log_file", "log_level", "sql_dir"):
                self.config[key.upper()] = self.config.pop(key)

    def test_key(self, key, group):

        keys = self._keys.get(group)
        if keys is not None:
            return key in keys
        return False

    @expose
    def is_valid_std_key(self, key):

        if len(key) == self.config["key_length"]:
            if all(c in hexdigits for c in key):
                return True
        return False

    @expose
    def save_keys(self):

        keys_dir = self.config["keys_dir"]

        try:
            for group, keys in self._keys.items():

                key_path = os.path.join(keys_dir, f"{group}.key")
                with open(key_path, "w") as file:
                    file.write("\n".join(keys))
        except OSError as e:
            logging.error(get_err(e))

    @expose
    def add_key(self, key, group, std=False, save=True):

        keys = self._keys.setdefault(group, list())
        if key not in keys and (not std or self.is_valid_std_key(key)):
            keys.append(key)

        if save:
            self.save_keys()

    def admin(self, func):

        return self.group_access(self.config["admin_group"])(func)

    def group_access(self, group):

        def factory(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = request.headers.get("api-key")
                if self.test_key(key, group):
                    return func(*args, **kwargs)
                return abort(status.UNAUTHORIZED)
            return wrapper
        return factory


# __init__ #

        # self.load_sql_script()
        # self.teardown_appcontext(self.close_db)

###################################

# def get_db(self):

    #     ctx = _app_ctx_stack.top
    #     if ctx is not None:
    #         if not hasattr(ctx, "_database"):
    #             try:
    #                 dbfile = self.config["database"]
    #                 ctx._database = sqlite3.connect(dbfile)
    #             except RuntimeError as e:
    #                 logging.error(get_err(e))
    #             finally:
    #                 if ctx._database:
    #                     ctx.database.close()
    #         return ctx._database

    # def close_db(self, exception):

    #     ctx = _app_ctx_stack.top
    #     if ctx is not None:
    #         if hasattr(ctx, '_database'):
    #             ctx._database.close()

    # def load_sql_script(self):

    #     self.sql_queries = dict()
    #     sql_dir = self.config["sql_script_dir"]

    #     try:

    #         for file in os.listdir(sql_dir):

    #             fullpath = os.path.join(sql_dir, file)
    #             name, ext = os.path.splitext(file)

    #             if ext == ".sql":
    #                 with open(fullpath, "r") as file:
    #                     self.sql_queries[name] = file.read()

    #     except OSError as e:
    #         logging.error(get_err(e))
