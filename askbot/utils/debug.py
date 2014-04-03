"""debugging utilities"""
import sys

def debug(message):
    """print debugging message to stderr"""
    message = unicode(message).encode('utf-8')
    sys.stderr.write(message + '\n')
