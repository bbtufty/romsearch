#########
ROMParser
#########

ROMParser will parse out useful information from both filenames and parsed .dat files. These are things like regions,
languages, and various flags for things like Demos or BIOS that then can be used to choose the best ROM.

If explicit languages are not found, then ROMParser will generally assign a language based on the region. This is not
true for regions like Scandinavia, where it could be any of multiple languages.

ROMParser can also determine whether ROMs are compatible with RetroAchievements. It does this in two passes - first
by matching to the hash (if RA uses MD5 hashes) or the name. Secondly, for ROMs that require patches it will search
by those by name, matching to things like region/version. In the second case, if a patch is needed it will pull that
out. This does rely on the naming on RA being pretty accurate, which is mostly the case but some may be missed.

For more details on the ROMParser arguments, see the :doc:`config file documentation <../configs/config>`.

API
===

.. autoclass:: romsearch.ROMParser
    :no-index:
    :members:
    :undoc-members: