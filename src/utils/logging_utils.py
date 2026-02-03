"""
Logging utilities for the Mistral OCR pipeline.
"""

import logging
import sys
from typing import Optional


def setup_logging(verbose: bool = False, quiet: bool = False, 
                  log_file: Optional[str] = None) -> None:
    """
    Setup logging configuration
    
    Args:
        verbose: Enable verbose logging (DEBUG level)
        quiet: Reduce logging output (WARNING level)
        log_file: Optional path to log file
    """
    # Determine log level
    if quiet:
        level = logging.WARNING
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    # Configure logging
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True  # Override any existing handlers
    )
    
    # Set specific loggers
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    if verbose:
        logging.debug("Verbose logging enabled")
    elif quiet:
        logging.info("Quiet mode enabled - reduced logging output")