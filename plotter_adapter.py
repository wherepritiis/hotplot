#!/usr/bin/env python3
"""
Plotter adapter module for supporting both AxiDraw and NextDraw plotters.
Provides a unified interface that handles API differences transparently.
"""

# Plotter type constants
PLOTTER_AXIDRAW = "axidraw"
PLOTTER_NEXTDRAW = "nextdraw"

# Global plotter type setting (default to AxiDraw for backward compatibility)
_current_plotter_type = PLOTTER_AXIDRAW

# Cache for NextDraw availability (checked dynamically)
_nextdraw_available_cache = None


def _check_nextdraw_availability():
    """Check if NextDraw is available by attempting to import it."""
    global _nextdraw_available_cache
    
    # Always re-check (don't cache) to detect newly installed libraries
    # This allows detection without server restart
    try:
        from nextdraw import NextDraw
        _nextdraw_available_cache = True
        return True
    except ImportError:
        _nextdraw_available_cache = False
        return False


# Initial check
_check_nextdraw_availability()


def get_plotter_type():
    """Get the current plotter type."""
    return _current_plotter_type


def set_plotter_type(plotter_type):
    """Set the current plotter type. Valid values: 'axidraw' or 'nextdraw'."""
    global _current_plotter_type
    if plotter_type not in (PLOTTER_AXIDRAW, PLOTTER_NEXTDRAW):
        raise ValueError(f"Invalid plotter type: {plotter_type}. Must be 'axidraw' or 'nextdraw'")
    _current_plotter_type = plotter_type


def is_nextdraw_available():
    """Check if NextDraw library is available. Re-checks dynamically."""
    return _check_nextdraw_availability()


def create_plotter_instance(plotter_type=None):
    """
    Create a plotter instance based on the specified type.
    
    Args:
        plotter_type: 'axidraw' or 'nextdraw'. If None, uses current global setting.
    
    Returns:
        Plotter instance (AxiDraw or NextDraw)
    
    Raises:
        ImportError: If NextDraw is requested but not available
        ValueError: If invalid plotter type is specified
    """
    if plotter_type is None:
        plotter_type = _current_plotter_type
    
    if plotter_type == PLOTTER_AXIDRAW:
        from pyaxidraw import axidraw
        return axidraw.AxiDraw()
    
    elif plotter_type == PLOTTER_NEXTDRAW:
        # Re-check availability dynamically
        if not _check_nextdraw_availability():
            raise ImportError(
                "NextDraw library is not installed. "
                "Please install it to use NextDraw support. "
                "See README.md for installation instructions."
            )
        # Import NextDraw fresh (availability check already verified it's available)
        # This avoids any potential issues with module caching
        from nextdraw import NextDraw
        return NextDraw()
    
    else:
        raise ValueError(f"Invalid plotter type: {plotter_type}. Must be 'axidraw' or 'nextdraw'")


def usb_command(plotter_instance, command):
    """
    Send a USB command to the plotter, handling API differences.
    
    Args:
        plotter_instance: The plotter instance (AxiDraw or NextDraw)
        command: Command string (without trailing \\r for NextDraw)
    
    Note:
        AxiDraw requires \\r at the end of commands, NextDraw does not.
        This function handles the difference automatically.
    """
    plotter_type = _current_plotter_type
    
    if plotter_type == PLOTTER_AXIDRAW:
        # AxiDraw requires \r at the end
        if not command.endswith('\r'):
            command = command + '\r'
        plotter_instance.usb_command(command)
    else:
        # NextDraw does not need \r (it's added automatically)
        # Remove \r if present to avoid double-adding
        if command.endswith('\r'):
            command = command[:-1]
        plotter_instance.usb_command(command)


def usb_query(plotter_instance, query):
    """
    Send a USB query to the plotter, handling API differences.
    
    Args:
        plotter_instance: The plotter instance (AxiDraw or NextDraw)
        query: Query string (without trailing \\r for NextDraw)
    
    Returns:
        Query response string
    
    Note:
        AxiDraw requires \\r at the end of queries, NextDraw does not.
        This function handles the difference automatically.
    """
    plotter_type = _current_plotter_type
    
    if plotter_type == PLOTTER_AXIDRAW:
        # AxiDraw requires \r at the end
        if not query.endswith('\r'):
            query = query + '\r'
        return plotter_instance.usb_query(query)
    else:
        # NextDraw does not need \r (it's added automatically)
        # Remove \r if present to avoid double-adding
        if query.endswith('\r'):
            query = query[:-1]
        return plotter_instance.usb_query(query)


def get_plotter_display_name(plotter_type=None):
    """Get the display name for a plotter type."""
    if plotter_type is None:
        plotter_type = _current_plotter_type
    
    if plotter_type == PLOTTER_AXIDRAW:
        return "AxiDraw"
    elif plotter_type == PLOTTER_NEXTDRAW:
        return "NextDraw"
    else:
        return "Unknown"


def get_api_display_name(plotter_type=None):
    """Get the API/library display name for a plotter type."""
    if plotter_type is None:
        plotter_type = _current_plotter_type
    
    if plotter_type == PLOTTER_AXIDRAW:
        return "PyAxidraw"
    elif plotter_type == PLOTTER_NEXTDRAW:
        return "NextDraw"
    else:
        return "Unknown"
