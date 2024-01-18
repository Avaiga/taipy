# -*- coding: utf-8 -*-


def add_uppercase_char(char_list):
    """ Given a replacement char list, this adds uppercase chars to the list """

    for item in char_list:
        char, xlate = item
        upper_dict = char.upper(), xlate.capitalize()
        if upper_dict not in char_list and char != upper_dict[0]:
            char_list.insert(0, upper_dict)
        return char_list


# Language specific pre translations
# Source awesome-slugify

_CYRILLIC = [      # package defaults:
    (u'ё', u'e'),    # io / yo
    (u'я', u'ya'),   # ia
    (u'х', u'h'),    # kh
    (u'у', u'y'),    # u
    (u'щ', u'sch'),  # sch
    (u'ю', u'u'),    # iu / yu
]
CYRILLIC = add_uppercase_char(_CYRILLIC)

_GERMAN = [        # package defaults:
    (u'ä', u'ae'),   # a
    (u'ö', u'oe'),   # o
    (u'ü', u'ue'),   # u
]
GERMAN = add_uppercase_char(_GERMAN)

_GREEK = [         # package defaults:
    (u'χ', u'ch'),   # kh
    (u'Ξ', u'X'),    # Ks
    (u'ϒ', u'Y'),    # U
    (u'υ', u'y'),    # u
    (u'ύ', u'y'),
    (u'ϋ', u'y'),
    (u'ΰ', u'y'),
]
GREEK = add_uppercase_char(_GREEK)

# Pre translations
PRE_TRANSLATIONS = CYRILLIC + GERMAN + GREEK
