Text-Unidecode
==============

.. image:: https://travis-ci.org/kmike/text-unidecode.svg?branch=master
    :target: https://travis-ci.org/kmike/text-unidecode
    :alt: Build Status

text-unidecode is the most basic port of the
`Text::Unidecode <http://search.cpan.org/~sburke/Text-Unidecode-0.04/lib/Text/Unidecode.pm>`_
Perl library.

There are other Python ports of Text::Unidecode (unidecode_
and isounidecode_). unidecode_ is GPL; isounidecode_ uses too much memory,
and it didn't support Python 3 when this package was created.

You can redistribute it and/or modify this port under the terms of either:

* `Artistic License`_, or
* GPL or GPLv2+

If you're OK with GPL-only, use unidecode_ (it has better memory usage and
better transliteration quality).

``text-unidecode`` supports Python 2.7 and 3.4+.

.. _unidecode: https://pypi.python.org/pypi/Unidecode/
.. _isounidecode: https://pypi.python.org/pypi/isounidecode/
.. _Artistic License: https://opensource.org/licenses/Artistic-Perl-1.0

Installation
------------

::

    pip install text-unidecode

Usage
-----

::

    >>> from text_unidecode import unidecode
    >>> unidecode(u'какой-то текст')
    'kakoi-to tekst'


