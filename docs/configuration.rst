#############
Configuration
#############

The config.yml file
===================

ROMSearch is configured primarily through simple, human-readable .yml files. Having set up your config file,
you can run ROMSearch just by: ::

    from romsearch import ROMSearch

    config_file = "config.yml"

    rs = ROMSearch(config_file)
    rs.run()

Setting up a config file
========================

The config file is an easy way to let ROMSearch know where to look for various files. It also includes a
number of switches that may be useful in different use cases.

**ROMSearch works in such a way that by default it will grab what it thinks is the best ROM file. You can disable
many of the ways it decides this if you want to grab multiple files**

As a minimal example, if we wanted to grab the entire US Catalog of PlayStation games and post what you've added to a
Discord channel, the config file would look something like this: ::

    raw_dir: 'F:\Emulation\raw'
    rom_dir: 'F:\Emulation\ROMs'
    dat_dir: 'F:\Emulation\data\dats'
    parsed_dat_dir: 'F:\Emulation\data\dats_parsed'
    dupe_dir: 'F:\Emulation\data\dupes'

    platforms:
      - Sony - PlayStation

    region_preferences:
      - USA

    language_preferences:
      - English

    romdownloader:
      remote_name: 'rclone_remote'

    discord:
      webhook_url: "https://discord.com/api/webhooks/webhook_url"

ROMS will be selected and moved to F:\Emulation\ROMs\Sony - PlayStation. Pretty simple, right? There are a number of
more granular controls if you want them, for more information in the :doc:`config file documentation <configs/config>`.
