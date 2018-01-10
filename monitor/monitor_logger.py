import os
import logging

import sys

LOG_PATH = 'logs'
LOG_FILE = 'text.txt'


def get_logger(name):
    i_logger = logging.getLogger(name)
    if os.path.exists(LOG_PATH):
        pass
    else:
        os.mkdir(LOG_PATH)
    # 指定logger输出格式
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
    # 文件日志
    file_handler = logging.FileHandler("%s/%s" % (LOG_PATH, LOG_FILE))
    file_handler.setFormatter(formatter)  # 可以通过setFormatter指定输出格式
    # 控制台日志
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.formatter = formatter  # 也可以直接给formatter赋值
    # 为logger添加的日志处理器，可以自定义日志处理器让其输出到其他地方
    i_logger.addHandler(file_handler)
    i_logger.addHandler(console_handler)
    # 指定日志的最低输出级别，默认为WARN级别
    i_logger.setLevel(logging.DEBUG)
    return i_logger


if __name__ == '__main__':
    logger = get_logger(__name__)
    logger.debug('test')
