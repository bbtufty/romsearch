# ROMSearch

[![](https://img.shields.io/pypi/v/romsearch.svg?label=PyPI&style=flat-square)](https://pypi.org/pypi/romsearch/)
[![](https://img.shields.io/pypi/pyversions/romsearch.svg?label=Python&color=yellow&style=flat-square)](https://pypi.org/pypi/romsearch/)
[![Docs](https://readthedocs.org/projects/romsearch/badge/?version=latest&style=flat-square)](https://romsearch.readthedocs.io/en/latest/)
[![Actions](https://img.shields.io/github/actions/workflow/status/bbtufty/romsearch/build.yaml?branch=main&style=flat-square)](https://github.com/bbtufty/romsearch/actions)
[![License](https://img.shields.io/badge/license-GNUv3-blue.svg?label=License&style=flat-square)](LICENSE)

ROMSearch is designed as a simple-to-inferface with tool that will allow you to pull ROM files from some remote (or
local) location, figure out the best ROM, and move it cleanly to a folder that can imported into an emulator. ROMSearch
is supposed to be a one-shot program to get you from files online to playing games (which is what we want, right?).

ROMSearch also has a GUI! Currently only for Windows, but makes setting up configurations simple and clean.

ROMSearch offers the ability to:

* Sync from remote folder using rclone
* Parse DAT files as well as filenames for ROM information
* Remove dupes from ROM lists using the excellent ``retool`` clonelists
* Match ROM hashes to RetroAchievements to get compatible ROMs 
* Patch ROM files so RetroAchievements can be enabled
* Moving files to a structured location, including potentially additional files that may be needed
* Discord integration so users can see the results of runs in a simple, clean way

To get started, see the [documentation](https://romsearch.readthedocs.io/en/latest/). For known issues and workarounds, 
see the [known issues](https://romsearch.readthedocs.io/en/latest/known_issues.html).

Currently, ROMSearch is in early development, and so many features may be added over time. At the moment, ROMSearch
works for the following consoles:

* Nintendo (Handheld)
   * Game Boy
   * Game Boy Color
   * Game Boy Advance
   * Pokemon Mini
* Nintendo (Home)
   * Nintendo Entertainment System
   * Super Nintendo Entertainment System
   * Nintendo 64
   * GameCube
* Sega (Home)
  * Mega Drive/Genesis
* Sony (Handheld)
   * PlayStation Portable
* Sony (Home)
   * PlayStation
   * PlayStation 2

but be aware there may be quirks that will only become apparent over time. We encourage users to open
[issues](https://github.com/bbtufty/romsearch/issues) as and where they find them.

The ROMSearch icon has been created by [Freepik - Flaticon](https://www.flaticon.com/free-icons/rom).
