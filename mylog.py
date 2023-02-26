import logging
import tqdm

class TqdmLoggingHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.tqdm.write(msg)
            self.flush()
        except Exception:
            self.handleError(record)

def get_log(name: str="default", level=logging.DEBUG):
    log = logging.getLogger(name)
    log.setLevel(level)
    formatter = logging.Formatter(logging.BASIC_FORMAT)
    hdlr=TqdmLoggingHandler()
    hdlr.setFormatter(formatter) 
    log.addHandler(hdlr)
    return log
