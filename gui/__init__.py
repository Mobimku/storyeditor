# gui/__init__.py
"""
GUI modules for FFmpeg Editor
Fixed imports and error handling
"""

import logging

# Configure logging for GUI modules
logging.getLogger(__name__).addHandler(logging.NullHandler())

try:
    from .theme_manager import ThemeManager
    THEME_MANAGER_AVAILABLE = True
except ImportError as e:
    logging.getLogger(__name__).warning(f"ThemeManager import failed: {e}")
    THEME_MANAGER_AVAILABLE = False
    ThemeManager = None

try:
    from .main_window import MainWindow
    MAIN_WINDOW_AVAILABLE = True
except ImportError as e:
    logging.getLogger(__name__).warning(f"MainWindow import failed: {e}")
    MAIN_WINDOW_AVAILABLE = False
    MainWindow = None

try:
    from .preview_widget import PreviewWidget
    PREVIEW_WIDGET_AVAILABLE = True
except ImportError as e:
    logging.getLogger(__name__).warning(f"PreviewWidget import failed: {e}")
    PREVIEW_WIDGET_AVAILABLE = False
    PreviewWidget = None

try:
    from .timeline_widget import TimelineWidget
    TIMELINE_WIDGET_AVAILABLE = True
except ImportError as e:
    logging.getLogger(__name__).warning(f"TimelineWidget import failed: {e}")
    TIMELINE_WIDGET_AVAILABLE = False
    TimelineWidget = None

try:
    from .tab_editor import EditorTab
    TAB_EDITOR_AVAILABLE = True
except ImportError as e:
    logging.getLogger(__name__).warning(f"EditorTab import failed: {e}")
    TAB_EDITOR_AVAILABLE = False
    EditorTab = None

try:
    from .tab_compiler import CompilerTab
    TAB_COMPILER_AVAILABLE = True
except ImportError as e:
    logging.getLogger(__name__).warning(f"CompilerTab import failed: {e}")
    TAB_COMPILER_AVAILABLE = False
    CompilerTab = None

# Export available modules
__all__ = []

if THEME_MANAGER_AVAILABLE:
    __all__.append('ThemeManager')

if MAIN_WINDOW_AVAILABLE:
    __all__.append('MainWindow')

if PREVIEW_WIDGET_AVAILABLE:
    __all__.append('PreviewWidget')

if TIMELINE_WIDGET_AVAILABLE:
    __all__.append('TimelineWidget')

if TAB_EDITOR_AVAILABLE:
    __all__.append('EditorTab')

if TAB_COMPILER_AVAILABLE:
    __all__.append('CompilerTab')

# Module status for debugging
MODULE_STATUS = {
    'ThemeManager': THEME_MANAGER_AVAILABLE,
    'MainWindow': MAIN_WINDOW_AVAILABLE,
    'PreviewWidget': PREVIEW_WIDGET_AVAILABLE,
    'TimelineWidget': TIMELINE_WIDGET_AVAILABLE,
    'EditorTab': TAB_EDITOR_AVAILABLE,
    'CompilerTab': TAB_COMPILER_AVAILABLE
}

def get_module_status():
    """Get status of all GUI modules"""
    return MODULE_STATUS.copy()

def check_dependencies():
    """Check and report missing dependencies"""
    missing = []
    for module, available in MODULE_STATUS.items():
        if not available:
            missing.append(module)
    
    if missing:
        logging.getLogger(__name__).warning(f"Missing GUI modules: {', '.join(missing)}")
    
    return len(missing) == 0