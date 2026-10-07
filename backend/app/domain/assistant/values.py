from enum import Enum


class Mode(str, Enum):
    RESEARCH = "research"


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
