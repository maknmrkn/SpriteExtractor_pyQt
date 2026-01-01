from PyQt6.QtWidgets import QFileDialog, QMessageBox


def get_directory(parent=None, title="Select Directory"):
    """Open dialog to select a directory."""
    return QFileDialog.getExistingDirectory(parent, title)


def get_save_directory(parent=None):
    """Prompt user to select output directory."""
    return get_directory(parent, "Save Frames To")


def show_info(parent, title, message):
    """Show an information message box."""
    QMessageBox.information(parent, title, message)


def show_warning(parent, title, message):
"""Show a warning message box."""
    QMessageBox.warning(parent, title, message)