#############
ROMDownloader
#############

The ROMDownloader uses ``rclone`` to sync files from a remote (or local) location to be used in other steps.
For instructions on how to set up ``rclone``, see their documentation at `Rclone <https://rclone.org/>`_.

ROMDownloader also has optional Discord integration, which will print out files downloaded or deleted at the end
of each run.

For more details on the ROMDownloader arguments, see the :doc:`config file documentation <../configs/config>`.

API
===

.. autoclass:: romsearch.ROMDownloader
    :no-index:
    :members:
    :undoc-members:
