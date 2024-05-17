#############
ROMSearch GUI
#############

ROMSearch features a GUI mode, which can be downloaded from the
`GitHub release page <https://github.com/bbtufty/romsearch/releases/latest>`_. Download the .exe file and place in a
folder of your choice. Note that currently this only works for windows, for Mac and Linux we suggest using the pip
version within ``python``.

**On first run, Windows may complain about the file. Just run anyway, the file is safe.**

When opening up the ROMSearch GUI, you will first see a terminal window. Do not close this! It'll output information
as ROMSearch runs, which can be handy to check where things are. The main window will also open up, which will look
something like this:

.. image:: ../images/config_main.png

You can exit ROMSearch using the button in the bottom left, or run ROMSearch using the button on the bottom right. By
default, it will load in sensible settings but you will need to add in the platforms you care about.

Creating a config file
----------------------

The first thing you'll want to do is create a configuration file. You can do this either by going
``File->New config file`` or ``Ctrl-N``. Save with ``File->Save config file`` or ``Ctrl-S``

Loading a config file
---------------------

If you have a pre-existing config file, ROMSearch will load this upon opening. Or, if you have another you'd like to
load you can do so by ``File->Load config file`` or ``Ctrl-O``.

.. toctree::
  :glob:
  :titlesonly:
  :maxdepth: 2

  config_main
  config_platforms
  config_regions_languages
  config_includes_excludes
  config_modules
