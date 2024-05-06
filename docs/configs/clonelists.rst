##########
clonelists
##########

ROMSearch can include curated clonelists to merge into its own dupes. Currently, this is only for ``retool``, but
there is flexibility to add others in the future.

Syntax: ::

    url: "url"              # Base url to pull files from

    [platform]: [filename]  # Filename for the platform-specific clonelist

retool
======

.. literalinclude:: ../../romsearch/configs/clonelists/retool.yml
