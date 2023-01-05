import os
import logging


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "loggers": {
        # Configure all loggers
        "": {
            "level": os.getenv("LOG_LEVEL_APP"),
            "handlers": ["console", "file"],
            "propagate": False,
        },
        # Azure core logger
        "azure.core.pipeline.policies.http_logging_policy": {
            "level": "WARN",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        # HTTP request logger
        "urllib3.connectionpool": {
            "level": "WARN",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        # Azure quantum logger
        "azure.quantum": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },
    "handlers": {
        "console": {
            "formatter": "formatter",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "formatter": "formatter",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.getenv("LOG_FILE"),
            "mode": "a",
            "maxBytes": 100000,
            "backupCount": 20,
        },
    },
    "formatters": {
        "formatter": {
            "format": "[%(asctime)s] [%(name)s] [%(thread)d] "
            "[%(levelname)s][%(funcName)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
}
