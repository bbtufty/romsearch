##########
ROMPatcher
##########

If a patch file is found and the ROMPatcher module is selected, then this will download patch files and apply to ROMs.
To highlight if a ROM has been patched, the final file will have a (ROMPatched) in the file name.

Currently, ROMSearch only uses ``xdelta`` to patch ROMs.

For more details on the ROMPatcher arguments, see the :doc:`config file documentation <../configs/config>`.

xdelta
======

To use ``xdelta``, download the latest xdelta3 release from
`here <https://github.com/jmacd/xdelta-gpl/releases/latest>`_. After unzipping the .exe file, add the path to this file
into your config, under ``xdelta_path`` in the ``rompatcher`` config section.

API
===

.. autoclass:: romsearch.ROMPatcher
    :no-index:
    :members:
    :undoc-members: