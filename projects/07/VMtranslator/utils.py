def log(*args, **kwargs):
    print(*args, **kwargs)


def log_info(*args, **kwargs):
    print('[Info ]:', *args, **kwargs)


def log_debug(*args, **kwargs):
    print('[Debug]:', *args, **kwargs)


def log_error(*args, **kwargs):
    print('[Error]:', *args, **kwargs)
