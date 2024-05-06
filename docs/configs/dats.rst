####
dats
####

ROMSearch can pull in dat files (either locally or automatically). Currently, this works for "Redump" and "No-Intro",
but can be easily expanded if necessary.

Syntax: ::

    url: "url"                      # OPTIONAL. Base url to build request from

    [platform]:                     # Name of the platform
      web_mapping: [web_mapping]    # OPTIONAL. If url is defined above, this is used to build the request
      file_mapping: [file_mapping]  # Name style for the file

No-Intro
========

.. literalinclude:: ../../romsearch/configs/dats/no-intro.yml

Redump
======

.. literalinclude:: ../../romsearch/configs/dats/redump.yml
