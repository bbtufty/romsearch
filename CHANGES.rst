0.0.3 (2024-05-08)
==================

Features
--------

- Added Sony - PlayStation 2

Fixes
-----

Configs
~~~~~~~

- Included dash between disc and number/letter for disc matching
- Added specific regex options for PS2

0.0.2 (2024-05-07)
==================

Features
--------

- Added Nintendo - Nintendo Entertainment System
- Added tools to parse filenames or full games list out of parsed .dat files, to check for new regex terms to add

Fixes
-----

DupeParser
~~~~~~~~~~

- Fixed crash if "searchTerm" does not exist in the retool dupe dict
- Get dupes from retool first, before dat file

GameFinder
~~~~~~~~~~

- Fixed bug where if include_games was defined but not for the platform, nothing would be found
- The full list of games is now sorted
- Fixed bug where occasionally multiple entries due to upper/lowercase could occur

ROMChooser
~~~~~~~~~~

- Revisions are now weighted more heavily than versions
- Budget editions are now favoured above anything else, assuming they roll in the various revision/version changes

ROMParser
~~~~~~~~~

- Fixed crash if "searchTerm" does not exist in the retool dupe dict

Configs
~~~~~~~

- Added specific regex options for NES
- Regions now has options for multiple rendering (e.g. UK can be UK or United Kingdom)
- Grouped ``rerelease`` with ``demoted_versions`` in regex
- Decoupled revisions from versions

0.0.1 (2024-05-06)
==================

- Initial release, support for GameCube, SNES, PSX