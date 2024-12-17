######
config
######

The ``config.yml`` file defines how ROMSearch will do the run. As such, it has quite a number of options.

As a note on includes, this will match something from the start of the string. So "Game Title VII" would include
"Game Title VII", "Game Title VIII", but not "Game Title Anthology - Game Title VII", for example.

Syntax: ::

    dirs:
      raw_dir: [raw_dir]                # Raw directory to download ROM files using ROMDownloader
      rom_dir: [rom_dir]                # Final output directory for ROMs. Will automatically subdivide by platform
      patch_dir: [patch_dir]            # Directory for patch files. Will divide up by game
      ra_hash_dir: [ra_hash_dir]        # Directory for parsed RA platform hashes
      dat_dir: [dat_dir]                # Directory to place raw .dat files
      parsed_dat_dir: [parsed_dat_dir]  # Directory to place parsed .dat files, as well as clonelists
      dupe_dir: [dupe_dir]              # Directory to place dupe files
      log_dir: [log_dir]                # Directory to place logs
      cache_dir: [cache_dir]            # Directory to place cache files

    platforms:                          # List of platforms to download ROMs for
      - [platform]

    region_preferences:                 # List of regions, in preference order
      - [most_preferred_region]
      - [next_preferred_region]

    language_preferences:               # List of languages, in preference order
      - [most_preferred_language]
      - [next_preferred_language]

    include_games:                      # OPTIONAL. Use this to trim down the number of ROMs downloaded
      [platform]:
        - [game]

    romsearch:                          # ROMSearch specific options
      method: 'filter_then_download'    # OPTIONAL. Method to use, option are 'filter_then_download', or
                                        #           'download_then_filter'. Defaults to 'filter_then_download'
      run_romdownloader: true           # OPTIONAL. Whether to run ROMDownloader. Defaults to true
      run_rahasher: false               # OPTIONAL. Whether to run RAHasher. Defaults to false
      run_datparser: true               # OPTIONAL. Whether to run DATParser. Defaults to true
      run_dupeparser: true              # OPTIONAL. Whether to run DupeParsed. Defaults to true
      run_romchooser: true              # OPTIONAL. Whether to run ROMChooser. Defaults to true
      run_rompatcher: false             # OPTIONAL. Whether to run ROMPatcher. Defaults to false
      run_rommover: true                # OPTIONAL. Whether to run ROMMover. Defaults to true
      dry_run: false                    # OPTIONAL. Set to true to not make any changes to filesystem. Defaults to false

    romdownloader:                      # ROMDownloader specific options
      dry_run: false                    # OPTIONAL. Set to true to not make any changes to filesystem. Defaults to false
      remote_name: 'rclone_remote'      # Rclone remote name
      use_absolute_url: false           # OPTIONAL. If true, will assume the path is an absolute URL for the rclone
                                        #           remote. Set to false if using an HTTP remote!
      sync_all: false                   # OPTIONAL. If true, will download everything that rclone finds. Set to false to
                                        #           use the include_games above

    rahasher:                           # RAHasher specific options
      username: "user"                  # RA username
      api_key: "1234567890abcde"        # RA API key
      cache_period: 30                  # Cache period for GameList in days. Since this is a heavy API operation, RA
                                        # suggests caching this aggressively. Defaults to 30

    dupeparser:                         # DupeParser specific options
      use_retool: true                  # OPTIONAL. Whether to use retool clonelists or not. Defaults to true

    gamefinder:                         # GameFinder specific options
      filter_dupes: true                # OPTIONAL. Whether to filter dupes or not. Defaults to true

    romparser:                          # ROMParser specific options
      use_filename: true                # OPTIONAL. Whether to parse properties from filename. Defaults to true
      use_dat: true                     # OPTIONAL. Whether to parse properties from .dat files. Defaults to true
      use_retool: true                  # OPTIONAL. Whether to parse properties from retool files. Defaults to true
      use_ra_hashes: false              # OPTIONAL. Whether to parse achievements from RA. Defaults to false

    romchooser:                         # ROMChooser specific options
      dry_run: false                    # OPTIONAL. Set to true to not make any changes to filesystem. Defaults to false
      use_best_version: true            # OPTIONAL. Whether to choose only what ROMChooser decides is the best version.
                                        #           Defaults to true
      filter_regions: true              # OPTIONAL. Whether to filter by region or not. Defaults to true
      filter_languages: true            # OPTIONAL. Whether to filter by language or not. Defaults to true
      bool_filters: "all_but_games"     # OPTIONAL. Can filter out non-games by various dat categories. If you want to
                                        #           include e.g. just games and applications, set to
                                        #           ['games', 'applications']. Defaults to 'all_but_games', which will
                                        #           remove everything except games

    rompatcher:                                # ROMPatcher specific options
      xdelta_path: [path_to_xdelta]            # OPTIONAL. This is where xdelta is located on your filesystem
      rompatcher_js_path: [path_to_rompatcher] # OPTIONAL. This is where RomPatcher.js is located on your filesystem

    discord:                            # OPTIONAL. If defined, supply a webhook URL so that ROMSearch can post Discord
      webhook_url: [webhook_url]        #           notifications

    logger:
      level: info                       # OPTIONAL. If defined, can set the log level to be printed to terminal and
                                        #           logs

Sample
======

.. literalinclude:: ../../romsearch/configs/sample_config.yml