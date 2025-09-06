# gui/theme_manager.py
"""
Theme management for Purple Blackhole theme
"""
import tkinter as tk
from tkinter import ttk
import json
import os
import logging
from typing import Dict, Any, Optional

class ThemeManager:
    """
    Manages application themes and styling
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.current_theme = self.config.get('theme', {})
        
        # Setup logger terlebih dahulu
        self.logger = logging.getLogger(__name__)
        
        # Default Purple Blackhole theme
        self.default_theme = {
            'name': 'Purple Blackhole',
            'bg_primary': '#1a0d26',      # Deep purple-black
            'bg_secondary': '#2d1b3d',    # Lighter purple-black
            'accent_primary': '#6b46c1',  # Purple
            'accent_secondary': '#a855f7', # Light purple
            'accent_tertiary': '#ec4899',  # Pink-purple
            'text_primary': '#f8fafc',     # Light gray
            'text_secondary': '#cbd5e1',   # Medium gray
            'border': '#4c1d95',          # Purple border
            'hover': '#7c3aed',           # Hover purple
            'success': '#10b981',         # Green
            'error': '#ef4444',           # Red
            'warning': '#f59e0b'          # Orange
        }
        
        # Merge with config theme
        self.theme = {**self.default_theme, **self.current_theme}
        
        # Configure styles
        self.style = ttk.Style()
        self.configure_styles()
        
        self.logger.info("ThemeManager initialized")
    
    def configure_styles(self):
        """Configure ttk styles with theme colors"""
        # Configure root window
        self.style.configure('TFrame', background=self.theme['bg_primary'])
        self.style.configure('TLabel', background=self.theme['bg_primary'], 
                           foreground=self.theme['text_primary'])
        self.style.configure('TButton', background=self.theme['accent_primary'],
                           foreground=self.theme['text_primary'])
        self.style.map('TButton', 
                     background=[('active', self.theme['hover'])])
        
        # Configure notebook (tabs)
        self.style.configure('TNotebook', background=self.theme['bg_primary'],
                           borderwidth=0)
        self.style.configure('TNotebook.Tab', background=self.theme['bg_secondary'],
                           foreground=self.theme['text_primary'],
                           padding=[12, 8])
        self.style.map('TNotebook.Tab',
                     background=[('selected', self.theme['accent_primary']),
                               ('active', self.theme['hover'])])
        
        # Configure progress bar
        self.style.configure('TProgressbar', background=self.theme['accent_primary'],
                           troughcolor=self.theme['bg_secondary'])
        
        # Configure scale (slider)
        self.style.configure('TScale', background=self.theme['bg_primary'],
                           troughcolor=self.theme['bg_secondary'],
                           lightcolor=self.theme['accent_primary'],
                           darkcolor=self.theme['accent_secondary'])
        
        # Configure entry
        self.style.configure('TEntry', fieldbackground=self.theme['bg_secondary'],
                           foreground=self.theme['text_primary'],
                           borderwidth=1)
        
        # Configure combobox
        self.style.configure('TCombobox', fieldbackground=self.theme['bg_secondary'],
                           foreground=self.theme['text_primary'],
                           background=self.theme['accent_primary'])
        
        # Configure checkbutton
        self.style.configure('TCheckbutton', background=self.theme['bg_primary'],
                           foreground=self.theme['text_primary'])
        
        # Configure radiobutton
        self.style.configure('TRadiobutton', background=self.theme['bg_primary'],
                           foreground=self.theme['text_primary'])
    
    def get_color(self, color_name: str) -> str:
        """Get a theme color by name"""
        return self.theme.get(color_name, '#000000')
    
    def apply_theme(self, root: tk.Tk):
        """Apply theme to root window"""
        root.configure(bg=self.theme['bg_primary'])
        
        # Configure standard widgets
        root.option_add('*background', self.theme['bg_primary'])
        root.option_add('*foreground', self.theme['text_primary'])
        root.option_add('*selectBackground', self.theme['accent_primary'])
        root.option_add('*selectForeground', self.theme['text_primary'])
    
    def create_custom_frame(self, parent, style: str = 'TFrame', padding: int = 0) -> ttk.Frame:
        """
        Create a custom styled frame with optional padding.
        (Refactored to use standard padding)
        
        Args:
            parent: Parent widget
            style: Style name for the frame
            padding: Padding in pixels
            
        Returns:
            Styled frame widget
        """
        # The complex container logic was breaking the layout.
        # Using the built-in padding mechanism is much more stable.
        frame = ttk.Frame(parent, style=style, padding=padding)
        return frame
    
    def create_custom_button(self, parent, text: str, command=None, 
                           style: str = 'TButton', width: int = None) -> ttk.Button:
        """
        Create a custom styled button
        
        Args:
            parent: Parent widget
            text: Button text
            command: Button command
            style: Style name for the button
            width: Button width in characters
            
        Returns:
            Styled button widget
        """
        # Define custom button style
        self.style.configure(style, background=self.theme['accent_primary'],
                           foreground=self.theme['text_primary'],
                           padding=[12, 8])
        self.style.map(style,
                     background=[('active', self.theme['hover'])])
        
        button = ttk.Button(parent, text=text, command=command, style=style)
        
        if width:
            button.configure(width=width)
        
        return button
    
    def create_custom_label(self, parent, text: str, 
                          style: str = 'TLabel',
                          font: tuple = None) -> ttk.Label:
        """
        Create a custom styled label
        
        Args:
            parent: Parent widget
            text: Label text
            style: Style name for the label
            font: Font tuple (family, size, weight)
            
        Returns:
            Styled label widget
        """
        return ttk.Label(parent, text=text, style=style,
                        font=font or ('Arial', 10))
    
    def create_custom_progressbar(self, parent, style: str = 'TProgressbar', 
                                variable=None, length: int = 200) -> ttk.Progressbar:
        """
        Create a custom styled progress bar
        
        Args:
            parent: Parent widget
            style: Style name for the progress bar
            variable: Variable to bind to progress bar
            length: Length of progress bar in pixels
            
        Returns:
            Styled progress bar widget
        """
        # Define custom progress bar style
        self.style.configure(style, background=self.theme['accent_primary'],
                           troughcolor=self.theme['bg_secondary'])
        
        return ttk.Progressbar(parent, style=style, variable=variable, length=length)
    
    def create_custom_scale(self, parent, style: str = 'TScale', 
                          from_=0, to=100, variable=None, 
                          orient='horizontal', length=200) -> ttk.Scale:
        """
        Create a custom styled scale/slider
        
        Args:
            parent: Parent widget
            style: Style name for the scale
            from_: Minimum value
            to: Maximum value
            variable: Variable to bind to scale
            orient: Orientation ('horizontal' or 'vertical')
            length: Length of scale in pixels
            
        Returns:
            Styled scale widget
        """
        # Define custom scale style
        self.style.configure(style, background=self.theme['bg_primary'],
                           troughcolor=self.theme['bg_secondary'],
                           lightcolor=self.theme['accent_primary'],
                           darkcolor=self.theme['accent_secondary'])
        
        return ttk.Scale(parent, style=style, from_=from_, to=to, 
                        variable=variable, orient=orient, length=length)
    
    def create_custom_entry(self, parent, style: str = 'TEntry', 
                          width: int = None) -> ttk.Entry:
        """
        Create a custom styled entry
        
        Args:
            parent: Parent widget
            style: Style name for the entry
            width: Entry width in characters
            
        Returns:
            Styled entry widget
        """
        # Define custom entry style
        self.style.configure(style, fieldbackground=self.theme['bg_secondary'],
                           foreground=self.theme['text_primary'],
                           borderwidth=1)
        
        entry = ttk.Entry(parent, style=style)
        
        if width:
            entry.configure(width=width)
        
        return entry
    
    def create_custom_combobox(self, parent, values: list = None, 
                             style: str = 'TCombobox', width: int = None) -> ttk.Combobox:
        """
        Create a custom styled combobox
        
        Args:
            parent: Parent widget
            values: List of values for combobox
            style: Style name for the combobox
            width: Combobox width in characters
            
        Returns:
            Styled combobox widget
        """
        # Define custom combobox style
        self.style.configure(style, fieldbackground=self.theme['bg_secondary'],
                           foreground=self.theme['text_primary'],
                           background=self.theme['accent_primary'])
        
        combobox = ttk.Combobox(parent, values=values or [], style=style)
        
        if width:
            combobox.configure(width=width)
        
        return combobox
    
    def create_custom_notebook(self, parent, style: str = 'TNotebook') -> ttk.Notebook:
        """
        Create a custom styled notebook
        
        Args:
            parent: Parent widget
            style: Style name for the notebook
            
        Returns:
            Styled notebook widget
        """
        # Define custom notebook style
        self.style.configure(style, background=self.theme['bg_primary'],
                           borderwidth=0)
        self.style.configure(f'{style}.Tab', background=self.theme['bg_secondary'],
                           foreground=self.theme['text_primary'],
                           padding=[12, 8])
        self.style.map(f'{style}.Tab',
                     background=[('selected', self.theme['accent_primary']),
                               ('active', self.theme['hover'])])
        
        return ttk.Notebook(parent, style=style)
    
    def create_custom_checkbutton(self, parent, text: str, 
                                style: str = 'TCheckbutton', 
                                variable=None, **kwargs) -> ttk.Checkbutton:
        """
        Create a custom styled checkbutton
        
        Args:
            parent: Parent widget
            text: Checkbutton text
            style: Style name for the checkbutton
            variable: Variable to bind to checkbutton
            **kwargs: Additional keyword arguments
            
        Returns:
            Styled checkbutton widget
        """
        # Define custom checkbutton style
        self.style.configure(style, background=self.theme['bg_primary'],
                           foreground=self.theme['text_primary'])
        
        # Create checkbutton with variable support
        if variable is not None:
            checkbutton = ttk.Checkbutton(parent, text=text, style=style, 
                                        variable=variable, **kwargs)
        else:
            checkbutton = ttk.Checkbutton(parent, text=text, style=style, **kwargs)
        
        return checkbutton
    
    def create_custom_radiobutton(self, parent, text: str, 
                                style: str = 'TRadiobutton', 
                                variable=None, value=None, **kwargs) -> ttk.Radiobutton:
        """
        Create a custom styled radiobutton
        
        Args:
            parent: Parent widget
            text: Radiobutton text
            style: Style name for the radiobutton
            variable: Variable to bind to radiobutton
            value: Value for this radiobutton
            **kwargs: Additional keyword arguments
            
        Returns:
            Styled radiobutton widget
        """
        # Define custom radiobutton style
        self.style.configure(style, background=self.theme['bg_primary'],
                           foreground=self.theme['text_primary'])
        
        # Create radiobutton with variable and value support
        if variable is not None and value is not None:
            radiobutton = ttk.Radiobutton(parent, text=text, style=style,
                                        variable=variable, value=value, **kwargs)
        elif variable is not None:
            radiobutton = ttk.Radiobutton(parent, text=text, style=style,
                                        variable=variable, **kwargs)
        else:
            radiobutton = ttk.Radiobutton(parent, text=text, style=style, **kwargs)
        
        return radiobutton
    
    def save_theme(self, filepath: str):
        """Save current theme to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.theme, f, indent=2)
            self.logger.info(f"Theme saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save theme: {e}")
    
    def load_theme(self, filepath: str):
        """Load theme from file"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    loaded_theme = json.load(f)
                    self.theme = {**self.default_theme, **loaded_theme}
                    self.configure_styles()
                self.logger.info(f"Theme loaded from {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to load theme: {e}")
    
    def reset_to_default(self):
        """Reset theme to default"""
        self.theme = self.default_theme.copy()
        self.configure_styles()
        self.logger.info("Theme reset to default")
    
    def get_theme_info(self) -> Dict[str, Any]:
        """Get theme information"""
        return {
            'name': self.theme.get('name', 'Unknown'),
            'colors': self.theme,
            'is_default': self.theme == self.default_theme
        }

# Test the theme_manager
if __name__ == "__main__":
    # Configure logging for test
    logging.basicConfig(level=logging.INFO)
    
    root = tk.Tk()
    root.title("Theme Manager Test")
    root.geometry("400x300")
    
    theme_manager = ThemeManager()
    theme_manager.apply_theme(root)
    
    # Create test widgets
    frame = theme_manager.create_custom_frame(root, padding=20)
    frame.pack(fill='both', expand=True)
    
    label = theme_manager.create_custom_label(
        frame, 
        "Purple Blackhole Theme", 
        font=('Arial', 14, 'bold')
    )
    label.pack(pady=10)
    
    button = theme_manager.create_custom_button(frame, "Test Button")
    button.pack(pady=5)
    
    progress = theme_manager.create_custom_progressbar(frame, length=200)
    progress.pack(pady=5)
    progress['value'] = 65
    
    scale = theme_manager.create_custom_scale(frame, from_=0, to=100, length=200)
    scale.pack(pady=5)
    scale.set(50)
    
    entry = theme_manager.create_custom_entry(frame, width=30)
    entry.pack(pady=5)
    entry.insert(0, "Test entry")
    
    combobox = theme_manager.create_custom_combobox(frame, values=['Option 1', 'Option 2'])
    combobox.pack(pady=5)
    combobox.set('Option 1')
    
    # Test checkbutton with variable
    test_var = tk.BooleanVar(value=True)
    checkbutton = theme_manager.create_custom_checkbutton(frame, "Test Checkbutton", variable=test_var)
    checkbutton.pack(pady=5)
    
    # Test radiobutton with variable
    radio_var = tk.StringVar(value="option1")
    radiobutton1 = theme_manager.create_custom_radiobutton(frame, "Option 1", variable=radio_var, value="option1")
    radiobutton1.pack(pady=2)
    radiobutton2 = theme_manager.create_custom_radiobutton(frame, "Option 2", variable=radio_var, value="option2")
    radiobutton2.pack(pady=2)
    
    root.mainloop()