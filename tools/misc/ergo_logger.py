import logging
import sys

from logging.handlers import TimedRotatingFileHandler
FORMATTER = logging.Formatter("%(asctime)s -%(process)s %(thread)s-%(levelname)s-line:%(lineno)d %(funcName)s- %(message)s")
LOG_FILE = "logs/ergo_video.log"

def get_console_handler():
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setFormatter(FORMATTER)
   return console_handler
def get_file_handler(filename=LOG_FILE):
   file_handler = TimedRotatingFileHandler(filename, when='midnight')
   file_handler.setFormatter(FORMATTER)
   return file_handler
def get_logger(logger_name):
   logger = logging.getLogger(logger_name)
   logger.setLevel(logging.DEBUG) # better to have too much log than not enough
   logger.addHandler(get_console_handler())
   logger.addHandler(get_file_handler(logger_name))
   # with this pattern, it's rarely necessary to propagate the error up to parent
   logger.propagate = False
   return logger