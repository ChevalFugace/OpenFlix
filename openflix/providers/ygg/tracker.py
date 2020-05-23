from openflix import app
from flask import abort, Response, request
import requests
from http import HTTPStatus as status
import logging


class YGGTracker:

    def __init__(self, **options):

        self.load_config(options)
        self.ygg_tracker_url = None
        self.session = requests.Session()

        app.add_url_rule(self.config["path"], view_func=self.announce, 
                        subdomain=self.config["subdomain"])

    def get_url(self):

        domain = self.config['subdomain'] + "." + app.config["SERVER_NAME"]
        return domain + self.config['path']

    def exchange_url(self, url):
        
        self.ygg_tracker_url = url
        return self.get_url()

    def load_config(self, options):

        options.setdefault("hide_complete", True)
        options.setdefault("timeout", 5)
        options.setdefault("path", "/announce")
        options.setdefault("subdomain", "p2p")

        self.config = options

    def get_ygg_tracker(self):

        if self.ygg_tracker_url is None:
            from . import ygg
            self.ygg_tracker_url = ygg.exchange_url(self.get_url())

    def hide_download(self, query_string):

        params = query_string.split("&")

        for i, param in enumerate(params):
            key, _, _ = param.partition("=")
            if key == "downloaded":
                params[i] = "downloaded=0"
                break

        return "&".join(params)

    def announce(self):

        response = abort(status.INTERNAL_SERVER_ERROR)
        self.get_ygg_tracker()
        
        if self.ygg_tracker_url is None:
            return response

        headers = dict(request.headers)
        args = str(request.query_string)
        headers.pop("Host", None)

        if self.config["hide_complete"]:
            args = self.hide_download(args)

        for _ in range(self.config["max_retry"]):

            try:
                resp = self.session.get(
                    url=f"{self.ygg_tracker_url}?{args}",
                    headers=headers,
                    cookies=request.cookies,
                    timeout=self.config["timeout"]
                )
                
            except requests.Timeout:
                continue
            except Exception as e:
                logging.error(e)
            else:
                response = (resp.content,
                            resp.status_code,
                            resp.raw.headers)
                break
        else:
            logging.error("maximum announce try exceeded")

        return response
