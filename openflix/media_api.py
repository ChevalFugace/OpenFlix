import os
import sys
import importlib
import logging
from http import HTTPStatus as status
from functools import wraps
# from flask_restful import Resource, Api
from flask import jsonify, request


from . import openflix_config as config
from . import db
from . import app
from .openflix_utils import route
from .interface import Interface

from pyutils.common import get_err
from sqlalchemy.types import ARRAY
from tmdbv3api import TMDb, Movie, TV


class Media(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    date = db.Column(ARRAY(db.Integer, dimensions=3))
    rating = db.Column(db.Float)
    genres = db.Column(ARRAY(db.String(64)))
    uri = db.Column(ARRAY(db.String(256)))

    def __repr__(self):
        return f'<name {self.name}>' \
                f'<date {self.date}>' \
                f'<rating {self.rating}>' \
                f'<genre {self.genres}>' \
                f'<uri {self.uri}>'


class MediaAPI(Interface):

    _providers = dict()
    _contents = dict()

    def __init__(self, **options):

        self.load_config(options)
        
        with app.app_context():
            super().__init__("media", subdomain=self.config["subdomain"])

        self.load_providers()
        self.load_medias()

        if self.config["use_caching"]:
            self.get_content = self.query_wrapper(self.get_content)

        self.load_metadata_provider()

    def load_medias(self):

        self._medias = {"movie": Movie(),
                        "show": TV()}

    def load_metadata_provider(self):

        self.tmdb = TMDb()
        self.tmdb.api_key = app.get_key(self.config["tmdb_keyname"])
        self.tmdb.language = self.config["language"]

    def load_config(self, conf):

        self.config = conf
        self.config.setdefault("preferred_provider", config.DEFAULT_PREF_PVD)
        self.config.setdefault("providers_dir",     config.DEFAULT_PVD_DIR)
        self.config.setdefault("extra_providers",   config.DEFAULT_EXTRA_PVD)
        self.config.setdefault("use_caching",       config.DEFAULT_USE_CACHE)
        self.config.setdefault("tmdb_keyname",      config.DEFAULT_TMDB_KEY)
        self.config.setdefault("language",          config.DEFAULT_LANGUAGE)
        self.config.setdefault("subdomain",         config.API_SUBDOMAIN)

    def load_providers(self):

        self._providers = list()

        directory = self.config["providers_dir"]
        preferred = self.config["preferred_provider"]
        extra = self.config["extra_providers"]

        try:
            sys.path.insert(0, directory)

            for entity in os.listdir(directory) + extra:
                name, *_ = os.path.splitext(entity)
                try:
                    handle = importlib.import_module(name, f"provider.{name}")
                except Exception as e:
                    logging.error(e)
                else:
                    if name == preferred:
                        self._providers.insert(0, handle)
                    else:
                        self._providers.append(handle)

            sys.path.remove(directory)

        except OSError as e:
            logging.error(e)

    def get_class_by_tablename(self, tablename):
        """Return class reference mapped to table.

        :param tablename: String with name of table.
        :return: Class reference or None.
        """
        for table in db.Model._decl_class_registry.values():
            name = getattr(table, "__tablename__")
            if name == tablename:
                return table

    def query_cache(self, **desc):
        pass
        # table = self.get_class_by_tablename()

    def cache_media(self, media):
        pass
        # db.session.add(media)
        # db.session.commit()

    def query_wrapper(self, func):

        @wraps(func)
        def _wrapper(*args, **kwargs):
            media = self.query_cache(*args, **kwargs)
            if media:
                return media
            media = func(*args, **kwargs)
            self.cache_media(media)
            return media

        return _wrapper

    def search_media(self, desc, handler):

        term = desc.get("name")
        page = desc.get("page", 1)

        if term:
            handler.language = desc.get("language", self.tmdb.language)
            medias = handler.search(term, page)

            for media in medias:
                yield media.entries

        return list()

    def get_media_details(self, id):

        media_type = request.args.get("type", None)

        if media_type is not None:
            handler = self._medias.get(media_type, None)
            if handler is not None:
                language = request.args.get("language", self.tmdb.language)
                handler.language = language
                details = handler.details(id)
                return details.entries

    def random(self):
        pass

    @route("/content/<int:id>")
    def get_content(self, id):

        details = self.get_media_details(id)

        if details is None:
            return jsonify({}), status.BAD_REQUEST

        for provider in self._providers:
            try:
                content = provider.query_content(details, dict(request.args))
            except Exception as e:
                logging.error(e)
            else:
                return jsonify(content), status.OK

        return jsonify(list()), status.NOT_FOUND

    @route("/details/<int:id>")
    def get_details(self, id):

        details = self.get_media_details(id)

        if details is None:
            return jsonify({}), status.BAD_REQUEST

        return jsonify(details), status.OK
    
    def get_popular(self, desc, handler):

        page = desc.get("page", 1)

        medias = handler.popular(page)

        for media in medias:
            yield media.entries

    @route
    def popular(self):

        media_type = request.args.get("type", None)
        medias = list()

        if media_type is None:
            for handler in self._medias.values():
                medias.extend(self.get_popular(request.args, handler))
        else:
            handler = self._medias.get(media_type)
            if handler is not None:
                medias = list(self.get_popular(request.args, handler))

        sort_by = request.args.get("sort_by", None)
        if sort_by is not None:
            medias.sort(key=lambda x: x[sort_by], reverse=True)

        return jsonify(medias), status.OK

    @route
    def search(self):

        media_type = request.args.get("type", None)
        medias = list()

        if media_type is None:
            for handler in self._medias.values():
                medias.extend(self.search_media(request.args, handler))
        else:
            handler = self._medias.get(media_type)
            if handler is not None:
                medias = list(self.search_media(request.args, handler))

        sort_by = request.args.get("sort_by", None)
        if sort_by is not None:
            medias.sort(key=lambda x: x[sort_by], reverse=True)

        return jsonify(medias), status.OK

    @route("exclu")
    def get_excus(self):
        pass
