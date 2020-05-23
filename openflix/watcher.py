#!/usr/bin/env python3

import os

from threading import Event, RLock

from inotify.constants import IN_ALL_EVENTS, MASK_LOOKUP
from inotify.adapters import InotifyTree

from pyutils.common import get_key_by_value
from pyutils.path import has_hidden

from . import openflix_config as config

from .interface import Interface, expose

from . import socket, app


class WatchNotifier(InotifyTree, Interface):

    def __init__(self, **options):

        self.load_config(options)

        self._thread = None
        self._thread_lock = RLock()
        self._stop_event = Event()
        self._stop_event.set()

        InotifyTree.__init__(self, self.config["dir"],
                             self.config["event_mask"])

        with app.app_context():
            Interface.__init__(self, "watcher")

    def load_config(self, conf):

        conf.setdefault("dir",          config.DEFAULT_WATCH_DIR)
        conf.setdefault("event_mask",   config.DEFAULT_WATCH_EVENT)
        conf.setdefault("tmp_file",     config.DEFAULT_WATCH_TMP)

        self.config = conf

        mask = 0
        ids = self.config["event_mask"].split("|")
        table = {**MASK_LOOKUP, IN_ALL_EVENTS: "IN_ALL_EVENTS"}

        for id in ids:
            flag = get_key_by_value(table, id)
            if flag is None:
                break
            else:
                mask |= flag
        else:
            self.config["event_mask"] = mask

    def _break_events(self):

        path = os.path.join(self.config["dir"], self.config["tmp_file"])

        with open(path, "w") as file:
            file.write("")

        os.remove(path)

    @expose
    def start(self):

        if self._stop_event.is_set():
            self._stop_event.clear()
            self._thread = socket.start_background_task(self.run)

    @expose
    def stop(self):

        if not self._stop_event.is_set():
            self._break_events()
            self._stop_event.set()

    def run(self):

        for event in self.event_gen(yield_nones=False):
            if self._stop_event.is_set():
                break
            self.send_reload_event(event)

    def send_reload_event(self, event):

        _, _, path, filename = event
        ext = os.path.splitext(filename)[-1]

        if has_hidden(path):
            return

        if ext == ".css":
            socket.emit("reload", {"data": "reload"},
                        broadcast=True, namespace="/test")
        elif ext in self.config["reload_ext"]:
            socket.emit("reload", {"data": "reload"},
                        broadcast=True, namespace="/test")
