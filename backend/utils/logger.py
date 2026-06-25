import os
import sys
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = "trust_framework", log_dir: str = "logs") -> logging.Logger:
    """
    Sets up a structured rotating logger that writes both to console and a rotating file store.
    """
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Avoid duplicate handlers if logger is re-initialized
    if logger.handlers:
        return logger

    # Log format definitions
    log_format = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # File Handler
    file_path = os.path.join(log_dir, "system.log")
    file_handler = RotatingFileHandler(
        filename=file_path,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    logger.info(f"Logging setup complete. System logs will write to: {file_path}")
    return logger

# Singleton instance of framework logger
logger = setup_logger()
