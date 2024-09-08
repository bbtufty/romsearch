########
RAHasher
########

The RAHasher will download a list of compatible ROM hashes from RetroAchievements to flag ROMs that have
achievements.

This requires API access, so you need to supply your RA username and API key. For how to do this, see
`this page <https://api-docs.retroachievements.org/#api-access>`_. Because GetGameList is heavy on the API,
there is a cache implemented that by default will only query the full game list once a month. If you need
to change this, you can with ``cache_period``, but do so at your own risk!

For more details on the RAHasher arguments, see the :doc:`config file documentation <../configs/config>`.

API
===

.. autoclass:: romsearch.RAHasher
    :no-index:
    :members:
    :undoc-members: