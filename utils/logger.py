import logging
from pathlib import Path

def get_logger(name) :
    logs = Path("logs")
    logs.mkdir(exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    log_format = logging.Formatter (
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)

    file_handler = logging.FileHandler(
        logs / "application.log",
        encoding = "utf-8"
    )
    file_handler.setFormatter(log_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger 

