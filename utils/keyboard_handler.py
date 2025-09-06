# utils/keyboard_handler.py
"""
Keyboard shortcuts handler
"""

import tkinter as tk
from typing import Dict, Any, Callable, Optional

class KeyboardHandler:
    """
    Manages keyboard shortcuts and hotkeys
    """
    
    def __init__(self, root: tk.Tk, config: Dict[str, Any] = None):
        self.root = root
        self.config = config or {}
        
        # Keyboard shortcuts registry
        self.shortcuts: Dict[str, Dict[str, Any]] = {}
        
        # Default shortcuts
        self.default_shortcuts = {
            # Playback Controls
            '<space>': {'name': 'toggle_play_pause', 'description': 'Toggle play/pause'},
            '<Left>': {'name': 'frame_backward', 'description': 'Frame backward'},
            '<Right>': {'name': 'frame_forward', 'description': 'Frame forward'},
            '<Home>': {'name': 'goto_beginning', 'description': 'Go to beginning'},
            '<End>': {'name': 'goto_end', 'description': 'Go to end'},
            '<Up>': {'name': 'volume_up', 'description': 'Volume up'},
            '<Down>': {'name': 'volume_down', 'description': 'Volume down'},
            
            # Editing
            '<i>': {'name': 'set_in_point', 'description': 'Set in point'},
            '<o>': {'name': 'set_out_point', 'description': 'Set out point'},
            '<Control-z>': {'name': 'undo', 'description': 'Undo'},
            '<Control-y>': {'name': 'redo', 'description': 'Redo'},
            '<Delete>': {'name': 'delete_selected', 'description': 'Delete selected'},
            '<BackSpace>': {'name': 'delete_selected', 'description': 'Delete selected'},
            
            # Application
            '<Control-o>': {'name': 'open_file', 'description': 'Open file'},
            '<Control-s>': {'name': 'save_project', 'description': 'Save project'},
            '<Control-Shift-s>': {'name': 'save_project_as', 'description': 'Save project as'},
            '<Control-n>': {'name': 'new_project', 'description': 'New project'},
            '<Control-q>': {'name': 'quit_application', 'description': 'Quit application'},
            '<Control-w>': {'name': 'close_window', 'description': 'Close window'},
            
            # View
            '<F1>': {'name': 'show_help', 'description': 'Show help'},
            '<F2>': {'name': 'toggle_fullscreen', 'description': 'Toggle fullscreen'},
            '<F5>': {'name': 'refresh', 'description': 'Refresh'},
            '<F11>': {'name': 'toggle_fullscreen', 'description': 'Toggle fullscreen'},
            '<Control-plus>': {'name': 'zoom_in', 'description': 'Zoom in'},
            '<Control-minus>': {'name': 'zoom_out', 'description': 'Zoom out'},
            '<Control-0>': {'name': 'reset_zoom', 'description': 'Reset zoom'},
            
            # Timeline
            '<Control-Left>': {'name': 'seek_backward', 'description': 'Seek backward'},
            '<Control-Right>': {'name': 'seek_forward', 'description': 'Seek forward'},
            '<Shift-Left>': {'name': 'seek_backward_fast', 'description': 'Seek backward fast'},
            '<Shift-Right>': {'name': 'seek_forward_fast', 'description': 'Seek forward fast'},
            
            # Markers
            '<m>': {'name': 'add_marker', 'description': 'Add marker'},
            '<Shift-m>': {'name': 'clear_markers', 'description': 'Clear markers'},
            
            # Selection
            '<Control-a>': {'name': 'select_all', 'description': 'Select all'},
            '<Control-d>': {'name': 'deselect_all', 'description': 'Deselect all'},
            '<Control-i>': {'name': 'invert_selection', 'description': 'Invert selection'},
        }
        
        # Load shortcuts from config
        self.load_shortcuts()
        
        # Register default shortcuts
        self.register_default_shortcuts()
    
    def load_shortcuts(self):
        """Load shortcuts from configuration"""
        custom_shortcuts = self.config.get('keyboard_shortcuts', {})
        
        # Update shortcuts with custom ones
        for key, shortcut_info in custom_shortcuts.items():
            if isinstance(shortcut_info, dict):
                self.shortcuts[key] = shortcut_info
            else:
                # Handle simple format: {'<Control-s>': 'save_project'}
                self.shortcuts[key] = {'name': shortcut_info, 'description': ''}
    
    def register_default_shortcuts(self):
        """Register default keyboard shortcuts"""
        for key, shortcut_info in self.default_shortcuts.items():
            if key not in self.shortcuts:
                self.shortcuts[key] = shortcut_info.copy()
    
    def register_shortcut(self, key: str, name: str, callback: Callable, 
                          description: str = ""):
        """
        Register a keyboard shortcut
        
        Args:
            key: Key combination (e.g., '<Control-s>')
            name: Shortcut name
            callback: Callback function
            description: Optional description
        """
        self.shortcuts[key] = {
            'name': name,
            'callback': callback,
            'description': description
        }
        
        # Bind the shortcut
        self.root.bind(key, callback)
    
    def unregister_shortcut(self, key: str):
        """
        Unregister a keyboard shortcut
        
        Args:
            key: Key combination to unregister
        """
        if key in self.shortcuts:
            del self.shortcuts[key]
            self.root.unbind(key)
    
    def get_shortcut(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get shortcut information
        
        Args:
            key: Key combination
            
        Returns:
            Shortcut information dictionary or None
        """
        return self.shortcuts.get(key)
    
    def get_shortcut_by_name(self, name: str) -> Optional[str]:
        """
        Get key combination by shortcut name
        
        Args:
            name: Shortcut name
            
        Returns:
            Key combination or None
        """
        for key, shortcut_info in self.shortcuts.items():
            if shortcut_info.get('name') == name:
                return key
        return None
    
    def get_all_shortcuts(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered shortcuts
        
        Returns:
            Dictionary of all shortcuts
        """
        return self.shortcuts.copy()
    
    def trigger_shortcut(self, name: str, event: tk.Event = None) -> bool:
        """
        Trigger shortcut by name
        
        Args:
            name: Shortcut name
            event: Optional event object
            
        Returns:
            True if shortcut was triggered
        """
        key = self.get_shortcut_by_name(name)
        if key:
            shortcut_info = self.shortcuts.get(key)
            if shortcut_info and 'callback' in shortcut_info:
                shortcut_info['callback'](event)
                return True
        return False
    
    def is_modifier_key(self, key: str) -> bool:
        """
        Check if key is a modifier key
        
        Args:
            key: Key name
            
        Returns:
            True if key is a modifier
        """
        modifier_keys = {'Control', 'Shift', 'Alt', 'Meta', 'Command'}
        return key in modifier_keys
    
    def format_key_combination(self, key: str) -> str:
        """
        Format key combination for display
        
        Args:
            key: Key combination (e.g., '<Control-s>')
            
        Returns:
            Formatted string (e.g., 'Ctrl+S')
        """
        # Remove angle brackets
        key = key.strip('<>')
        
        # Split into parts
        parts = key.split('-')
        
        # Format each part
        formatted_parts = []
        for part in parts:
            if part == 'Control':
                formatted_parts.append('Ctrl')
            elif part == 'Shift':
                formatted_parts.append('Shift')
            elif part == 'Alt':
                formatted_parts.append('Alt')
            elif part == 'Meta' or part == 'Command':
                formatted_parts.append('Cmd')
            else:
                # Capitalize single letters
                if len(part) == 1:
                    formatted_parts.append(part.upper())
                else:
                    formatted_parts.append(part.capitalize())
        
        return '+'.join(formatted_parts)
    
    def get_shortcuts_summary(self) -> str:
        """
        Get formatted summary of all shortcuts
        
        Returns:
            Formatted string with all shortcuts
        """
        summary = "Keyboard Shortcuts:\n"
        summary += "=" * 50 + "\n\n"
        
        # Group shortcuts by category
        categories = {
            'Playback': ['toggle_play_pause', 'frame_backward', 'frame_forward', 
                       'goto_beginning', 'goto_end', 'volume_up', 'volume_down'],
            'Editing': ['set_in_point', 'set_out_point', 'undo', 'redo', 
                       'delete_selected'],
            'Application': ['open_file', 'save_project', 'save_project_as', 
                           'new_project', 'quit_application', 'close_window'],
            'View': ['show_help', 'toggle_fullscreen', 'refresh', 'zoom_in', 
                    'zoom_out', 'reset_zoom'],
            'Timeline': ['seek_backward', 'seek_forward', 'seek_backward_fast', 
                        'seek_forward_fast', 'add_marker', 'clear_markers'],
            'Selection': ['select_all', 'deselect_all', 'invert_selection']
        }
        
        for category, shortcut_names in categories.items():
            summary += f"{category}:\n"
            summary += "-" * 20 + "\n"
            
            for name in shortcut_names:
                key = self.get_shortcut_by_name(name)
                if key:
                    shortcut_info = self.shortcuts.get(key, {})
                    description = shortcut_info.get('description', '')
                    formatted_key = self.format_key_combination(key)
                    summary += f"  {formatted_key:<20} - {description}\n"
            
            summary += "\n"
        
        return summary
    
    def show_shortcuts_help(self):
        """Show shortcuts help dialog"""
        import tkinter.messagebox as messagebox
        
        help_text = self.get_shortcuts_summary()
        messagebox.showinfo("Keyboard Shortcuts", help_text)
    
    def save_shortcuts_config(self, filepath: str):
        """
        Save shortcuts configuration to file
        
        Args:
            filepath: Path to save configuration
        """
        import json
        
        # Prepare data for saving
        config_data = {}
        for key, shortcut_info in self.shortcuts.items():
            if 'name' in shortcut_info:
                config_data[key] = shortcut_info['name']
        
        try:
            with open(filepath, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            print(f"Failed to save shortcuts config: {e}")
    
    def load_shortcuts_config(self, filepath: str):
        """
        Load shortcuts configuration from file
        
        Args:
            filepath: Path to configuration file
        """
        import json
        
        try:
            with open(filepath, 'r') as f:
                config_data = json.load(f)
            
            # Update shortcuts
            for key, name in config_data.items():
                if key in self.shortcuts:
                    self.shortcuts[key]['name'] = name
        except Exception as e:
            print(f"Failed to load shortcuts config: {e}")

# Test the keyboard_handler
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Keyboard Handler Test")
    root.geometry("400x300")
    
    # Create keyboard handler
    keyboard_handler = KeyboardHandler(root)
    
    # Register some test shortcuts
    def test_callback(event=None):
        print("Test shortcut triggered!")
    
    def show_shortcuts(event=None):
        keyboard_handler.show_shortcuts_help()
    
    keyboard_handler.register_shortcut(
        '<Control-t>', 
        'test_shortcut', 
        test_callback, 
        'Test shortcut'
    )
    
    keyboard_handler.register_shortcut(
        '<F1>', 
        'show_help', 
        show_shortcuts, 
        'Show help'
    )
    
    # Create test UI
    label = tk.Label(root, text="Press Ctrl+T to test shortcut\nPress F1 to show help", 
                     font=('Arial', 12))
    label.pack(expand=True)
    
    # Print all shortcuts
    print("All shortcuts:")
    for key, info in keyboard_handler.get_all_shortcuts().items():
        formatted_key = keyboard_handler.format_key_combination(key)
        print(f"{formatted_key}: {info.get('name', 'Unknown')}")
    
    root.mainloop()