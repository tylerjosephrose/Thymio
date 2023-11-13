from enum import Enum


class Color(Enum):
    """
    Enum of predefined colors.
    """
    RED = "#FF0000"
    GREEN = "#00FF00"
    BLUE = "#0000FF"
    YELLOW = "#FFFF00"
    CYAN = "#00FFFF"
    MAGENTA = "#FF00FF"
    WHITE = "#FFFFFF"
    OFF = "#000000"


class Sound(Enum):
    STARTUP = 0
    SHUTDOWN = 1
    ARROW_BTN = 2
    CENTER_BTN = 3
    ALARM = 4
    SCHOCK = 5
    FOLLOWING = 6
    PROXIMITY = 7
    STOP = 8
