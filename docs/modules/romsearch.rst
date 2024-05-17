#########
ROMSearch
#########

This is the main part that controls the various other modules. It essentially calls everything (given user preferences),
and so while it doesn't really do all that much on its own, is the interface to everything else.

ROMSearch has 2 modes, the default will parse from the .dat file then download relevant files, to minimize disc space
used (`filter_then_download`). For completionists/data hoarders, there's also a `download_then_filter` option, which
will download and then filter from the downloaded files.

For more details on the ROMSearch arguments, see the :doc:`config file documentation <../configs/config>`.

API
===

.. autoclass:: romsearch.ROMSearch
    :no-index:
    :members:
    :undoc-members:
