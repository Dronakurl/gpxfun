import logging
import tqdm
import colorlog

class TqdmLoggingHandler(colorlog.StreamHandler):
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)
        self.setFormatter(colorlog.ColoredFormatter("%(log_color)s%(levelname)s:%(name)s:%(message)s"))

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.tqdm.write(msg)
            self.flush()
        except Exception:
            self.handleError(record)


def get_log(name: str = "default", level=logging.DEBUG):
    log = logging.getLogger(name)
    log.setLevel(level)
    hdlr = TqdmLoggingHandler()
    log.addHandler(hdlr)
    return log
