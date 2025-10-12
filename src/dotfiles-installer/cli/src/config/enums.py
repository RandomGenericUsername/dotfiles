from enum import Enum


class InstallType(str, Enum):
    update = "update"
    clean = "clean"
