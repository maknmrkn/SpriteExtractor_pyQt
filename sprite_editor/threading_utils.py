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
        Create a Worker configured to run the given function in a background thread and to emit progress, finished, and error signals.
        
        This initializes the worker, stores the target function and its arguments, creates a WorkerSignals instance accessible via `self.signals`, and injects a `progress_callback` keyword argument bound to `self.signals.progress` so the target function can report progress.
        
        Parameters:
        	fn (callable): The function to execute when the worker runs.
        	*args: Positional arguments to pass to `fn`.
        	**kwargs: Keyword arguments to pass to `fn`; a `progress_callback` key will be added/overwritten and set to the worker's progress signal.
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
        Execute the stored callable with its provided positional and keyword arguments and emit appropriate worker signals.
        
        On successful execution emits the `finished` signal with the callable's return value. If an exception is raised, logs the error and emits the `error` signal with a tuple containing the exception type, the exception instance, and the formatted traceback string.
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