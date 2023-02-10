"""
Set Global Logging Config
"""

import logging
from logging import config

LOG_CONFIG = {
    "version": 1,
    "loggers": {
        "default": {
            "level": "DEBUG",
            "handlers": ["consoleHandler", "fileHandler"]
        }
    },
    "handlers": {
        "consoleHandler": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "level": "DEBUG"
        },
        "fileHandler": {
            "formatter": "default",
            "class": "logging.FileHandler",
            "level": "ERROR",
            "filename": "error.log",
            "mode": "w"
        },
    },
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(levelname)s - %(message)s"
        }
    }
}

def get_logger(name):
    """Configure global logger"""
    config.dictConfig(LOG_CONFIG)
    logger = logging.getLogger(name)
    return logger
