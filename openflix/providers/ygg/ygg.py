from openflix.interface import Interface, expose
from openflix import app
from mastodon import Mastodon
from yggtorrentscraper import (YggTorrentScraper, set_yggtorrent_tld,
                               get_yggtorrent_tld, categories)
import time
import datetime
from http import HTTPStatus as status
from flask import Response, abort, request
import requests
from threading import Timer
import re
import logging
import torrent_parser
from openflix.openflix_utils import route
from openflix import openflix_config
from random import randint
from .cloudflare_bypass import create_cfhandler

def make_ygg_url():

    return f"https://www2.yggtorrent.{get_yggtorrent_tld()}"


def get_first_occ(fields, name):

    for field in fields:
        if field.name == name:
            return field


def get_category(name):

    for category in categories:
        if category["name"] == name:
            return category


def t_to_sec(value):

    t = time.strptime(value, "%H:%M:%S")

    return datetime.timedelta(hours=t.tm_hour,
                              minutes=t.tm_min,
                              seconds=t.tm_sec).total_seconds()


class YGGProvider(Interface):

    def __init__(self, **options):

        self.load_config(options)

        with app.app_context():
            super().__init__("ygg",subdomain=self.config["subdomain"], 
                                url_prefix="/ygg")
        
        self.init_scraper()
        self.init_masto()
        self.tracker_url = None

        timing = options["update_tld_period"]
        if timing > 0:
            Timer(timing, self.update_domain).start()

        # app.add_url_rule("/provider/ygg/torrent/<int:id>", view_func=self.download_torrent)

    def init_scraper(self):

        self.scraper = YggTorrentScraper(create_cfhandler())
        key = app.get_key(self.config["keyname"])

        if key:
            login, _, password = key.partition(":")
            if not self.scraper.login(login, password):
                raise RuntimeWarning(f"could not loggin to yggtorrent")
        else:
            raise RuntimeWarning("ygg key file do not exist")

    def init_masto(self):

        token = app.get_key(self.config["masto_keyname"])

        self.masto = Mastodon(api_base_url=self.config["masto_url"],
                              access_token=token)

        self.update_domain()

    def convert_options(self, options):

        media_type = options.get("type")

        table = {"movie": ("films_&_videos", ("film", "animation")),
                 "show": ("films_&_videos", ("emission_tv", "serie_tv")),
                 "game": ("jeux_video", options.get("platform", ()))
                 }

        entry = table.get(media_type, None)
        if entry is not None:
            options["category"], options["subcategory"] = entry
        return options

    def gen_torrent_url(self, torrent):

        return "/provider/ygg/torrent" + torrent.url.partition("id=")[2]

    def convert_to_content(self, torrent):

        return {"provider": "ygg",
                "type": "torrent",
                "name": torrent.name,
                "size": torrent.size,
                "uri": self.gen_torrent_url(torrent),
                "data": {
                    "uploaded": torrent.uploaded_datetime.strftime("%Y-%m-%d"),
                    "completed": torrent.completed,
                    "seeders": torrent.seeders,
                    "leechers": torrent.leechers
                    }
                }

    def get_max_torrent(self, options):

        n = options.get("max_content", None)
        if n is not None and n.isdigit():
            return int(n)

        return self.config["max_torrent"]

    def query_content(self, details, options):

        options = self.convert_options(options)
        release_year = " " + details["release_date"].split("-")[0]

        options.update(name=details["title"] + release_year)

        torrents = self.scraper.search(options)

        if self.config["search_with_original_title"]:
            options.update(name=details["original_title"] + release_year)
            torrents.extend(self.scraper.search(options))

        for _, torrent in zip(range(self.get_max_torrent(options)), torrents):
            torrent_details = self.scraper.extract_details(torrent)
            yield self.convert_to_content(torrent_details)

    @route("/torrent/<int:id>")
    def get_torrent(self, id):

        url = f"{make_ygg_url()}/engine/download_torrent?id={id}"
        response = self.scraper.session.get(url)
        return torrent_parser.decode(response.content)
        
    def exchange_url(self, url):

        self.tracker_url = url

        try:
            data = self.get_torrent(randint(1000,5000))
        except Exception as e:
            logging.error(e)
        else:
            return data["announce"]

    def spoof_torrent(self, id):

        data = self.get_torrent(id)

        if self.tracker_url is None:
            from . import tracker
            self.tracker_url = tracker.exchange_url(data["announce"])
        
        data["announce"] = self.tracker_url

        return torrent_parser.encode(data)

    def download_torrent(self, id):
        
        try:
            data = self.spoof_torrent(id)
        except Exception as e:
            logging.error(e)
            return abort(status.INTERNAL_SERVER_ERROR)

        return Response(data, mimetype="application/x-bittorrent")

    def load_config(self, options):

        options.setdefault("masto_url", "https://mamot.fr/")
        options.setdefault("account_id", "YggTorrent@mamot.fr")
        options.setdefault("masto_keyname", "masto")
        options.setdefault("tld_pattern", r"[^\.]+\.yggtorrent\.([^/\"]+)")
        options.setdefault("update_tld_period", "10:00:00")  # every 10 hours
        options.setdefault("keyname", "ygg")
        options.setdefault("search_with_original_title", True)
        options.setdefault("max_torrent", 4)
        options.setdefault("subdomain", openflix_config.API_SUBDOMAIN)

        if type(options["update_tld_period"]) == str:
            period = options["update_tld_period"]
            options["update_tld_period"] = t_to_sec(period)

        self.config = options

    @expose
    def update_domain(self):

        accounts = self.masto.account_search(self.config["account_id"])

        for account in accounts:
            website = get_first_occ(account.fields, "Website")
            if website:
                match = re.search(self.config["tld_pattern"], website.value)
                if match:
                    set_yggtorrent_tld(match.group(1))

    @expose
    def set_ygg_tld(self, tld):
        set_yggtorrent_tld(tld)

    @expose
    def get_ygg_tld(self, type, id):
        return get_yggtorrent_tld()
