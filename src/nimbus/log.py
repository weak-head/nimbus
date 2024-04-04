import logging
import os
from datetime import datetime

from nimbus.config import Config


def configure(config: Config) -> None:

    # --
    # Log directory
    log_dir = "~/.nimbus/log"
    log_dir = os.path.abspath(os.path.expanduser(log_dir))
    os.makedirs(log_dir, exist_ok=True)

    # --
    # Log file
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"{today}.log")

    # --
    # Log config
    logging.basicConfig(
        filename=log_file,
        encoding="utf-8",
        level=logging.INFO,
        format="%(message)s",
    )

    # --
    # Disable log output for particular loggers
    for name in ["botocore", "boto3", "boto", "s3transfer"]:
        logging.getLogger(name).setLevel(logging.CRITICAL)
