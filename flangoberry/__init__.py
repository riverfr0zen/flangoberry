import logging
from flangoberry import default_settings as settings


__version__ = settings.VERSION


logging.basicConfig(level=settings.LOG_LEVELS["flangoberry"])
logger = logging.getLogger(__name__)
for litem in settings.LOG_LEVELS.keys():
    logging.getLogger(litem).setLevel(settings.LOG_LEVELS[litem])
