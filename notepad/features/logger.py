"""
Custom notepad logging helpers
"""

from functools import wraps, partial
import logging

LOG = logging.getLogger(__name__)



def configure_logging(verbose: int):
    level = logging.WARN
    if verbose == 1:
        level = logging.INFO
    elif verbose >= 2:
        level = logging.DEBUG

    logging.basicConfig(level=level)
    return level


def _logger(func, level):
    @wraps(func)
    def wrapper(*args, **kwargs):
        level("Entering method %s", func.__name__)
        has_other_params_beside_self = len(args) > 1
        if has_other_params_beside_self or kwargs:
            level("Args %s kwargs %s", args, kwargs)
        res = func(*args, **kwargs)
        level("Exiting method %s", func.__name__)
        return res

    return wrapper


log_info = partial(_logger, level=LOG.info)
log_debug = partial(_logger, level=LOG.debug)
log_action = log_info  # could have something more specific for actions
