from enum import Enum


class Domain(Enum):
    CS = "CS"
    DEV = "DEV"


class SourceType(Enum):
    GITHUB = "GITHUB"
    SLACK = "SLACK"
    NOTION = "NOTION"
    RAW_TEXT = "RAW_TEXT"
    FILE = "FILE"
