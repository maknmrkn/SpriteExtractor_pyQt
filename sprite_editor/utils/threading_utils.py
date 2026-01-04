from PyQt6.QtCore import QObject, QRunnable, pyqtSignal
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
        Create a Worker that will run the given callable in a background thread.
        
        Stores the callable and its positional and keyword arguments on the instance, creates a WorkerSignals object as `self.signals`, and injects a `progress_callback` entry into `self.kwargs` that is bound to `self.signals.progress` so the target callable can emit progress updates.
        
        Parameters:
            fn (callable): The function to execute in the worker thread.
            *args: Positional arguments to pass to `fn`.
            **kwargs: Keyword arguments to pass to `fn`. Will be mutated to include a
                `progress_callback` key referencing `self.signals.progress`.
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
        Execute the stored callable with the worker's arguments and emit completion or error signals.
        
        On successful completion, emits the worker's `finished` signal with the callable's return value. If an exception is raised, logs the traceback and emits the worker's `error` signal with a tuple `(exception type, exception instance, formatted traceback)`.
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
