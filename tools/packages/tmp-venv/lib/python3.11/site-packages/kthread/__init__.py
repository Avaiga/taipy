import ctypes
import inspect
# python 2/3 switch
try:
    import thread
except ImportError:
    import _thread as thread
import threading

name = "kthread"

def _async_raise(tid, exctype):
    """Raises the exception, causing the thread to exit"""
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("Invalid thread ID")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble, 
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
        raise SystemError("PyThreadState_SetAsyncExc failed")

class KThread(threading.Thread):
    """Killable thread.  See terminate() for details"""
    def _get_my_tid(self):
        """Determines the instance's thread ID"""
        if not self.is_alive():
            raise threading.ThreadError("Thread is not active")
        
        # do we have it cached?
        if hasattr(self, "_thread_id"):
            return self._thread_id
        
        # no, look for it in the _active dict
        for tid, tobj in threading._active.items():
            if tobj is self:
                self._thread_id = tid
                return tid
        
        raise AssertionError("Could not determine the thread's ID")
    
    def raise_exc(self, exctype):
        """raises the given exception type in the context of this thread"""
        _async_raise(self._get_my_tid(), exctype)
    
    def terminate(self):
        """raises SystemExit in the context of the given thread, which should 
        cause the thread to exit silently (unless caught)"""
        # WARNING: using terminate(), kill(), or exit() can introduce instability in your programs
        # It is worth noting that terminate() will NOT work if the thread in question is blocked by a syscall (accept(), recv(), etc.)
        self.raise_exc(SystemExit)

    # alias functions
    def kill(self):
        self.terminate()
        
    def exit(self):
        self.terminate()