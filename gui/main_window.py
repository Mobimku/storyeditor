# gui/main_window.py
"""
Main application window - Simplified and Compatible Version
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import threading
import os
from typing import Dict, Any, Optional, Callable

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.theme_manager import ThemeManager
from gui.tab_editor import EditorTab
from gui.tab_compiler import CompilerTab
from utils.progress_tracker import ProgressTracker

class MainWindow:
    """
    Main application window with simplified responsive layout
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("FFmpeg Editor - Professional Video Processing")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 600)
        
        # Initialize theme manager
        self.theme_manager = ThemeManager(self.config)
        self.theme_manager.apply_theme(self.root)
        
        # Initialize progress tracker
        self.progress_tracker = ProgressTracker()
        
        # Application state
        self.current_file = None
        self.is_processing = False
        self.preview_widget = None
        
        # Setup UI components
        self.setup_ui()
        self.setup_keyboard_shortcuts()
        
        # Configure window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.logger.info("Main window initialized")
    
    def setup_ui(self):
        """Setup the main UI with grid layout"""
        # Configure main window grid
        self.root.grid_columnconfigure(1, weight=1)  # Center column expands
        self.root.grid_rowconfigure(1, weight=1)     # Main content row expands
        
        # Menu bar
        self.create_menu_bar()
        
        # Toolbar (row 0)
        self.create_toolbar()
        
        # Main content area (row 1) - using grid for better control
        self.create_main_content()
        
        # Status bar (row 2)
        self.create_status_bar()
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open File...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Import URL...", command=self.import_url, accelerator="Ctrl+I")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_application, accelerator="Ctrl+Q")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Reset Layout", command=self.reset_layout)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_help, accelerator="F1")
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_toolbar(self):
        """Create application toolbar"""
        toolbar_frame = ttk.Frame(self.root)
        toolbar_frame.grid(row=0, column=0, columnspan=3, sticky='ew', padx=5, pady=2)
        
        # File operations
        self.open_btn = self.theme_manager.create_custom_button(
            toolbar_frame, "📁 Open", command=self.open_file, width=8
        )
        self.open_btn.pack(side='left', padx=(0, 2))
        
        self.url_btn = self.theme_manager.create_custom_button(
            toolbar_frame, "🌐 URL", command=self.import_url, width=8
        )
        self.url_btn.pack(side='left', padx=(0, 2))
        
        # Separator
        ttk.Separator(toolbar_frame, orient='vertical').pack(side='left', fill='y', padx=5)
        
        # Playback controls
        self.play_btn = self.theme_manager.create_custom_button(
            toolbar_frame, "▶ Play", command=self.toggle_playback, width=8
        )
        self.play_btn.pack(side='left', padx=(0, 2))
        
        # Processing controls
        self.process_btn = self.theme_manager.create_custom_button(
            toolbar_frame, "🎬 Process", command=self.start_processing, width=10
        )
        self.process_btn.pack(side='left', padx=(0, 2))
        
        # Status indicator
        self.status_indicator = tk.Canvas(toolbar_frame, width=12, height=12, highlightthickness=0)
        self.status_indicator.pack(side='right', padx=5)
        self.update_status_indicator('ready')
    
    def create_main_content(self):
        """Create main content area with 3-column layout"""
        # Left panel (Media List) - column 0
        self.create_left_panel()
        
        # Center panel (Preview + Tabs) - column 1
        self.create_center_panel()
        
        # Right panel (Properties) - column 2
        self.create_right_panel()
    
    def create_left_panel(self):
        """Create left panel for media files"""
        left_frame = ttk.Frame(self.root)
        left_frame.grid(row=1, column=0, sticky='nsew', padx=(5, 2), pady=5)
        left_frame.grid_rowconfigure(1, weight=1)  # Media list expands
        
        # Title
        title_label = self.theme_manager.create_custom_label(
            left_frame, "📁 Project Media", font=('Arial', 11, 'bold')
        )
        title_label.grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        # Media list with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.grid(row=1, column=0, sticky='nsew')
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        # Listbox
        self.media_listbox = tk.Listbox(
            list_frame,
            bg=self.theme_manager.get_color('bg_secondary'),
            fg=self.theme_manager.get_color('text_primary'),
            selectbackground=self.theme_manager.get_color('accent_primary'),
            font=('Arial', 9),
            width=25
        )
        self.media_listbox.grid(row=0, column=0, sticky='nsew')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.media_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.media_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Bind events
        self.media_listbox.bind('<Double-Button-1>', self.on_media_double_click)
    
    def create_center_panel(self):
        """Create center panel for preview and timeline"""
        center_frame = ttk.Frame(self.root)
        center_frame.grid(row=1, column=1, sticky='nsew', padx=2, pady=5)
        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_rowconfigure(0, weight=3)  # Preview gets more space
        center_frame.grid_rowconfigure(1, weight=1)  # Tabs get less space
        
        # Preview area
        preview_frame = ttk.LabelFrame(center_frame, text="🎬 Video Preview", padding=10)
        preview_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 5))
        
        # Preview placeholder
        self.preview_container = ttk.Frame(preview_frame)
        self.preview_container.pack(fill='both', expand=True)
        
        self.preview_placeholder = self.theme_manager.create_custom_label(
            self.preview_container,
            "No video loaded\n\nClick '📁 Open' to load a video file\nor '🌐 URL' to import from web",
            font=('Arial', 12)
        )
        self.preview_placeholder.pack(expand=True)
        
        # Tabs area
        tabs_frame = ttk.Frame(center_frame)
        tabs_frame.grid(row=1, column=0, sticky='nsew')
        
        # Create notebook for tabs
        self.notebook = self.theme_manager.create_custom_notebook(tabs_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        try:
            self.editor_tab = EditorTab(self.notebook, self.theme_manager, self.config)
            self.compiler_tab = CompilerTab(self.notebook, self.theme_manager, self.config)
            
            self.notebook.add(self.editor_tab.frame, text="📝 Editor")
            self.notebook.add(self.compiler_tab.frame, text="🎬 Compiler")
        except Exception as e:
            self.logger.error(f"Failed to create tabs: {e}")
            # Create placeholder tabs
            placeholder_tab = ttk.Frame(self.notebook)
            placeholder_label = self.theme_manager.create_custom_label(
                placeholder_tab, f"Tab creation failed: {str(e)}", font=('Arial', 10)
            )
            placeholder_label.pack(expand=True)
            self.notebook.add(placeholder_tab, text="Error")
        
        # Try to integrate preview widget
        self.integrate_preview_widget()
    
    def create_right_panel(self):
        """Create right panel for properties"""
        right_frame = ttk.Frame(self.root)
        right_frame.grid(row=1, column=2, sticky='nsew', padx=(2, 5), pady=5)
        right_frame.grid_rowconfigure(1, weight=1)
        
        # Title
        title_label = self.theme_manager.create_custom_label(
            right_frame, "⚙️ Properties", font=('Arial', 11, 'bold')
        )
        title_label.grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        # Properties area
        props_frame = ttk.Frame(right_frame)
        props_frame.grid(row=1, column=0, sticky='nsew')
        
        # Color grading section
        color_frame = ttk.LabelFrame(props_frame, text="Color Grading", padding=5)
        color_frame.pack(fill='x', pady=(0, 5))
        
        preset_label = self.theme_manager.create_custom_label(color_frame, "Preset:")
        preset_label.pack(anchor='w')
        
        self.color_preset = self.theme_manager.create_custom_combobox(
            color_frame,
            values=["None", "Cinematic", "Vibrant", "Dramatic", "Natural"],
            width=15
        )
        self.color_preset.set("Cinematic")
        self.color_preset.pack(fill='x', pady=2)
        
        # Volume section
        volume_frame = ttk.LabelFrame(props_frame, text="Audio", padding=5)
        volume_frame.pack(fill='x', pady=(0, 5))
        
        volume_label = self.theme_manager.create_custom_label(volume_frame, "Volume:")
        volume_label.pack(anchor='w')
        
        self.volume_var = tk.DoubleVar(value=100.0)
        volume_scale = self.theme_manager.create_custom_scale(
            volume_frame,
            from_=0, to=200, variable=self.volume_var,
            orient='horizontal', length=150
        )
        volume_scale.pack(fill='x')
        
        self.volume_label_val = self.theme_manager.create_custom_label(volume_frame, "100%")
        self.volume_label_val.pack()
        
        # Bind volume updates
        self.volume_var.trace('w', self.update_volume_display)
    
    def create_status_bar(self):
        """Create status bar"""
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=2, column=0, columnspan=3, sticky='ew', padx=5, pady=2)
        
        # Status sections
        self.status_file = self.theme_manager.create_custom_label(
            status_frame, "No file loaded", font=('Arial', 9)
        )
        self.status_file.pack(side='left', padx=5)
        
        # Progress bar (initially hidden)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = self.theme_manager.create_custom_progressbar(
            status_frame,
            variable=self.progress_var,
            length=200
        )
        # Don't pack initially
        
        # Status message
        self.status_message = self.theme_manager.create_custom_label(
            status_frame, "Ready", font=('Arial', 9)
        )
        self.status_message.pack(side='right', padx=5)
    
    def integrate_preview_widget(self):
        """Try to integrate preview widget"""
        try:
            from gui.preview_widget import PreviewWidget
            
            # Remove placeholder
            if hasattr(self, 'preview_placeholder'):
                self.preview_placeholder.destroy()
            
            # Create preview widget
            self.preview_widget = PreviewWidget(
                self.preview_container,
                self.theme_manager,
                self.config
            )
            self.preview_widget.frame.pack(fill='both', expand=True)
            
            self.logger.info("Preview widget integrated successfully")
            
        except ImportError as e:
            self.logger.warning(f"Preview widget not available: {e}")
            # Keep placeholder
        except Exception as e:
            self.logger.error(f"Failed to integrate preview widget: {e}")
            # Keep placeholder
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-i>', lambda e: self.import_url())
        self.root.bind('<Control-q>', lambda e: self.quit_application())
        self.root.bind('<space>', lambda e: self.toggle_playback())
        self.root.bind('<F1>', lambda e: self.show_help())
        
        # Set focus to enable keyboard shortcuts
        self.root.focus_set()
    
    def update_status_indicator(self, status: str):
        """Update status indicator color"""
        colors = {
            'ready': self.theme_manager.get_color('success'),
            'processing': self.theme_manager.get_color('warning'),
            'error': self.theme_manager.get_color('error')
        }
        
        color = colors.get(status, colors['ready'])
        self.status_indicator.delete('all')
        self.status_indicator.create_oval(2, 2, 10, 10, fill=color, outline='')
    
    def update_volume_display(self, *args):
        """Update volume display"""
        volume = self.volume_var.get()
        self.volume_label_val.config(text=f"{volume:.0f}%")
    
    # File operations
    def open_file(self):
        """Open file dialog"""
        filetypes = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Open Video File",
            filetypes=filetypes
        )
        
        if filename:
            self.load_file(filename)
    
    def import_url(self):
        """Show URL import dialog"""
        url_dialog = tk.Toplevel(self.root)
        url_dialog.title("Import from URL")
        url_dialog.geometry("500x150")
        url_dialog.transient(self.root)
        url_dialog.grab_set()
        
        # Center dialog
        url_dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 100,
            self.root.winfo_rooty() + 100
        ))
        
        main_frame = ttk.Frame(url_dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # URL entry
        url_label = self.theme_manager.create_custom_label(main_frame, "Enter URL:")
        url_label.pack(anchor='w', pady=(0, 5))
        
        url_entry = self.theme_manager.create_custom_entry(main_frame, width=50)
        url_entry.pack(fill='x', pady=(0, 10))
        url_entry.focus()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        def download_url():
            url = url_entry.get().strip()
            if url:
                url_dialog.destroy()
                self.download_from_url(url)
            else:
                messagebox.showwarning("No URL", "Please enter a valid URL")
        
        download_btn = self.theme_manager.create_custom_button(
            button_frame, "Download", command=download_url
        )
        download_btn.pack(side='right', padx=(5, 0))
        
        cancel_btn = self.theme_manager.create_custom_button(
            button_frame, "Cancel", command=url_dialog.destroy
        )
        cancel_btn.pack(side='right')
        
        # Bind Enter key
        url_entry.bind('<Return>', lambda e: download_url())
    
    def load_file(self, filepath: str):
        """Load video file"""
        try:
            self.current_file = filepath
            filename = os.path.basename(filepath)
            
            # Update status
            self.status_file.config(text=f"Loaded: {filename}")
            self.update_status_indicator('ready')
            
            # Add to media list
            self.media_listbox.insert(tk.END, filename)
            
            # Load in preview widget if available
            if self.preview_widget:
                success = self.preview_widget.load_video(filepath)
                if not success:
                    messagebox.showerror("Error", f"Failed to load video: {filename}")
                    return
            
            self.logger.info(f"Loaded file: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to load file: {e}")
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def download_from_url(self, url: str):
        """Download video from URL (placeholder)"""
        self.update_status_indicator('processing')
        self.status_message.config(text="Downloading...")
        
        # Show progress bar
        self.progress_bar.pack(side='left', padx=10)
        
        # TODO: Implement actual URL download
        # For now, just simulate
        def simulate_download():
            for i in range(101):
                self.progress_var.set(i)
                self.root.update_idletasks()
                self.root.after(30)  # 30ms delay
            
            # Hide progress bar and update status
            self.progress_bar.pack_forget()
            self.progress_var.set(0)
            self.update_status_indicator('ready')
            self.status_message.config(text="Download completed")
            
            messagebox.showinfo("Download", f"Downloaded: {url[:50]}...")
        
        # Start simulation in thread
        thread = threading.Thread(target=simulate_download)
        thread.daemon = True
        thread.start()
    
    # Playback controls
    def toggle_playback(self):
        """Toggle video playback"""
        if self.preview_widget:
            self.preview_widget.toggle_playback()
            playback_state = "Playing" if self.preview_widget.is_playing else "Paused"
            self.status_message.config(text=playback_state)
        else:
            self.logger.info("Toggle playback (no preview available)")
    
    # Processing operations
    def start_processing(self):
        """Start video processing"""
        if not self.current_file:
            messagebox.showwarning("No File", "Please load a video file first")
            return
        
        if self.is_processing:
            messagebox.showwarning("Processing", "Already processing another operation.")
            return
        
        self.is_processing = True
        self.update_status_indicator('processing')
        self.status_message.config(text="Processing...")
        
        # Show progress bar
        self.progress_bar.pack(side='left', padx=10)
        
        # Simulate processing
        def simulate_processing():
            for i in range(101):
                self.progress_var.set(i)
                self.root.update_idletasks()
                self.root.after(50)  # 50ms delay
            
            # Finish processing
            self.finish_processing(True, "Video processing completed!")
        
        # Start simulation in thread
        thread = threading.Thread(target=simulate_processing)
        thread.daemon = True
        thread.start()
    
    def finish_processing(self, success: bool = True, message: str = ""):
        """Finish processing operation"""
        self.is_processing = False
        self.progress_bar.pack_forget()
        self.progress_var.set(0)
        
        if success:
            self.update_status_indicator('ready')
            self.status_message.config(text="Processing completed")
            messagebox.showinfo("Success", message)
        else:
            self.update_status_indicator('error')
            self.status_message.config(text="Processing failed")
            messagebox.showerror("Error", message)
    
    # View operations
    def reset_layout(self):
        """Reset layout to default"""
        self.logger.info("Reset layout")
        messagebox.showinfo("Reset Layout", "Layout reset to default")
    
    # Help and about
    def show_help(self):
        """Show help dialog"""
        help_text = """FFmpeg Editor - Keyboard Shortcuts

File Operations:
  Ctrl+O    Open file
  Ctrl+I    Import from URL
  Ctrl+Q    Quit application

Playback Controls:
  Space     Toggle play/pause
  
View:
  F1        Show this help

Tips:
  • Double-click files in media list to load them
  • Use toolbar buttons for quick access
  • Check status bar for current operations
"""
        messagebox.showinfo("Help - Keyboard Shortcuts", help_text)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """FFmpeg Editor v1.0.0
Professional Video Processing Tool

Features:
• Video processing with FFmpeg
• Real-time preview
• URL import support
• Professional UI with Purple Blackhole theme

Developed with Python & Tkinter
© 2025 FFmpeg Editor Team
"""
        messagebox.showinfo("About FFmpeg Editor", about_text)
    
    # Event handlers
    def on_media_double_click(self, event):
        """Handle double-click on media list"""
        selection = self.media_listbox.curselection()
        if selection:
            filename = self.media_listbox.get(selection[0])
            self.logger.info(f"Double-clicked on: {filename}")
            # TODO: Load selected media file if we have full path
    
    def on_closing(self):
        """Handle window closing"""
        if self.is_processing:
            if messagebox.askokcancel("Processing", 
                "Video is still processing. Are you sure you want to quit?"):
                self.is_processing = False
            else:
                return
        
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.quit_application()
    
    def quit_application(self):
        """Quit application with cleanup"""
        # Cleanup preview widget
        if self.preview_widget:
            try:
                self.preview_widget.cleanup()
            except:
                pass
        
        self.logger.info("Quitting application")
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Start the application main loop"""
        try:
            # Center window on screen
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f"{width}x{height}+{x}+{y}")
            
            # Show window
            self.root.deiconify()
            self.root.mainloop()
            
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
        except Exception as e:
            self.logger.error(f"Application runtime error: {e}")
            messagebox.showerror("Runtime Error", f"Application error: {str(e)}")
        finally:
            # Ensure cleanup
            if hasattr(self, 'preview_widget') and self.preview_widget:
                try:
                    self.preview_widget.cleanup()
                except:
                    pass

# Test the main window
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test configuration
    test_config = {
        'theme': {
            'name': 'Purple Blackhole'
        }
    }
    
    try:
        # Create and run main window
        app = MainWindow(test_config)
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()