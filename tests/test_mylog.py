import logging
from utils.mylog import get_log

log = get_log(__name__, level=logging.DEBUG)


def test_mylog(capsys):
    log.debug("test test")
    captured = capsys.readouterr()
    assert captured.out == "\x1b[37mDEBUG:tests.test_mylog:test test\x1b[0m\n"



