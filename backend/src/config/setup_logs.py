import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

class LogSetup:
    """
    Professional logging setup utility with configurable console and file handlers.
    """

    def __init__(
        self,
        name: str,
        level: int = logging.INFO,
        log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        date_format: str = "%Y-%m-%d %H:%M:%S",
    ):
        self.logger = logging.getLogger(name)
        self.level = level
        self.log_format = log_format
        self.date_format = date_format

    def _get_formatter(self) -> logging.Formatter:
        """
        Returns a logging formatter with the configured format and date.
        """
        return logging.Formatter(self.log_format, datefmt=self.date_format)
    
    def setup_console_handler(self) -> None:
        """
        Adds a console (stdout) logging handler to the logger.
        """
        if any(isinstance(h, logging.StreamHandler) for h in self.logger.handlers):
            return  # Prevent duplicate console handlers
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self._get_formatter())
        self.logger.setLevel(self.level)
        self.logger.addHandler(console_handler)
    
    def setup_file_handler(self, filename: str = "application.log") -> None:
        """
        Adds a timed rotating file handler to the logger.

        Args:
            filename (str): Name of the log file (created in ../logs/ directory).
        """
        # Determine log directory path
        parent_dir = Path(__file__).parent.parent.parent.resolve()
        log_folder = parent_dir / 'logs'
        log_folder.mkdir(parents=True, exist_ok=True)
        log_file = log_folder / filename
        log_file.touch(exist_ok=True)

        # Prevent duplicate file handlers for the same file
        file_handler = TimedRotatingFileHandler(
            filename=log_file, when="midnight", interval=1, backupCount=7
        )
        file_handler.setFormatter(self._get_formatter())
        self.logger.setLevel(self.level)
        self.logger.addHandler(file_handler)

        return file_handler

    def get_logger(self) -> logging.Logger:
        """
        Returns the configured logger instance.

        Returns:
            logging.Logger: The configured logger.
        """
        return self.logger


if __name__=='__main__':
    logger_setup = LogSetup('my_logger')
    logger_setup.setup_console_handler()
    file_handler = logger_setup.setup_file_handler() 
    logger = logger_setup.get_logger()
    logger.info('this is the logging first message')