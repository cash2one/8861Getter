import sys
import os
from global_conf import thread_safe_mode
try:
    import thread
    import threading
except ImportError:
    thread = None

if thread_safe_mode and thread:
    _lock = threading.RLock()
else:
    _lock = None

def acquireLock():
    """
    Acquire the module-level lock for serializing access to shared data.

    This should be released with _releaseLock().
    """
    if _lock:
        _lock.acquire()

def releaseLock():
    """
    Release the module-level lock acquired by calling _acquireLock().
    """
    if _lock:
        _lock.release()

def genKey():
    """
    gen the process info
    Returns:

    """
    key = "default"
    if thread:
        threadid = thread.get_ident()
        threadName = threading.current_thread().name
    else:
        threadid = ""
        threadName = ""
    processName = 'Main'
    mp = sys.modules.get('multiprocessing')
    if mp is not None:
        # Errors may occur if multiprocessing has not finished loading
        # yet - e.g. if a custom import hook causes third-party code
        # to run when multiprocessing calls import. See issue 8200
        # for an example
        try:
            processName = mp.current_process().name
        except StandardError:
            pass
    if  hasattr(os, 'getpid'):
        processId = os.getpid()
    else:
        processId = ""
    return ("%s_%s_%s_%s") % (str(processId), processName, threadid, threadName )