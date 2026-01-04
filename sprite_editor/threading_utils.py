from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, QMetaObject, Q_ARG
from PyQt6.QtWidgets import QMessageBox
import traceback
import logging


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    """
    finished = pyqtSignal(object)  # Signal emitted when task is finished, with result as parameter
    error = pyqtSignal(tuple)  # Signal emitted when an error occurs (exctype, value, traceback)
    progress = pyqtSignal(object)  # Signal emitted to report progress


class Worker(QRunnable):
    """
    Worker thread for executing tasks in the background.
    
    Inherits from QRunnable to handle worker thread setup, cleanup and management.
    """
    def __init__(self, fn, *args, **kwargs):
        """
        Initialize the worker with a function and its arguments.
        
        :param fn: The function to execute in the thread
        :param args: Arguments to pass to the function
        :param kwargs: Keyword arguments to pass to the function
        """
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    def run(self):
        """
        Initialize the runner function with passed args and kwargs.
        """
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception as e:
            # Log the exception
            logging.error(f"Error in background thread: {str(e)}")
            logging.error(traceback.format_exc())
            # Emit the error signal with exception info
            exctype, value = type(e), e
            self.signals.error.emit((exctype, value, traceback.format_exc()))