from enum import Enum


class RouterDomain(Enum):
    CS = "CS"
    DEV = "DEV"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class Domain(Enum):
    CS = "CS"
    DEV = "DEV"


class SourceType(Enum):
    GITHUB = "GITHUB"
    SLACK = "SLACK"
    NOTION = "NOTION"
    RAW_TEXT = "RAW_TEXT"
    FILE = "FILE"
