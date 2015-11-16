"""Convenience classes to support Actor model of concurrency, backed by threads."""
import threading
from collections import namedtuple
import Queue as queue
import Tkinter as tk
import ttk

from components.messaging import Receiver

class InterruptableThread(object):
    """Interface class to support easier threading."""
    def __init__(self, name):
        super(InterruptableThread, self).__init__()
        self.__name = name
        self.__quit_flag = threading.Event()
        self.__thread = threading.Thread(target=self._run, name=name)

    def get_name(self):
        """Returns the name of the thread instance as specified during instantiation."""
        return self.__name

    # Threading
    def start(self):
        """Starts the thread."""
        self.__thread.start()
    def will_quit(self):
        """Checks whether the thread is supposed to quit."""
        return self.__quit_flag.is_set()
    def quit(self):
        """Quits and joins with the thread, if it's running."""
        self._quit_soon()
        self._wake()
        if self.__thread.is_alive():
            self.__thread.join()
    def _quit_soon(self):
        """Marks the flag that the thread will check to quit."""
        self.__quit_flag.set()

    # Abstract methods
    def _wake(self):
        """Wake the thread method, if it's sleeping, to signal it to prepare to quit."""
        pass
    def _run(self):
        """The function that will be run in a new thread."""
        pass

class Reactor(InterruptableThread, Receiver):
    """Models an event-driven thread that receives & handles Signals as messages."""
    def __init__(self, name):
        super(Reactor, self).__init__(name)

    # Implementation of parent abstract methods
    def _wake(self):
        """Wakes the thread to prepare it to quit."""
        self.send(None)
    def _run(self):
        """Runs as a thread."""
        self._run_pre()
        while not self.will_quit():
            signal = self._receive()
            if signal is not None:
                self._react(signal)
            else:
                self._quit_soon()
            self._received_done()
        self._run_post()

    # Abstract methods
    def _run_pre(self):
        """Executes before the thread starts. Useful for initialization."""
        pass
    def _run_post(self):
        """Executes after the thread ends. Useful for initialization."""
        pass

class GUIReactor(Receiver):
    """Runs and updates a TKinter root window based on received Signals.
    Has the same public semantics as InterruptableThreads, but the start method blocks
    the caller until the GUI exits.
    Has the same abstract method semantics as Reactors. Unlike Reactors, this
    must run in the main thread.
    """
    def __init__(self, name="GUI", update_interval=10):
        super(GUIReactor, self).__init__()
        self.__name = name
        self._root = tk.Tk()
        self.__initialize_theming()
        self.__update_interval = update_interval
    def __initialize_theming(self):
        style = ttk.Style()
        if "aqua" in style.theme_names():
            style.theme_use("aqua") # OS X
        elif "vista" in style.theme_names():
            style.theme_use("vista") # Windows
        else:
            style.theme_use("clam") # Linux
        self._root.style = style

    def get_name(self):
        """Returns the name of the thread instance as specified during instantiation."""
        return self.__name

    # Event loop
    def start(self):
        """Starts the GUI and blocks until the GUI quits.
        Because of how TKinter works, this should be called in the main thread."""
        self._run_pre()
        self._run()
        self._root.mainloop()
    def quit(self):
        """Quits the GUI and unblocks the thread that called the start method."""
        self._root.quit()
        self._run_post()
    def _run(self):
        """Reacts to any received signals and then sleeps for a bit."""
        self._react_all()
        self._root.after(self.__update_interval, self._run)

    # Abstract methods
    def _run_pre(self):
        """Executes before the GUI starts. Useful for initialization."""
        pass
    def _run_post(self):
        """Executes after the thread ends. Useful for initialization."""
        pass
