from importlib.metadata import version

# Get the version
__version__ = version(__name__)

from .modules import (DATParser,
                      DupeParser,
                      GameFinder,
                      ROMDownloader,
                      ROMChooser,
                      ROMMover,
                      ROMParser,
                      ROMSearch
                      )

__all__ = [
    "DATParser",
    "DupeParser",
    "GameFinder",
    "ROMDownloader",
    "ROMChooser",
    "ROMMover",
    "ROMParser",
    "ROMSearch",
]
