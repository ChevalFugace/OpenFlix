from .media_types import Video, Software, Sound
from . import db


class Reading:

    def __init__(self):
        self.pages = 0


class Narative:

    def __init__(self):
        self.trailer = ""
        self.storyline = ""
        self.language = None


class Episodic:

    def __init__(self):
        self.season = 0
        self.episode = 0


class Movie(Video, Narative):
    id = db.Column(db.Integer, primary_key=True)
    pass


class Documentary(Video, Narative):
    id = db.Column(db.Integer, primary_key=True)
    pass


class Spectacle(Video, Narative):
    id = db.Column(db.Integer, primary_key=True)
    pass


class Anime(Video, Narative, Episodic):
    id = db.Column(db.Integer, primary_key=True)
    pass


class MusicVideo(Video):
    pass


class Concert(Video):
    pass


class Music(Sound):

    def __init__(self):
        self.album: None


class AudioBook(Sound, Narative):
    pass


class EBook(Reading, Narative):
    pass


class Game(Software, Narative):
    pass
