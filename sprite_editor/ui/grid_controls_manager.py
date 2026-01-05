from PyQt6.QtWidgets import QColorDialog
from PyQt6.QtGui import QColor


class GridControlsManager:
    """
    Manages grid and UI controls functionality for the main window.
    """
    def __init__(self, main_window):
        self.main_window = main_window

    def _update_grid_color_button(self, color: QColor):
        """
        Update the grid color control and apply the color to the canvas.
        
        Parameters:
            color (QColor): The color to use for the grid; updates the grid color button's appearance and sets the canvas's grid color, then refreshes the canvas display.
        """
        self.main_window.grid_color_button.setStyleSheet(f"background-color: {color.name()}; color: {'black' if color.lightness() > 128 else 'white'};")
        self.main_window.canvas.grid_color = color
        self.main_window.canvas.update_display()

    def _update_bg_color_button(self, color: QColor):
        """
        Update the background-color button's appearance and apply the chosen color to the canvas.
        
        Parameters:
            color (QColor): New background color; this updates the button's background and text color for legibility, sets the canvas background_color, and refreshes the canvas display.
        """
        self.main_window.bg_color_button.setStyleSheet(f"background-color: {color.name()}; color: {'black' if color.lightness() > 128 else 'white'};")
        self.main_window.canvas.background_color = color
        self.main_window.canvas.update_display()

    def _on_choose_grid_color(self):
        """
        Open a color picker and apply the selected color to the canvas grid.
        
        If the user selects a valid color, update the grid color button and the canvas grid color via the update helper.
        """
        color = QColorDialog.getColor(self.main_window.canvas.grid_color, self.main_window, "Choose Grid Color")
        if color.isValid():
            self._update_grid_color_button(color)

    def _on_choose_bg_color(self):
        """
        Open a color picker to choose a canvas background color and apply it if valid.
        
        If the user selects a valid color, update the background color button and the canvas background.
        """
        color = QColorDialog.getColor(self.main_window.canvas.background_color, self.main_window, "Choose Background Color")
        if color.isValid():
            self._update_bg_color_button(color)

    def _on_line_style_changed(self, text):
        """
        Set the canvas grid line style and refresh the display.
        
        Parameters:
            text (str): The name of the line style to apply (e.g., "Solid", "Dotted").
        """
        self.main_window.canvas.line_style = text
        self.main_window.canvas.update_display()

    def _on_grid_toggled(self, checked):
        """
        Enable or disable the canvas grid and refresh the canvas display.
        
        Parameters:
            checked (bool): True to show the grid, False to hide it.
        """
        self.main_window.canvas.show_grid = checked
        self.main_window.canvas.update_display()

    def _on_grid_width_changed(self, value):
        """
        Set the canvas grid cell width and refresh the canvas display.
        
        Parameters:
            value (int): New grid cell width in pixels.
        """
        self.main_window.canvas.grid_width = value
        self.main_window.canvas.update_display()

    def _on_grid_height_changed(self, value):
        """
        Set the canvas grid cell height and refresh the canvas display.
        
        Parameters:
            value (int): New grid cell height in pixels.
        """
        self.main_window.canvas.grid_height = value
        self.main_window.canvas.update_display()

    def _on_padding_x_changed(self, value):
        """
        Set the horizontal padding between grid cells on the canvas and refresh the view.
        
        Parameters:
            value (int): New horizontal padding in pixels to apply between grid cells.
        """
        self.main_window.canvas.padding_x = value
        self.main_window.canvas.update_display()

    def _on_padding_y_changed(self, value):
        """
        Update the canvas vertical grid padding and refresh the display.
        
        Parameters:
            value (int): New vertical padding value for the grid.
        """
        self.main_window.canvas.padding_y = value
        self.main_window.canvas.update_display()

    def _on_spacing_x_changed(self, value):
        """
        Update the canvas horizontal grid spacing and refresh the display.
        
        Parameters:
            value (int): New horizontal spacing in pixels between grid cells.
        """
        self.main_window.canvas.spacing_x = value
        self.main_window.canvas.update_display()

    def _on_spacing_y_changed(self, value):
        """
        Set the vertical grid spacing for the canvas and refresh the display.
        
        Parameters:
            value (int): New vertical spacing (in pixels) between grid cells.
        """
        self.main_window.canvas.spacing_y = value
        self.main_window.canvas.update_display()