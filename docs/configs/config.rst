######
config
######

The ``config.yml`` file defines how ROMSearch will do the run. As such, it has quite a number of options.

Syntax: ::

    raw_dir: [raw_dir]                # Raw directory to download ROM files using ROMDownloader
    rom_dir: [rom_dir]                # Final output directory for ROMs. Will automatically subdivide by platform
    dat_dir: [dat_dir]                # Directory to place raw .dat files
    parsed_dat_dir: [parsed_dat_dir]  # Directory to place parsed .dat files, as well as clonelists
    dupe_dir: [dupe_dir]              # Directory to place dupe files

    run_romdownloader: true           # OPTIONAL. Whether to run ROMDownloader. Defaults to true
    run_datparser: true               # OPTIONAL. Whether to run DATParser. Defaults to true
    run_dupeparser: true              # OPTIONAL. Whether to run DupeParsed. Defaults to true
    run_romchooser: true              # OPTIONAL. Whether to run ROMChooser. Defaults to true
    run_rommover: true                # OPTIONAL. Whether to run ROMMover. Defaults to true

    platforms:                        # List of platforms to download ROMs for
      - [platform]

    region_preferences:               # List of regions, in preference order
      - [most_preferred_region]
      - [next_preferred_region]

    language_preferences:             # List of languages, in preference order
      - [most_preferred_language]
      - [next_preferred_language]

    include_games:                    # OPTIONAL. Use this to trim down the number of ROMs downloaded
      [platform]:
        - [game]

    romsearch:                        # ROMSearch specific options
      dry_run: false                  # OPTIONAL. Set to true to not make any changes to filesystem. Defaults to false

    romdownloader:                    # ROMDownloader specific options
      dry_run: false                  # OPTIONAL. Set to true to not make any changes to filesystem. Defaults to false
      remote_name: 'rclone_remote'    # Rclone remote name
      sync_all: false                 # OPTIONAL. If true, will download everything that rclone finds. Set to false to
                                      #           use the include_games above

    dupeparser:                       # DupeParser specific options
      use_dat: true                   # OPTIONAL. Whether to use .dat files or not. Defaults to true
      use_retool: true                # OPTIONAL. Whether to use retool clonelists or not. Defaults to true

    gamefinder:                       # GameFinder specific options
      filter_dupes: true              # OPTIONAL. Whether to filter dupes or not. Defaults to true

    romparser:                        # ROMParser specific options
      use_dat: true                   # OPTIONAL. Whether to parse properties from .dat files. Defaults to true
      use_filename: true              # OPTIONAL. Whether to parse properties from filename. Defaults to true

    romchooser:                       # ROMChooser specific options
      dry_run: false                  # OPTIONAL. Set to true to not make any changes to filesystem. Defaults to false
      use_best_version: true          # OPTIONAL. Whether to choose only what ROMChooser decides is the best version.
                                                  Defaults to true
      allow_multiple_regions: false   # OPTIONAL. If true, will allow files from multiple regions, else will choose the
                                                  highest region in the list. Defaults to false
      filter_regions: true            # OPTIONAL. Whether to filter by region or not. Defaults to true
      filter_languages: true          # OPTIONAL. Whether to filter by language or not. Defaults to true
      bool_filters: "all_but_games"   # OPTIONAL. Can filter out non-games by various dat categories. If you want to
                                                  include e.g. just games and applications, set to
                                                  ['games', 'applications']. Defaults to 'all_but_games', which will
                                                  remove everything except games

    discord:                          # OPTIONAL. If defined, supply a webhook URL so that ROMSearch can post Discord
      webhook_url: [webhook_url]      #           notifications

Sample
======

.. literalinclude:: ../../romsearch/configs/sample_config.yml