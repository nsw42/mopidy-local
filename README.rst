*********************
Mopidy-Local for Piju
*********************

This is a fork of `mopidy-local`_ for the `PiJu`_ project.

.. _mopidy-local: https://github.com/mopidy/mopidy-local
.. _PiJu: https://github.com/nsw42/piju


The following changes have been made specific for PiJu, which might be too specialised to prevent them from being pushed upstream:

- Use mutagen to extract mp3 tags, so that the album release year can be honoured


Also, the following bug fixes and improvements, which need to be pushed upstream:

- Correct the logged number of tracks that need to be updated


Installation to a MacOS homebrew install of Mopidy
==================================================

Since this fork is not going to be released, ``pip install`` will not work. Instead, use a traditional ``setup.py``
installation, specifying the mopidy environment as the destination.

Precise version numbers of python and mopidy will vary, but the general principle is::

    /usr/local/opt/python@3.8/bin/python3.8 setup.py install --prefix /usr/local/Cellar/mopidy/3.0.2_1/libexec

Similarly, installing additional dependencies (``mutagen``) can be done with::

    /usr/local/opt/python\@3.8/libexec/bin/pip install --prefix=/usr/local/Cellar/mopidy/3.0.2_1/libexec mutagen
