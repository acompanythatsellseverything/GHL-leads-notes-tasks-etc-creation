import logging
import os
from logging.handlers import TimedRotatingFileHandler


log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Log file path
log_file = os.path.join(log_directory, "app.log")

# Set up file logging (rotating logs daily)
file_handler = TimedRotatingFileHandler(
    log_file, when="midnight", interval=1, backupCount=30, encoding="utf-8"
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
file_handler.setLevel(logging.INFO)

# Set up console logging (for terminal output)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
console_handler.setLevel(logging.INFO)

# Get the root logger and configure it
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
