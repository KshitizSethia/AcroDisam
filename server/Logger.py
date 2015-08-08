import logging

import string_constants


logging_format = "%(levelname)s: %(process)d %(asctime)s %(message)s"
logging.basicConfig(filename=string_constants.file_logs,
                    level=logging.DEBUG, format=logging_format, datefmt='%m/%d/%Y %I:%M:%S %p')
common_logger = logging.getLogger(string_constants.name_logger)
