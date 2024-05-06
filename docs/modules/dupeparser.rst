##########
DupeParser
##########

DupeParser generates a list of potential duplicate files based on name. It either does this via curated clonelists
(currently only retool), or via information in parsed .dat files.

If priorities are present in the retool clonelist, it will use these to prioritise particular release versions versus
others

For more details on the DupeParser arguments, see the :doc:`config file documentation <../configs/config>`.

API
===

.. autoclass:: romsearch.DupeParser
    :no-index:
    :members:
    :undoc-members: