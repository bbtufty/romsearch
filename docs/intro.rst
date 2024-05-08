#########
ROMSearch
#########

.. image:: https://img.shields.io/pypi/v/romsearch.svg?label=PyPI&style=flat-square
    :target: https://pypi.org/pypi/romsearch/
.. image:: https://img.shields.io/pypi/pyversions/romsearch.svg?label=Python&color=yellow&style=flat-square
    :target: https://pypi.org/pypi/romsearch/
.. image:: https://img.shields.io/github/actions/workflow/status/bbtufty/romsearch/build_test.yaml?branch=main&style=flat-square
    :target: https://github.com/bbtufty/romsearch/actions
.. image:: https://readthedocs.org/projects/romsearch/badge/?version=latest&style=flat-square
   :target: https://romsearch.readthedocs.io/en/latest/
.. image:: https://img.shields.io/badge/license-GNUv3-blue.svg?label=License&style=flat-square

ROMSearch is designed as a simple-to-inferface with tool that will allow you to pull ROM files from some remote (or
local) location, figure out the best ROM, and move it cleanly to a folder that can imported into an emulator. ROMSearch
is supposed to be a one-shot program to get you from files online to playing games (which is what we want, right?).

ROMSearch offers the ability to:

* Sync from remote folder using rclone
* Parse DAT files as well as filenames for ROM information
* Remove dupes from ROM lists using DAT files as well as the excellent ``retool`` clonelists
* Moving files to a structured location, including potentially additional files that may be needed
* Discord integration so users can see the results of runs in a simple, clean way

To get started, see the :doc:`installation <installation>` and :doc:`configuration <configuration>` pages. For the
philosophy behind how ROMSearch chooses a ROM, see :doc:`1G1R <1g1r>`.

Currently, ROMSearch is in early development, and so many features may be added over time. At the moment, ROMSearch
has the capability for:

* Nintendo - GameCube
* Nintendo - Nintendo Entertainment System
* Nintendo - Super Nintendo Entertainment System
* Sony - PlayStation
* Sony - PlayStation 2

but be aware there may be quirks that will only become apparent over time. We encourage users to open
`issues <https://github.com/bbtufty/romsearch/issues>`_ as and where they find them. Known issues can be found at
:doc:`known issues <known_issues>`.

ROMSearch is also built in such a way that other platforms/filters can be added in a simple way using config files
rather than manually adding to the base code. For more details of how these work, see the various
:doc:`configs <configs>` pages.
