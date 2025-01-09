#########
platforms
#########

ROMSearch can work for a number of platforms, and the config for each is stored in a separate configuration file.

Syntax: ::

    group: ["Redump", "No-Intro"]     # The group for these files. Currently either "Redump" or "No-Intro
    dir: [dir]                        # The remote dir for rclone. This is usually something like [group]/[platform]
    unzip: true                       # OPTIONAL. Whether to unzip files when moving. Defaults to false
    additional_dirs:                  # OPTIONAL. Occasionally, files may need to be pulled from other remote directories.
      [additional_dir]: [dir]         #           These can be specified here

    ra_id: [id]                       # OPTIONAL. The RetroAchievements console ID, from their API_GetConsoleIDs
    ra_hash_method: ["md5", "custom"] # OPTIONAL. The RetroAchievements hash method. Supports "md5" and "custom"

    patch_method: ["xdelta", "rompatcher_js"]  # OPTIONAL: Method for patching ROMs. Supports "xdelta", "rompatcher_js"
    file_exts:                                 # OPTIONAL: Potential file extensions. ROMPatcher uses this to figure
       - [ext]                                 #           out the file to patch
    patch_file_exts:                           # OPTIONAL: Potential file extensions. ROMPatcher uses this to figure
       - [ext]                                 #           out the patch file

Nintendo - Game Boy
===================

.. literalinclude:: ../../romsearch/configs/platforms/Nintendo - Game Boy.yml

Nintendo - Game Boy Color
=========================

.. literalinclude:: ../../romsearch/configs/platforms/Nintendo - Game Boy Color.yml

Nintendo - Game Boy Advance
===========================

.. literalinclude:: ../../romsearch/configs/platforms/Nintendo - Game Boy Advance.yml

Nintendo - Pokemon Mini
=======================

.. literalinclude:: ../../romsearch/configs/platforms/Nintendo - Pokemon Mini.yml

Nintendo - Nintendo Entertainment System
========================================

.. literalinclude:: ../../romsearch/configs/platforms/Nintendo - Nintendo Entertainment System.yml

Nintendo - Super Nintendo Entertainment System
==============================================

.. literalinclude:: ../../romsearch/configs/platforms/Nintendo - Super Nintendo Entertainment System.yml

Nintendo - Nintendo 64
======================

.. literalinclude:: ../../romsearch/configs/platforms/Nintendo - Nintendo 64.yml

Nintendo - GameCube
===================

.. literalinclude:: ../../romsearch/configs/platforms/Nintendo - GameCube.yml

Sega - Mega Drive - Genesis
===========================

.. literalinclude:: ../../romsearch/configs/platforms/Sega - Mega Drive - Genesis.yml

Sony - PlayStation Portable
===========================

.. literalinclude:: ../../romsearch/configs/platforms/Sony - PlayStation Portable.yml

Sony - PlayStation
==================

.. literalinclude:: ../../romsearch/configs/platforms/Sony - PlayStation.yml

Sony - PlayStation 2
====================

.. literalinclude:: ../../romsearch/configs/platforms/Sony - PlayStation 2.yml