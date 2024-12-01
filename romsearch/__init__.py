from importlib.metadata import version

# Get the version
__version__ = version(__name__)

from .modules import (
    DATParser,
    DupeParser,
    GameFinder,
    RAHasher,
    ROMDownloader,
    ROMChooser,
    ROMCleaner,
    ROMMover,
    ROMParser,
    ROMPatcher,
    ROMSearch,
)

__all__ = [
    "DATParser",
    "DupeParser",
    "GameFinder",
    "RAHasher",
    "ROMDownloader",
    "ROMChooser",
    "ROMCleaner",
    "ROMMover",
    "ROMParser",
    "ROMPatcher",
    "ROMSearch",
]
