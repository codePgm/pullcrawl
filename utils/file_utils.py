"""File operation utilities."""

import re
import time
from pathlib import Path


def clean_filename(text: str, max_length: int = 100) -> str:
    """Clean text for use as filename.
    
    Removes invalid characters and limits length.
    """
    # Remove invalid filename characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', text)
    # Limit length
    return cleaned[:max_length]


def get_timestamp() -> str:
    """Get current timestamp in YYYYmmdd_HHMMSS format."""
    return time.strftime('%Y%m%d_%H%M%S')


def ensure_directory(path: Path) -> None:
    """Ensure directory exists, create if not."""
    path.mkdir(parents=True, exist_ok=True)
