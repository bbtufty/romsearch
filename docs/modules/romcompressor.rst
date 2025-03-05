#############
ROMCompressor
#############

For some platforms, ROMs may come as a number of individual files (e.g. the original PlayStation has .bin and .cue
files). ROMCompressor simplifies this by compressing these files into one single file.

If a platform is marked for compression, and the path to the appropriate executable is given in the config, then
ROMCompressor will compress these files down.

Currently, ROMSearch can use ``chdman`` to compress ROMs to ``.chd`` files.

For more details on the ROMCompressor arguments, see the :doc:`config file documentation <../configs/config>`.

chdman
======

To use ``chdman``, download the latest chdman release from
`https://github.com/umageddon/namDHC/releases <https://github.com/umageddon/namDHC/releases>`_.
Download chdman.exe, add the path to this file into your config, under ``chdman_path`` in the
``romcompressor`` config section.

API
===

.. autoclass:: romsearch.ROMCompressor
    :no-index:
    :members:
    :undoc-members: