"""Helpers for logging configuration and filtering"""

def _stdout_filter(record):
    """Allow only DEBUG, INFO, and WARNING through to stdout."""
    return record["level"].no < 40  # 40 = ERROR
