""" A simple logger module. """
import os
LOG_FOLDER = 'logs'
LOG_FILE = 'log.txt'

def init() -> None:
    """
    Initialize the logger.
    """
    if LOG_FOLDER not in os.listdir():
        os.mkdir(LOG_FOLDER)
    if LOG_FILE not in os.listdir(LOG_FOLDER):
        with open(f"{LOG_FOLDER}/{LOG_FILE}", "w", encoding="utf-8") as f:
            f.write("")

def log(msg: str, to_print: bool = True) -> None:
    """
    Log a message to the log file.
    """
    with open(f"{LOG_FOLDER}/{LOG_FILE}", "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    if to_print:
        print(msg)

def delete():
    """
    Delete the log file content.
    """
    with open(f"{LOG_FOLDER}/{LOG_FILE}", "w", encoding="utf-8") as f:
        f.write("")
