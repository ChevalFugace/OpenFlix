#!/usr/bin/env python3

import sys
from pyutils.initialzation import parse_args

from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

import openflix.openflix_config as conf

from .server import OpenFlix
from .openflix_utils import Config

argv = parse_args(sys.argv)

config = Config(argv.get("config", conf.DEFAULT_CONFIG))

app = OpenFlix(**config.get_section("flask"))

socket = SocketIO(**config.get_section("socketio"))

db = SQLAlchemy(**config.get_section("database"))

cors = CORS(**config.get_section("cors"))