import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from .logger import logger

ENV_LOADED = False


def getenv(key: str, default: str = None) -> str:
    global ENV_LOADED

    if not ENV_LOADED:
        load_dotenv()
        ENV_LOADED = True

    return os.getenv(key, default)


def _platform_cache_dir() -> Path:
    """User cache directory for the current platform."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local"
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Caches"
    else:
        base = os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache"

    return Path(base) / "moodle-mcp"


def get_output_dir() -> Path:
    """Directory for API response dumps.

    MCP clients launch servers with an arbitrary working directory -- Claude
    Desktop uses `/`, which is read-only -- so a relative path is not safe to
    write to. Default to the user cache directory and let `MOODLE_MCP_OUTPUT_DIR`
    override it.
    """
    override = getenv("MOODLE_MCP_OUTPUT_DIR")
    return Path(override).expanduser() if override else _platform_cache_dir()


def to_json_file(data, filename, folder=None):
    """Dump an API response to disk for debugging.

    Best effort: these dumps are a debugging aid, so a failure to write one must
    never take down the tool call that produced the data.
    """
    target = Path(folder).expanduser() if folder else get_output_dir()

    try:
        target.mkdir(parents=True, exist_ok=True)
        with open(target / filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except OSError as e:
        logger.warning(f"Could not write debug dump {target / filename}: {e}")
