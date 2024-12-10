##########
ROMPatcher
##########

If a patch file is found and the ROMPatcher module is selected, then this will download patch files and apply to ROMs.
To highlight if a ROM has been patched, the final file will have a (ROMPatched) in the file name.

Currently, ROMSearch can use ``xdelta`` and ``RomPatcher.js`` to patch ROMs.

For more details on the ROMPatcher arguments, see the :doc:`config file documentation <../configs/config>`.

xdelta
======

To use ``xdelta``, download the latest xdelta3 release from
`https://github.com/jmacd/xdelta-gpl/releases/latest <https://github.com/jmacd/xdelta-gpl/releases/latest>`_.
After unzipping the .exe file, add the path to this file into your config, under ``xdelta_path`` in the ``rompatcher``
config section.

RomPatcher.js
=============

You may need to download ``node.js`` to start with. You can get it at `https://nodejs.org/en <https://nodejs.org/en>`_.
After that, clone the NodePatcher.js repository and install: ::

   git clone https://github.com/marcrobledo/RomPatcher.js.git
   cd RomPatcher.js
   npm install

After this, as the RomPatcher.js path in the config, put the path to the ``index.js`` file.

API
===

.. autoclass:: romsearch.ROMPatcher
    :no-index:
    :members:
    :undoc-members: