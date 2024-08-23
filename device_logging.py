""" A simple logger module. """
import os
import time

LOG_FOLDER = "logs"
LOG_FILE = "device.log"
LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50
}
LOG_COLORS = {
    "DEBUG": "\033[94m",      # Blue
    "INFO": "\033[92m",       # Green
    "WARNING": "\033[93m",    # Yellow
    "ERROR": "\033[91m",      # Red
    "CRITICAL": "\033[95m",   # Magenta
    "RESET": "\033[0m"        # Reset
}


class Logger:
    """
    A simple logger class.
    """
    def __init__(
        self,
        name,
        level="DEBUG",
        filename=f"{LOG_FOLDER}/{LOG_FILE}"
    ) -> None:
        self.name = name
        self.level = LOG_LEVELS[level]
        self.filename = filename
        if LOG_FOLDER not in os.listdir():
            os.mkdir(LOG_FOLDER)
        if LOG_FILE not in os.listdir(LOG_FOLDER):
            with open(f"{LOG_FOLDER}/{LOG_FILE}", "w", encoding="utf-8") as f:
                f.write("")

    def _get_uptime(self) -> str:
        uptime_s = time.ticks_ms() // 1000
        return '{:02}:{:02}:{:02}'.format(
            uptime_s // 3600, (uptime_s % 3600) // 60, uptime_s % 60
        )

    def _format_message(self, level: str, message: str) -> tuple[str, str]:
        """ Format the message to be logged. """
        color = LOG_COLORS.get(level, LOG_COLORS["RESET"])
        reset = LOG_COLORS["RESET"]
        uptime = self._get_uptime()
        return (
            f"[{self.name}] {uptime}{color} {level}: {message}{reset}",
            f"[{self.name}] {uptime} {level}: {message}"
        )

    def _log(self, level: str, message: str) -> None:
        """ Log a message. """
        if LOG_LEVELS[level] >= self.level:
            formatted_message = self._format_message(level, message)
            print(formatted_message[0])
            if self.filename:
                self._write_to_file(formatted_message[1])

    def _write_to_file(self, message: str) -> None:
        """ Write a message to the log file. """
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(message + "\n")

    def debug(self, message: str) -> None:
        """ Log a debug message. """
        self._log("DEBUG", message)

    def info(self, message: str) -> None:
        """ Log an info message. """
        self._log("INFO", message)

    def warning(self, message: str) -> None:
        """ Log a warning message. """
        self._log("WARNING", message)

    def error(self, message: str) -> None:
        """ Log an error message. """
        self._log("ERROR", message)

    def critical(self, message: str) -> None:
        """ Log a critical message. """
        self._log("CRITICAL", message)

    def clear(self) -> None:
        """
        Delete the log file content.
        """
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write("")
