0.0.7 (2024-08-28)
==================

Features
--------

Tests
~~~~~

- Added in initial unit tests for ROMParser and ROMChooser

Fixes
-----

DATParser
~~~~~~~~~

- Logging tidied up to make more readable

DupeParser
~~~~~~~~~~

- Logging tidied up to make more readable

GameFinder
~~~~~~~~~~

- Logging tidied up to make more readable

ROMChooser
~~~~~~~~~~

- Logging significantly improved to make it clear which ROMs have been excluded and why
- Fixed crash when a revision is just labelled "rev"
- Fixed bug where a version like "v.0.1" would cause a crash
- Fixed bug where letter at end of version could cause a crash
- Fixed bug where lettered version could cause a crash
- Fixed bugs with flagging and removing various editions

ROMDownloader
~~~~~~~~~~~~~

- Logging tidied up to make more readable

ROMMover
~~~~~~~~

- Logging tidied up to make more readable

ROMParser
~~~~~~~~~

- ROMParser will now correctly parse multiple regions/languages
- Logging tidied up to make more readable

ROMSearch
~~~~~~~~~

- Logging tidied up to make more readable

General
~~~~~~~

- Bump to 0.0.7
- Due to changes to the re module, ROMSearch requires python>=3.11
- Allowed specifying log level in the config file

0.0.6 (2024-05-23)
==================

Fixes
-----

ROMChooser
~~~~~~~~~~

- Language priorities are now baked into the ROM selection. ROMs with more (and higher priority) languages
  will now be preferred

ROMDownloader
~~~~~~~~~~~~~

- Added a ``use_absolute_url`` option, which if False will strip the leading slash from the directories. This is
  potentially useful if using an HTTP remote
- rclone can now either sync or copy. It'll use sync if completionist mode is on, else it'll use copy which is
  a little cleaner
- If there are errors in the rclone command, ROMDownloader will now retry a few times
- Improved how rclone runs, to be less verbose and hopefully more reliable

ROMParser
~~~~~~~~~

- If no language is given in the ROM data, will attempt to pull this out from the region

General
~~~~~~~

- Updated dev tools for the new config directory structure
- Renamed `ftp_dir` to `dir` ion platform config files for clarity
- Fixed error message in GUI in includes/excludes existed for an unchecked platform


0.0.5 (2024-05-17)
==================

Features
--------

- ROMSearch now has a GUI! This currently is just used for a more friendly way to set the config file, but will
  be built out in the future
- ROMSearch now has two modes: the first is `filter_then_download` (default), which will use the dat file to filter,
  then only download relevant files. The second is `download_then_filter`, which will download everything and then
  filter. For data hoarders!

Fixes
-----

GameFinder
~~~~~~~~~~

- Ensure includes/excludes works the same as it does for ROMDownloader
- Includes/excludes will now search dupes as well, for consistency

ROMDownloader
~~~~~~~~~~~~~

- Ensure output directory exists before downloading files

General
~~~~~~~

- Updates to .github workflows and templates
- `bool_filters` in the config file is now `dat_filters` for clarity
- Overhauled directory handling in the config file
- ROMSearch now has more clearly defined options
- Exposed log directory and cache directory
- Overhauled logging system to avoid unnecessary file bloat and I/O. Speed ups of about a factor 3
- Overhauled how config files are read in to avoid unneccesary I/O. Speed ups of about a factor 2

0.0.4 (2024-05-09)
==================

Features
--------

- Added Sony - PlayStation Portable

Fixes
-----

ROMChooser
~~~~~~~~~~

- Added regex terms for PSP
- Fixed a bug with version scoring

Util
~~~~

- Added feature to flag up tags but not remove them from the short name (e.g. "Demo" should be included in the name,
  but should be used to flag up demo ROMs)

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