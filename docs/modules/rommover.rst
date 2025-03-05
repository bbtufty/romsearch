########
ROMMover
########

ROMMover will move the final chosen ROM files to a clean directory structure, optionally unzipping files along the way.

If multi-disc handling is enabled, then for multi-disc games files will be moved to a hidden folder (e.g.
``.Final Fantasy VII (USA)`` within the main game folder), and an m3u playlist file will be created to point at those
files.

If a patch file is found and ROMPatcher is turned on, then the file will also be patched at this stage.

For more details on the ROMMover arguments, see the :doc:`config file documentation <../configs/config>`.

API
===

.. autoclass:: romsearch.ROMMover
    :no-index:
    :members:
    :undoc-members: