#########
platforms
#########

ROMSearch can work for a number of platforms, and the config for each is stored in a separate configuration file.

Syntax: ::

    group: ["Redump", "No-Intro"]   # The group for these files. Currently either "Redump" or "No-Intro
    ftp_dir: [ftp_dir]              # The FTP dir for rclone. This is usually something like [group]/[platform]
    unzip: true                     # OPTIONAL. Whether to unzip files when moving. Defaults to false
    additional_dirs:                # OPTIONAL. Occasionally, files may need to be pulled from other ftp directories.
      [additional_dir]: [ftp_dir]   #           These can be specified here

Nintendo - GameCube
===================

.. literalinclude:: ../../romsearch/configs/platforms/Nintendo - GameCube.yml

Nintendo - Super Nintendo Entertainment System
==============================================

.. literalinclude:: ../../romsearch/configs/platforms/Nintendo - Super Nintendo Entertainment System.yml

Sony - PlayStation
==================

.. literalinclude:: ../../romsearch/configs/platforms/Sony - PlayStation.yml