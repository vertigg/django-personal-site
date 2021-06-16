"""
Bot module for all convert functions
"""

from datetime import datetime as dt


def convert_time(unixtime: float) -> str:
    """Convert posix time to datetime for database record"""
    return dt.fromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')
