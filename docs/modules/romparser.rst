#########
ROMParser
#########

ROMParser will parse out useful information from both filenames and parsed .dat files. These are things like regions,
languages, and various flags for things like Demos or BIOS that then can be used to choose the best ROM.

If explicit languages are not found, then ROMParser will generally assign a language based on the region. This is not
true for regions like Scandinavia, where it could be any of multiple languages.

For more details on the ROMParser arguments, see the :doc:`config file documentation <../configs/config>`.

API
===

.. autoclass:: romsearch.ROMParser
    :no-index:
    :members:
    :undoc-members: