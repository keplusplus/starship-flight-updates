import sys
import logging

class StarshipLogger:
    def __init__(self, log_file_name = 'latest.log', level = logging.INFO):
        self.log_file_name = log_file_name
        self.level = level

        self.logger = logging.getLogger()

        file = open(self.log_file_name, 'w')
        file.truncate(0)
        file.close()

        logFormatter = logging.Formatter("%(asctime)s [%(threadName)s] [%(levelname)s] | %(message)s")

        fileHandler = logging.FileHandler(self.log_file_name)
        fileHandler.setFormatter(logFormatter)
        self.logger.addHandler(fileHandler)

        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setFormatter(logFormatter)
        self.logger.addHandler(consoleHandler)

        self.logger.setLevel(logging.INFO)

    def error(self, msg):
        self.logger.error(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def log(self, msg):
        self.info(msg)