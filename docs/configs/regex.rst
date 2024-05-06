#####
regex
#####

The ``regex.yml`` file controls how filenames are parsed using regex rules.

Syntax: ::

    [name]:                          # Name of the group
      pattern: [pattern]             # Regex matching pattern
      type: ["str", "list", "bool"]  # OPTIONAL. How to parse this match. If "list", a list of possible values needs
                                       to be defined in the config defaults. If "str", will pull out the string of
                                       the regex match. If bool, if the pattern is found within the filename will be
                                       set True, else False. Defaults to "bool"
      flags: ["I", "NOFLAG"]         # OPTIONAL. Flags to pass to regex. "I" indicates ignorecase, "NOFLAG" means no
                                       flags. Defaults to "I"
      group: [group]                 # OPTIONAL. Regex patterns can be grouped together into a single overarching group.
                                       If not set, will not group
      search_tags: [True, False]     # OPTIONAL. If False, will search the whole string instead of tags within the file.
                                       Defaults to True

Full file
=========

.. literalinclude:: ../../romsearch/configs/regex.yml