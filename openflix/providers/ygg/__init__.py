from openflix import config
from .ygg import YGGProvider
from .tracker import YGGTracker

ygg = YGGProvider(**config.get_section("ygg"))



tracker = YGGTracker(**config.get_section("tracker"))


def query_content(details, options):
    return list(ygg.query_content(details, options))
