from importlib.metadata import version

# Get the version
__version__ = version(__name__)

from .modules import (
    DATMapper,
    DATParser,
    DupeParser,
    GameFinder,
    RAHasher,
    ROMDownloader,
    ROMChooser,
    ROMCleaner,
    ROMCompressor,
    ROMMover,
    ROMParser,
    ROMPatcher,
    ROMSearch,
)

__all__ = [
    "DATMapper",
    "DATParser",
    "DupeParser",
    "GameFinder",
    "RAHasher",
    "ROMDownloader",
    "ROMChooser",
    "ROMCleaner",
    "ROMCompressor",
    "ROMMover",
    "ROMParser",
    "ROMPatcher",
    "ROMSearch",
]
