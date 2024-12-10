############
Known Issues
############

* For very long filenames in Windows, there may be an error in moving files due to the length of the filename.

  * Enabling long paths will fix this. In the Registry Editor, set
    ``HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem\LongPathsEnabled`` to 1.

* In GameFinder, includes/excludes can cause some unexpected behavior since it will also search through duplicate files.
  For example, having an include of "Crash Bandicoot" for the PS1 will also grab "Crash Bash" and
  "CTR - Crash Team Racing" since at least one of their duplicates starts with "Crash Bandicoot".

* Currently, the code is not aware of ``retool``'s supersets or compilations array.

* Occasionally, multiple ROMs will be found with the same priority.

  * This will be improved with more regex flags in future releases
