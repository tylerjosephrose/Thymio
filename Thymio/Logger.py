import logging
import logging.handlers
import os


def setup_logger(level='INFO'):
    """
    Set up the logger for the Thymio library.
    """
    internal_logger = logging.getLogger("Thymio")
    internal_logger.setLevel(level)

    # log to file
    if not os.path.exists("logs"):
        os.mkdir("logs")
    filename = "logs/Thymio.log"

    file_handler = logging.handlers.TimedRotatingFileHandler(filename, when='midnight')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    internal_logger.addHandler(file_handler)

    # log to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    internal_logger.addHandler(console_handler)
    return internal_logger


logger = setup_logger()
