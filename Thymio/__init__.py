import logging
import os
from datetime import datetime


def setup_logger(level='INFO'):
    """
    Set up the logger for the Thymio library.
    """
    internal_logger = logging.getLogger("Thymio")
    internal_logger.setLevel(level)

    # log to file
    if not os.path.exists("logs"):
        os.mkdir("logs")
    file_handler = logging.FileHandler(f"logs/{datetime.now().strftime('%Y%m%dT%H%M%S')}.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    internal_logger.addHandler(file_handler)

    # log to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    internal_logger.addHandler(console_handler)
    return internal_logger


logger = setup_logger()
