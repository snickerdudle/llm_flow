# Logging logic
from typing import Callable, Optional
from datetime import datetime


class Logger:
    def __init__(self, filename="test.log"):
        self.filename = filename
        self.buffer = []

    def writeBufferToFile(self):
        with open(self.filename, "a") as f:
            content = "\n".join(self.buffer) + "\n"
            f.write(content)

    def log(self, message: str, source: Optional[Callable] = None):
        # source is a class method that is calling the logger
        # Message is going to look like this:
        # DD-MM-YY:HH:MM:SS:MS: <class:function> message
        if source is None:
            source = "Unknown"
        else:
            # Get the name of the class that this method belongs to
            # and the name of the method
            source = source.__qualname__

        # Get the datetime string
        datetime_str = datetime.now().strftime("%d-%m-%Y:%H:%M:%S:%f")
        message = f"{datetime_str}: <{source}> {message}"

        self.buffer.append(message)
        print(message)
