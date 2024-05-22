

from typing import TypeAlias, Literal, Callable
import traceback


LoggingLevel: TypeAlias = Literal['debug', 'info', 'warn', 'error', 'fatal']

LoggingOutput: TypeAlias = Callable[[str], None]

def _log_level_to_int(level: LoggingLevel) -> int:
    if level == 'debug': return 0
    if level == 'info': return 1
    if level == 'warn': return 2
    if level == 'error': return 3
    if level == 'fatal': return 4
    raise ValueError(f"Invalid logging level: {level}")

def cast_logging_level(level: str) -> LoggingLevel | None:
    if level == 'debug': return 'debug'
    if level == 'info': return 'info'
    if level == 'warn': return 'warn'
    if level == 'error': return 'error'
    if level == 'fatal': return 'fatal'
    return None

class Logger:
    prefix: str | None
    logging_level: LoggingLevel
    logging_output: LoggingOutput

    subloggers: list['Logger']

    def append_sublogger(self, sublogger: 'Logger'):
        self.subloggers.append(sublogger)

    def remove_sublogger(self, sublogger: 'Logger'):
        self.subloggers.remove(sublogger)

    def __init__(
        self, 
        prefix: str | None = None,
        logging_level: LoggingLevel = "info", 
        logging_output: LoggingOutput = print
    ):
        self.prefix = prefix
        self.logging_level = logging_level
        self.logging_output = logging_output
        self.subloggers = []

    def debug(self, message: str):
        if self.__should_log('debug'):
            self.logging_output(f"\033[0;32m{self.__prefix()}{message}\033[0m")

        for sublogger in self.subloggers: sublogger.debug(message)

    def info(self, message: str):
        if self.__should_log('info'):
            self.logging_output(f"\033[0;34m{self.__prefix()}\033[0m{message}")

        for sublogger in self.subloggers: sublogger.info(message)

    def warn(self, message: str):
        if self.__should_log('warn'):
            self.logging_output(f"\033[0;33m{self.__prefix()}{message}\033[0m")

        for sublogger in self.subloggers: sublogger.warn(message)

    def error(self, message: str):
        if self.__should_log('error'):
            self.logging_output(f"\033[0;31m{self.__prefix()}{message}\033[0m")

        for sublogger in self.subloggers: sublogger.error(message)

    def exception(self, error: Exception):
        if self.__should_log('error'):
            self.logging_output(f"\033[0;31m{self.__prefix()}{str(error)}\033[0m")
            self.logging_output(traceback.format_exc())

        for sublogger in self.subloggers: sublogger.exception(error)
        
    def fatal(self, message: str):
        if self.__should_log('fatal'):
            self.logging_output(f"\033[0;31m{self.__prefix()}{message}\033[0m")

        for sublogger in self.subloggers: sublogger.fatal(message)

    def __prefix(self) -> str:
        return f"[{self.prefix}] " if self.prefix is not None else ""

    def __should_log(self, level: LoggingLevel) -> bool:
        return _log_level_to_int(level) >= _log_level_to_int(self.logging_level)