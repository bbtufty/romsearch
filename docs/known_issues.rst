############
Known Issues
############

* In GameFinder, includes/excludes can cause some unexpected behavior since it will also search through duplicate files.
  For example, having an include of "Crash Bandicoot" for the PS1 will also grab "Crash Bash" and
  "CTR - Crash Team Racing" since at least one of their duplicates starts with "Crash Bandicoot".

* Currently, the code is not aware of ``retool``'s supersets or compilations array.

* Occasionally, multiple ROMs will be found with the same priority.

  * This will be improved with more regex flags in future releases
