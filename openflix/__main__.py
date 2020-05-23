from . import app, config, db, socket, cors
from .media_api import MediaAPI
from . import routes

if __name__ == "__main__":

    db.init_app(app)
    socket.init_app(app)
    cors.init_app(app)

    media_api = MediaAPI(**config.get_section("media-server"))

    if app.debug:
        from .watcher import WatchNotifier
        watcher = WatchNotifier(**config.get_section("watcher"))
        watcher.start()
    
    app.run(host="0.0.0.0")
    socket.run(app)
