from pathlib import Path


def is_in_docker() -> bool:
    return Path("/.dockerenv").is_file()
