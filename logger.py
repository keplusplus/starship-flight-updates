import sys
import logging
import message

class StarshipLogger:
    def __init__(self, log_file_name = 'latest.log', level = logging.INFO, broadcast = False):
        self.log_file_name = log_file_name
        self.level = level
        self.broadcast = broadcast

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

        self.logger.setLevel(self.level)

    def error(self, msg):
        self.logger.error(msg)
        if self.broadcast:
            message.send_message(f'Log: [ERROR] {msg}', color = 13632027)

    def warning(self, msg):
        self.logger.warning(msg)
        if self.broadcast:
            message.send_message(f'Log: [WARN] {msg}', color = 16767232)

    def info(self, msg):
        self.logger.info(msg)
        if self.broadcast:
            message.send_message(f'Log: [INFO] {msg}', color = 1237395)

    def debug(self, msg):
        self.logger.debug(msg)

    def log(self, msg):
        self.info(msg)