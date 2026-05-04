#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════
#  ERROR_HANDLER.PY — Graceful Error Handling & Decorators
# ═══════════════════════════════════════════════════════════════

import functools
import logging
import subprocess
import sys
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)


def handle_subprocess_error(func: Callable) -> Callable:
    """
    Decorator for subprocess operations with detailed error messages.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except subprocess.TimeoutExpired as e:
            logger.error(f"⏱️  Timeout in {func.__name__}: operation took too long")
            return None
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Process failed in {func.__name__}")
            logger.error(f"   Command: {' '.join(e.cmd)}")
            logger.error(f"   Return code: {e.returncode}")
            if e.stderr:
                logger.error(f"   Error: {e.stderr[:200]}")
            return None
        except FileNotFoundError as e:
            logger.error(f"❌ File not found in {func.__name__}: {e.filename}")
            if "ffmpeg" in str(e.filename).lower():
                logger.error(
                    "   Install FFmpeg:\n"
                    "   Windows: winget install ffmpeg\n"
                    "   Mac: brew install ffmpeg\n"
                    "   Linux: sudo apt install ffmpeg"
                )
            return None
        except Exception as e:
            logger.error(f"❌ Error in {func.__name__}: {type(e).__name__}: {e}")
            return None
    return wrapper


def handle_io_error(func: Callable) -> Callable:
    """
    Decorator for file I/O operations with detailed error messages.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except IOError as e:
            logger.error(f"❌ I/O Error in {func.__name__}: {e}")
            return None
        except UnicodeDecodeError as e:
            logger.error(f"❌ Encoding error in {func.__name__}: {e}")
            logger.error("   Try: python -m chardet <file>")
            return None
        except Exception as e:
            logger.error(f"❌ Error in {func.__name__}: {type(e).__name__}: {e}")
            return None
    return wrapper


def handle_api_error(func: Callable) -> Callable:
    """
    Decorator for API operations (Pexels, Ollama, etc).
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        import requests
        try:
            return func(*args, **kwargs)
        except requests.exceptions.Timeout:
            logger.error(f"🔌 API timeout in {func.__name__}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"🔌 API connection failed in {func.__name__}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"🔌 HTTP Error in {func.__name__}: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"❌ Error in {func.__name__}: {type(e).__name__}: {e}")
            return None
    return wrapper


class ErrorContext:
    """Context manager for detailed error reporting."""
    
    def __init__(self, operation: str, fallback: Optional[Any] = None):
        self.operation = operation
        self.fallback = fallback
    
    def __enter__(self):
        logger.debug(f"Starting: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.error(f"❌ {self.operation} failed: {exc_val}")
            return False  # Don't suppress exception
        logger.debug(f"✅ {self.operation} completed")
        return True
