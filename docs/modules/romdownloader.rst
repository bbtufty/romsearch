#############
ROMDownloader
#############

The ROMDownloader uses ``rclone`` to sync files from a remote (or local) location to be used in other steps.
For instructions on how to set up ``rclone``, see their documentation at `Rclone <https://rclone.org/>`_.

If using the default ``filter_then_download`` mode, ROMDownloader will use rclone copy to copy files and then delete
extraneous files from the raw directory at the end. For ``download_then_filter`` it will use rclone sync to do a full
sync, and then automatically delete files afterwards.

ROMDownloader also has optional Discord integration, which will print out files downloaded or deleted at the end
of each run.

For more details on the ROMDownloader arguments, see the :doc:`config file documentation <../configs/config>`.

API
===

.. autoclass:: romsearch.ROMDownloader
    :no-index:
    :members:
    :undoc-members:
