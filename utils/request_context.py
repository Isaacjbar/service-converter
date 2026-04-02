import threading

_local = threading.local()


def set_current_ip(ip: str):
    _local.ip = ip


def get_current_ip():
    return getattr(_local, 'ip', None)
