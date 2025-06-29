import threading
import time

def set_timeout(func, timeout):
    result = [None]
    exception = [None]

    def target():
        try:
            result[0] = func()
        except Exception as e:
            exception[0] = e

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        return None, "Timeout"
    elif exception[0]:
        return exception[0]
    else:
        return result[0], None
