#############
ROMAssociator
#############

The ROMAssociator matches up files to games, potentially de-duping and assigning retool filters. It does this by
checking the filename against potential game names, and assigning them to an overall association. If the retool dupe
list has more complicated filters (see their description at
`https://unexpectedpanda.github.io/retool/contribute-clone-lists-variants-filters/
<https://unexpectedpanda.github.io/retool/contribute-clone-lists-variants-filters/>`_), then it will also parse through
these as appropriate.

ROMAssociator has no user-configurable arguments.

API
===

.. autoclass:: romsearch.ROMAssociator
    :no-index:
    :members:
    :undoc-members: