import logging
from   logging.handlers import RotatingFileHandler


# FIXME: give a new logger instead of the root logger
def set_root_logger(
        filename,
        level='INFO',
        format="%(message)s",
        **file_handler_kwargs):
    """
    Set and return the root handler to have a sole handler of `RotatingFileHandler`.
    """
    logging.basicConfig(level=level, format=format)
    handler = RotatingFileHandler(filename, **file_handler_kwargs)
    root = logging.getLogger()
    root.handlers[:] = [handler]
    return root
