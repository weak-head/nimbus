import logging
import os
import sys
from datetime import datetime

from nimbus.config import Config


def setup_logger(config: Config) -> bool:
    try:
        log_formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)-5.5s] - %(message)s",
        )

        root_logger = logging.getLogger()
        root_logger.setLevel(config.logs.level)

        if config.logs.location:
            today = datetime.now().strftime("%Y-%m-%d")
            log_dir = os.path.abspath(os.path.expanduser(config.logs.location))
            log_file = os.path.join(log_dir, f"{today}.log")
            os.makedirs(log_dir, exist_ok=True)

            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(log_formatter)
            root_logger.addHandler(file_handler)

        if config.logs.stdout:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(log_formatter)
            root_logger.addHandler(console_handler)

        for name in ["botocore", "boto3", "boto", "s3transfer"]:
            logging.getLogger(name).setLevel(logging.CRITICAL)

    except Exception:  # pylint: disable=broad-exception-caught
        logging.getLogger().setLevel(logging.CRITICAL)
        for handler in logging.getLogger().handlers[:]:
            logging.getLogger().removeHandler(handler)
        return False
    return True
