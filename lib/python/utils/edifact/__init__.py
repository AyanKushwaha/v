
# :vim set fileencoding=latin-1:
# changelog{{{2
# [acosta:07/313@15:33] First implementation.
# [acosta:07/324@11:05] Split into several modules.
# }}}

"""
UN/EDIFACT

Generic building blocks for EDIFACT messages.
"""

import codecs
import re


# Will add newlines if set to True.
debug = False


# encodings =============================================================={{{1

# Level A Character Set
#=============================================================================
# Letters, upper case         A to Z
# Numerals                    0 to 9
# Space                       ' '
# Full stop                   .
# Comma                       ,
# Hyphen/minus sign           -
# Opening parentheses         (
# Closing parentheses         )
# Oblique stroke (slash)      /
# Equals sign                 =
#                                     Reserved for use as:
# Apostrophe                  '       segment terminator
# Plus sign                   +       segment tag and data element separator
# Colon                       :       component data element separator
# Question mark               ?       release character
#                                     ? immediately preceding one of the
#                                     characters '+:? restores their normal
#                                     meaning.  E.g. 10?+10=20 means 10+10=20.
#                                     Question mark is represented by ??.
# The following characters are part of the level A character set but cannot be
# used internationally in telex transmissions:
# Exclamation mark            !
# Quotation mark              "
# Percentage sign             %
# Ampersand                   &
# Asterisk                    *
# Semi-colon                  ;
# Less-than sign              <
# Greater than sign           >

# Level B character set
# This character set is not intended for transmission to telex machines.
#=============================================================================
# Letters, upper case         A to Z
# Letters, lower case         a to z
# Numerals                    0 to 9
# Space character             ' '
# Full stop                   .
# Comma                       ,
# Hyphen/minus sign           -
# Opening parentheses         (
# Closing parentheses         )
# Oblique stroke (slash)      /
# Apostrophe                  '
# Plus sign                   +
# Colon                       :
# Equals sign                 =
# Question mark               ?
# Exclamation mark            !
# Quotation mark              "
# Percentage sign             %
# Ampersand                   &
# Asterisk                    *
# Semi-colon                  ;
# Less-than sign              <
# Greater-than sign           >
#   Information separator IS 4 segment terminator
#   Information separator IS 3 data element separator
#   Information separator IS 1 component data element separator

# NOTE there are other possible character sets: UNOC, UNOD, ...

class TranslationDict(dict):
    """Return default value if translation not found."""
    def __init__(self, charset=(), map={}, default=None):
        dict.__init__(self, map)
        for c in charset:
            self[ord(c)] = unicode(c)
        self.default = default

    def __getitem__(self, c):
        try:
            return dict.__getitem__(self, c)
        except KeyError:
            self[c] = self.default
            return self.default


# In Level A and Level B
letters_upper_case = set((
    u'\N{LATIN CAPITAL LETTER A}',
    u'\N{LATIN CAPITAL LETTER B}',
    u'\N{LATIN CAPITAL LETTER C}',
    u'\N{LATIN CAPITAL LETTER D}',
    u'\N{LATIN CAPITAL LETTER E}',
    u'\N{LATIN CAPITAL LETTER F}',
    u'\N{LATIN CAPITAL LETTER G}',
    u'\N{LATIN CAPITAL LETTER H}',
    u'\N{LATIN CAPITAL LETTER I}',
    u'\N{LATIN CAPITAL LETTER J}',
    u'\N{LATIN CAPITAL LETTER K}',
    u'\N{LATIN CAPITAL LETTER L}',
    u'\N{LATIN CAPITAL LETTER M}',
    u'\N{LATIN CAPITAL LETTER N}',
    u'\N{LATIN CAPITAL LETTER O}',
    u'\N{LATIN CAPITAL LETTER P}',
    u'\N{LATIN CAPITAL LETTER Q}',
    u'\N{LATIN CAPITAL LETTER R}',
    u'\N{LATIN CAPITAL LETTER S}',
    u'\N{LATIN CAPITAL LETTER T}',
    u'\N{LATIN CAPITAL LETTER U}',
    u'\N{LATIN CAPITAL LETTER V}',
    u'\N{LATIN CAPITAL LETTER W}',
    u'\N{LATIN CAPITAL LETTER X}',
    u'\N{LATIN CAPITAL LETTER Y}',
    u'\N{LATIN CAPITAL LETTER Z}',
))

# In level B only
letters_lower_case = set((
    u'\N{LATIN SMALL LETTER A}',
    u'\N{LATIN SMALL LETTER B}',
    u'\N{LATIN SMALL LETTER C}',
    u'\N{LATIN SMALL LETTER D}',
    u'\N{LATIN SMALL LETTER E}',
    u'\N{LATIN SMALL LETTER F}',
    u'\N{LATIN SMALL LETTER G}',
    u'\N{LATIN SMALL LETTER H}',
    u'\N{LATIN SMALL LETTER I}',
    u'\N{LATIN SMALL LETTER J}',
    u'\N{LATIN SMALL LETTER K}',
    u'\N{LATIN SMALL LETTER L}',
    u'\N{LATIN SMALL LETTER M}',
    u'\N{LATIN SMALL LETTER N}',
    u'\N{LATIN SMALL LETTER O}',
    u'\N{LATIN SMALL LETTER P}',
    u'\N{LATIN SMALL LETTER Q}',
    u'\N{LATIN SMALL LETTER R}',
    u'\N{LATIN SMALL LETTER S}',
    u'\N{LATIN SMALL LETTER T}',
    u'\N{LATIN SMALL LETTER U}',
    u'\N{LATIN SMALL LETTER V}',
    u'\N{LATIN SMALL LETTER W}',
    u'\N{LATIN SMALL LETTER X}',
    u'\N{LATIN SMALL LETTER Y}',
    u'\N{LATIN SMALL LETTER Z}',
))

# In level A and level B
numerals = set((
    u'\N{DIGIT ZERO}',
    u'\N{DIGIT ONE}',
    u'\N{DIGIT TWO}',
    u'\N{DIGIT THREE}',
    u'\N{DIGIT FOUR}',
    u'\N{DIGIT FIVE}',
    u'\N{DIGIT SIX}',
    u'\N{DIGIT SEVEN}',
    u'\N{DIGIT EIGHT}',
    u'\N{DIGIT NINE}',
))

# In level A and B
set_1 = set((
    u'\N{SPACE}',
    u'\N{FULL STOP}',
    u'\N{COMMA}',
    u'\N{HYPHEN-MINUS}',
    u'\N{LEFT PARENTHESIS}',
    u'\N{RIGHT PARENTHESIS}',
    u'\N{SOLIDUS}',  # slash
    u'\N{EQUALS SIGN}',
))

# In level A and B, should be avoided for Telex transmissions.
set_2 = set((
    u'\N{EXCLAMATION MARK}',
    u'\N{QUOTATION MARK}',
    u'\N{PERCENT SIGN}',
    u'\N{AMPERSAND}',
    u'\N{ASTERISK}',
    u'\N{SEMICOLON}',
    u'\N{LESS-THAN SIGN}',
    u'\N{GREATER-THAN SIGN}',
))

# In level A and B, have to be escaped for level A
set_3 = set((
    u'\N{APOSTROPHE}',
    u'\N{PLUS SIGN}',
    u'\N{COLON}',
    u'\N{QUESTION MARK}',
))

# Level B only
set_4 = set((
    unicode(chr(0x001c)), # u'\N{INFORMATION SEPARATOR FOUR}',  # (file separator)
    unicode(chr(0x001d)), # u'\N{INFORMATION SEPARATOR THREE}', # (group separator)
    unicode(chr(0x001f)), # u'\N{INFORMATION SEPARATOR ONE}',   # (unit separator)
))


# "Special" translations, removes all diacritics
# The transformation takes care of:
# Basic Latin        (0000-007F)
# Latin-1 Supplement (0080-00FF)
# Latin Extended-A   (0100-017F)
# Other latin characters have special use only (phonetics, archeology, ...)
xlate_latin = {
    u'\N{LATIN CAPITAL LETTER AE}': 'Ae',
    u'\N{LATIN CAPITAL LETTER A WITH ACUTE}': 'A',
    u'\N{LATIN CAPITAL LETTER A WITH BREVE}': 'A',
    u'\N{LATIN CAPITAL LETTER A WITH CIRCUMFLEX}': 'A',
    u'\N{LATIN CAPITAL LETTER A WITH DIAERESIS}': 'Ae',
    u'\N{LATIN CAPITAL LETTER A WITH GRAVE}': 'A',
    u'\N{LATIN CAPITAL LETTER A WITH MACRON}': 'A',
    u'\N{LATIN CAPITAL LETTER A WITH OGONEK}': 'A',
    u'\N{LATIN CAPITAL LETTER A WITH RING ABOVE}': 'Aa',
    u'\N{LATIN CAPITAL LETTER A WITH TILDE}': 'A',
    u'\N{LATIN CAPITAL LETTER C WITH ACUTE}': 'C',
    u'\N{LATIN CAPITAL LETTER C WITH CARON}': 'C',
    u'\N{LATIN CAPITAL LETTER C WITH CEDILLA}': 'C',
    u'\N{LATIN CAPITAL LETTER C WITH CIRCUMFLEX}': 'C',
    u'\N{LATIN CAPITAL LETTER C WITH DOT ABOVE}': 'C',
    u'\N{LATIN CAPITAL LETTER D WITH CARON}': 'D',
    u'\N{LATIN CAPITAL LETTER D WITH STROKE}': 'D',
    u'\N{LATIN CAPITAL LETTER ENG}': 'N',
    u'\N{LATIN CAPITAL LETTER ETH}': 'D',
    u'\N{LATIN CAPITAL LETTER E WITH ACUTE}': 'E',
    u'\N{LATIN CAPITAL LETTER E WITH BREVE}': 'E',
    u'\N{LATIN CAPITAL LETTER E WITH CARON}': 'E',
    u'\N{LATIN CAPITAL LETTER E WITH CIRCUMFLEX}': 'E',
    u'\N{LATIN CAPITAL LETTER E WITH DIAERESIS}': 'E',
    u'\N{LATIN CAPITAL LETTER E WITH DOT ABOVE}': 'E',
    u'\N{LATIN CAPITAL LETTER E WITH GRAVE}': 'E',
    u'\N{LATIN CAPITAL LETTER E WITH MACRON}': 'E',
    u'\N{LATIN CAPITAL LETTER E WITH OGONEK}': 'E',
    u'\N{LATIN CAPITAL LETTER G WITH BREVE}': 'G',
    u'\N{LATIN CAPITAL LETTER G WITH CEDILLA}': 'G',
    u'\N{LATIN CAPITAL LETTER G WITH CIRCUMFLEX}': 'G',
    u'\N{LATIN CAPITAL LETTER G WITH DOT ABOVE}': 'G',
    u'\N{LATIN CAPITAL LETTER H WITH CIRCUMFLEX}': 'H',
    u'\N{LATIN CAPITAL LETTER H WITH STROKE}': 'H',
    u'\N{LATIN CAPITAL LETTER I WITH ACUTE}': 'I',
    u'\N{LATIN CAPITAL LETTER I WITH BREVE}': 'I',
    u'\N{LATIN CAPITAL LETTER I WITH CIRCUMFLEX}': 'I',
    u'\N{LATIN CAPITAL LETTER I WITH DIAERESIS}': 'I',
    u'\N{LATIN CAPITAL LETTER I WITH DOT ABOVE}': 'I',
    u'\N{LATIN CAPITAL LETTER I WITH GRAVE}': 'I',
    u'\N{LATIN CAPITAL LETTER I WITH MACRON}': 'I',
    u'\N{LATIN CAPITAL LETTER I WITH OGONEK}': 'I',
    u'\N{LATIN CAPITAL LETTER I WITH TILDE}': 'I',
    u'\N{LATIN CAPITAL LETTER J WITH CIRCUMFLEX}': 'J',
    u'\N{LATIN CAPITAL LETTER K WITH CEDILLA}': 'K',
    u'\N{LATIN CAPITAL LETTER L WITH ACUTE}': 'L',
    u'\N{LATIN CAPITAL LETTER L WITH CARON}': 'L',
    u'\N{LATIN CAPITAL LETTER L WITH CEDILLA}': 'L',
    u'\N{LATIN CAPITAL LETTER L WITH MIDDLE DOT}': 'L',
    u'\N{LATIN CAPITAL LETTER L WITH STROKE}': 'L',
    u'\N{LATIN CAPITAL LETTER N WITH ACUTE}': 'N',
    u'\N{LATIN CAPITAL LETTER N WITH CARON}': 'N',
    u'\N{LATIN CAPITAL LETTER N WITH CEDILLA}': 'N',
    u'\N{LATIN CAPITAL LETTER N WITH TILDE}': 'N',
    u'\N{LATIN CAPITAL LETTER O WITH ACUTE}': 'O',
    u'\N{LATIN CAPITAL LETTER O WITH BREVE}': 'O',
    u'\N{LATIN CAPITAL LETTER O WITH CIRCUMFLEX}': 'O',
    u'\N{LATIN CAPITAL LETTER O WITH DIAERESIS}': 'Oe',
    u'\N{LATIN CAPITAL LETTER O WITH DOUBLE ACUTE}': 'O',
    u'\N{LATIN CAPITAL LETTER O WITH GRAVE}': 'O',
    u'\N{LATIN CAPITAL LETTER O WITH MACRON}': 'O',
    u'\N{LATIN CAPITAL LETTER O WITH STROKE}': 'Oe',
    u'\N{LATIN CAPITAL LETTER O WITH TILDE}': 'O',
    u'\N{LATIN CAPITAL LETTER R WITH ACUTE}': 'R',
    u'\N{LATIN CAPITAL LETTER R WITH CARON}': 'R',
    u'\N{LATIN CAPITAL LETTER R WITH CEDILLA}': 'R',
    u'\N{LATIN CAPITAL LETTER S WITH ACUTE}': 'S',
    u'\N{LATIN CAPITAL LETTER S WITH CARON}': 'S',
    u'\N{LATIN CAPITAL LETTER S WITH CEDILLA}': 'S',
    u'\N{LATIN CAPITAL LETTER S WITH CIRCUMFLEX}': 'S',
    u'\N{LATIN CAPITAL LETTER THORN}': 'Th',
    u'\N{LATIN CAPITAL LETTER T WITH CARON}': 'T',
    u'\N{LATIN CAPITAL LETTER T WITH CEDILLA}': 'T',
    u'\N{LATIN CAPITAL LETTER T WITH STROKE}': 'T',
    u'\N{LATIN CAPITAL LETTER U WITH ACUTE}': 'U',
    u'\N{LATIN CAPITAL LETTER U WITH BREVE}': 'U',
    u'\N{LATIN CAPITAL LETTER U WITH CIRCUMFLEX}': 'U',
    u'\N{LATIN CAPITAL LETTER U WITH DIAERESIS}': 'Ue',
    u'\N{LATIN CAPITAL LETTER U WITH DOUBLE ACUTE}': 'U',
    u'\N{LATIN CAPITAL LETTER U WITH GRAVE}': 'U',
    u'\N{LATIN CAPITAL LETTER U WITH MACRON}': 'U',
    u'\N{LATIN CAPITAL LETTER U WITH OGONEK}': 'U',
    u'\N{LATIN CAPITAL LETTER U WITH RING ABOVE}': 'U',
    u'\N{LATIN CAPITAL LETTER U WITH TILDE}': 'U',
    u'\N{LATIN CAPITAL LETTER W WITH CIRCUMFLEX}': 'W',
    u'\N{LATIN CAPITAL LETTER Y WITH ACUTE}': 'Y',
    u'\N{LATIN CAPITAL LETTER Y WITH CIRCUMFLEX}': 'Y',
    u'\N{LATIN CAPITAL LETTER Y WITH DIAERESIS}': 'Y',
    u'\N{LATIN CAPITAL LETTER Z WITH ACUTE}': 'Z',
    u'\N{LATIN CAPITAL LETTER Z WITH CARON}': 'Z',
    u'\N{LATIN CAPITAL LETTER Z WITH DOT ABOVE}': 'Z',
    u'\N{LATIN CAPITAL LIGATURE IJ}': 'IJ',
    u'\N{LATIN CAPITAL LIGATURE OE}': 'Oe',
    u'\N{LATIN SMALL LETTER AE}': 'ae',
    u'\N{LATIN SMALL LETTER A WITH ACUTE}': 'a',
    u'\N{LATIN SMALL LETTER A WITH BREVE}': 'a',
    u'\N{LATIN SMALL LETTER A WITH CIRCUMFLEX}': 'a',
    u'\N{LATIN SMALL LETTER A WITH DIAERESIS}': 'ae',
    u'\N{LATIN SMALL LETTER A WITH GRAVE}': 'a',
    u'\N{LATIN SMALL LETTER A WITH MACRON}': 'a',
    u'\N{LATIN SMALL LETTER A WITH OGONEK}': 'a',
    u'\N{LATIN SMALL LETTER A WITH RING ABOVE}': 'aa',
    u'\N{LATIN SMALL LETTER A WITH TILDE}': 'a',
    u'\N{LATIN SMALL LETTER C WITH ACUTE}': 'c',
    u'\N{LATIN SMALL LETTER C WITH CARON}': 'c',
    u'\N{LATIN SMALL LETTER C WITH CEDILLA}': 'c',
    u'\N{LATIN SMALL LETTER C WITH CIRCUMFLEX}': 'c',
    u'\N{LATIN SMALL LETTER C WITH DOT ABOVE}': 'c',
    u'\N{LATIN SMALL LETTER DOTLESS I}': 'i',
    u'\N{LATIN SMALL LETTER D WITH CARON}': 'd',
    u'\N{LATIN SMALL LETTER D WITH STROKE}': 'd',
    u'\N{LATIN SMALL LETTER ENG}': 'n',
    u'\N{LATIN SMALL LETTER ETH}': 'd',
    u'\N{LATIN SMALL LETTER E WITH ACUTE}': 'e',
    u'\N{LATIN SMALL LETTER E WITH BREVE}': 'e',
    u'\N{LATIN SMALL LETTER E WITH CARON}': 'e',
    u'\N{LATIN SMALL LETTER E WITH CIRCUMFLEX}': 'e',
    u'\N{LATIN SMALL LETTER E WITH DIAERESIS}': 'e',
    u'\N{LATIN SMALL LETTER E WITH DOT ABOVE}': 'e',
    u'\N{LATIN SMALL LETTER E WITH GRAVE}': 'e',
    u'\N{LATIN SMALL LETTER E WITH MACRON}': 'e',
    u'\N{LATIN SMALL LETTER E WITH OGONEK}': 'e',
    u'\N{LATIN SMALL LETTER G WITH BREVE}': 'g',
    u'\N{LATIN SMALL LETTER G WITH CEDILLA}': 'g',
    u'\N{LATIN SMALL LETTER G WITH CIRCUMFLEX}': 'g',
    u'\N{LATIN SMALL LETTER G WITH DOT ABOVE}': 'g',
    u'\N{LATIN SMALL LETTER H WITH CIRCUMFLEX}': 'h',
    u'\N{LATIN SMALL LETTER H WITH STROKE}': 'h',
    u'\N{LATIN SMALL LETTER I WITH ACUTE}': 'i',
    u'\N{LATIN SMALL LETTER I WITH BREVE}': 'i',
    u'\N{LATIN SMALL LETTER I WITH CIRCUMFLEX}': 'i',
    u'\N{LATIN SMALL LETTER I WITH DIAERESIS}': 'i',
    u'\N{LATIN SMALL LETTER I WITH GRAVE}': 'i',
    u'\N{LATIN SMALL LETTER I WITH MACRON}': 'i',
    u'\N{LATIN SMALL LETTER I WITH OGONEK}': 'i',
    u'\N{LATIN SMALL LETTER I WITH TILDE}': 'i',
    u'\N{LATIN SMALL LETTER J WITH CIRCUMFLEX}': 'j',
    u'\N{LATIN SMALL LETTER K WITH CEDILLA}': 'k',
    u'\N{LATIN SMALL LETTER L WITH ACUTE}': 'l',
    u'\N{LATIN SMALL LETTER L WITH CARON}': 'l',
    u'\N{LATIN SMALL LETTER L WITH CEDILLA}': 'l',
    u'\N{LATIN SMALL LETTER L WITH MIDDLE DOT}': 'l',
    u'\N{LATIN SMALL LETTER L WITH STROKE}': 'l',
    u'\N{LATIN SMALL LETTER N PRECEDED BY APOSTROPHE}': 'n',
    u'\N{LATIN SMALL LETTER N WITH ACUTE}': 'n',
    u'\N{LATIN SMALL LETTER N WITH CARON}': 'n',
    u'\N{LATIN SMALL LETTER N WITH CEDILLA}': 'n',
    u'\N{LATIN SMALL LETTER N WITH TILDE}': 'n',
    u'\N{LATIN SMALL LETTER O WITH ACUTE}': 'o',
    u'\N{LATIN SMALL LETTER O WITH BREVE}': 'o',
    u'\N{LATIN SMALL LETTER O WITH CIRCUMFLEX}': 'o',
    u'\N{LATIN SMALL LETTER O WITH DIAERESIS}': 'oe',
    u'\N{LATIN SMALL LETTER O WITH DOUBLE ACUTE}': 'o',
    u'\N{LATIN SMALL LETTER O WITH GRAVE}': 'o',
    u'\N{LATIN SMALL LETTER O WITH MACRON}': 'o',
    u'\N{LATIN SMALL LETTER O WITH STROKE}': 'oe',
    u'\N{LATIN SMALL LETTER O WITH TILDE}': 'o',
    u'\N{LATIN SMALL LETTER R WITH ACUTE}': 'r',
    u'\N{LATIN SMALL LETTER R WITH CARON}': 'r',
    u'\N{LATIN SMALL LETTER R WITH CEDILLA}': 'r',
    u'\N{LATIN SMALL LETTER SHARP S}': 'ss',
    u'\N{LATIN SMALL LETTER S WITH ACUTE}': 's',
    u'\N{LATIN SMALL LETTER S WITH CARON}': 's',
    u'\N{LATIN SMALL LETTER S WITH CEDILLA}': 's',
    u'\N{LATIN SMALL LETTER S WITH CIRCUMFLEX}': 's',
    u'\N{LATIN SMALL LETTER THORN}': 'th',
    u'\N{LATIN SMALL LETTER T WITH CARON}': 't',
    u'\N{LATIN SMALL LETTER T WITH CEDILLA}': 't',
    u'\N{LATIN SMALL LETTER T WITH STROKE}': 't',
    u'\N{LATIN SMALL LETTER U WITH ACUTE}': 'u',
    u'\N{LATIN SMALL LETTER U WITH BREVE}': 'u',
    u'\N{LATIN SMALL LETTER U WITH CIRCUMFLEX}': 'u',
    u'\N{LATIN SMALL LETTER U WITH DIAERESIS}': 'ue',
    u'\N{LATIN SMALL LETTER U WITH DOUBLE ACUTE}': 'u',
    u'\N{LATIN SMALL LETTER U WITH GRAVE}': 'u',
    u'\N{LATIN SMALL LETTER U WITH MACRON}': 'u',
    u'\N{LATIN SMALL LETTER U WITH OGONEK}': 'u',
    u'\N{LATIN SMALL LETTER U WITH RING ABOVE}': 'u',
    u'\N{LATIN SMALL LETTER U WITH TILDE}': 'u',
    u'\N{LATIN SMALL LETTER W WITH CIRCUMFLEX}': 'w',
    u'\N{LATIN SMALL LETTER Y WITH ACUTE}': 'y',
    u'\N{LATIN SMALL LETTER Y WITH CIRCUMFLEX}': 'y',
    u'\N{LATIN SMALL LETTER Y WITH DIAERESIS}': 'y',
    u'\N{LATIN SMALL LETTER Z WITH ACUTE}': 'z',
    u'\N{LATIN SMALL LETTER Z WITH CARON}': 'z',
    u'\N{LATIN SMALL LETTER Z WITH DOT ABOVE}': 'z',
    u'\N{LATIN SMALL LIGATURE IJ}': 'ij',
    u'\N{LATIN SMALL LIGATURE OE}': 'oe',
}



class BasicEncoding:
    """Base class for the encodings that are implemented here (UNOA, UNOB,
    "MRZ")."""

    enc_name = None

    class Codec(codecs.Codec):
        def __init__(self, enc_name):
            self.enc_name = enc_name

        def encode(self, input, errors='ignore'):
            return codecs.charmap_encode(input, errors, encodings[self.enc_name])

        def decode(self, input, errors='ignore'):
            return codecs.charmap_decode(input, errors, decodings[self.enc_name])


    class StreamWriter(Codec, codecs.StreamWriter):
        pass


    class StreamReader(Codec, codecs.StreamReader):
        pass


    @classmethod
    def getregentry(cls):
        return (cls.Codec(cls.enc_name).encode, cls.Codec(cls.enc_name).decode,
                cls.StreamReader, cls.StreamWriter)


class UNOA(BasicEncoding):

    enc_name = 'UNOA'

    class Decoding(TranslationDict):
        """Takes care of most latin characters, but no special translation for
        control characters."""

        allowed_characters = (letters_upper_case | numerals | set_1 | set_2 | set_3)

        def __init__(self):
            TranslationDict.__init__(self, charset=self.allowed_characters)
            # Translate lower case to upper case
            for c in letters_lower_case:
                self[ord(c)] = unicode(c.upper())
            # Translate latin characters with diacritics according to table
            for c in xlate_latin:
                self[ord(c)] = unicode(xlate_latin[c].upper())
            # Escape characters in set_3
            for c in set_3:
                self[ord(c)] = unicode('?' + c)


class UNOB(BasicEncoding):

    enc_name = 'UNOB'

    class Decoding(TranslationDict):
        """UNOB Decoding dictionary. No translation for control characters."""

        allowed_characters = (letters_upper_case | letters_lower_case | numerals |
            set_1 | set_2 | set_3 | set_4)

        def __init__(self):
            TranslationDict.__init__(self, charset=self.allowed_characters)
            for c in xlate_latin:
                self[ord(c)] = unicode(xlate_latin[c])


class MRZ(BasicEncoding):
    """MRZ, Machine Readable Zone, see ICAO 9303 Part 3.  There are some
    further restrictions on which characters are allowed in the MRZ of a travel
    document.  This encoding is even more restrictive than level A, only upper
    case letters, numerals and space are allowed."""

    enc_name = 'MRZ'

    class Decoding(TranslationDict):
        additionals = set((
            u'\N{SPACE}',
            u'\N{LESS-THAN SIGN}',
        ))

        # For MRZ (party names): Translate '-' -> ' '.
        xlate = {
            u'\N{HYPHEN-MINUS}': ' '
        }

        allowed_characters = (letters_upper_case | numerals | additionals)

        def __init__(self):
            TranslationDict.__init__(self, charset=self.allowed_characters)
            # Translate lower case to upper case
            for c in letters_lower_case:
                self[ord(c)] = unicode(c.upper())
            # Translate latin characters with diacritics according to table
            for c in xlate_latin:
                self[ord(c)] = unicode(xlate_latin[c].upper())
            # Change hyphen/dash/minus to space
            for c in self.xlate:
                self[ord(c)] = unicode(self.xlate[c])


def _registry(encoding):
    if encoding == 'unoa':
        return UNOA.getregentry()
    elif encoding == 'unob':
        return UNOB.getregentry()
    elif encoding == 'mrz':
        return MRZ.getregentry()
    else:
        return None


codecs.register(_registry)


decodings = {
    'UNOA': UNOA.Decoding(),
    'UNOB': UNOB.Decoding(),
    'MRZ': MRZ.Decoding(),
}


encodings = {}
for key in decodings:
    encodings[key] = codecs.make_encoding_map(decodings[key])


def latin1_to_edifact(s, level='UNOA'):
    """Transcribe string to format valid for transmission with EDIFACT.
    level can be one of 'UNOA', 'UNOB' and the home-brewed 'MRZ'."""
    if not level in decodings:
        raise ValueError("latin1_to_edifact(): level must be one of '%s'," % (decodings.keys(),))
    return str(str(s).decode('latin-1').translate(decodings[level]))


def alnum(s):
    """Used by document identities, only alpha-numeric characters (in
    uppercase) and numbers are allowed."""
    return latin1_to_edifact(s, level='MRZ').replace(' ', '').replace('<', '')


def mrz(sn, gn, maxlen=30, delimiter='<'):
    """Create a string valid for MRZ of passport/ID card.
    Example:
        print mrz("Bernadotte", "Carl Gustaf Folke Hubertus")
    would print:
        BERNADOTTE<<CARL<GUSTAF<FOLK<H
    """
    def adjust(l, i):
        z = -(i + 1)
        lenl = len(l) + sum([len(x) for x in l])
        if lenl > maxlen:
            lz = len(l[z]) - lenl + maxlen
            if lz < 1:
                l[z] = l[z][0]
                l = adjust(l, i + 1)
            else:
                l[z] = l[z][:lz]
                l = adjust(l, i)
        return l
    mrz_regexp = re.compile(r'[^A-Z]+')
    primary = mrz_regexp.split(str(sn.decode('mrz')))
    secondary = mrz_regexp.split(str(gn.decode('mrz')))
    lenp = len(primary)
    sngn = adjust(primary + secondary, 0)
    return delimiter.join(sngn[:lenp]) + (2 * delimiter) + delimiter.join(sngn[lenp:])


# Building blocks ========================================================{{{1

# Special ----------------------------------------------------------------{{{2
class Special(str):
    """Characters that have special meaning in UN/EDIFACT Level A messages."""
    def __new__(cls, level='UNOA'):
        if level == 'UNOB':
            return str.__new__(cls, "%c%c.? %c" % (0x001c, 0x001d, 0x001f))
        else:
            return str.__new__(cls, ":+.? '")

    def __init__(self, level='UNOA'):
        self.level = level

    @property
    def component(self):
        """Component data element separator: used to separate the component
        data elements in a composite data element."""
        return self[0]

    @property
    def data(self):
        """Data element separator: used to separate data elements in a
        segment."""
        return self[1]

    @property
    def decimal(self):
        """Separates integral and fractional parts of a decimal number."""
        return self[2]

    @property
    def release(self):
        """Release character: a character used to restore to its original
        meaning any character used as a syntactical separator. [ISO 9735]"""
        return self[3]

    @property
    def reserved(self):
        """Reserved for future use."""
        return self[4]

    @property
    def terminator(self):
        """Segment terminator: indicating the end of a segment."""
        return self[5]

    def escape(self, s):
        """
        Translate to Level A or B character sets.

        Use the release character '?' to restore to its original meaning any
        character used as a syntactical separator.

        NOTE!
        The release character is not counted as part of the length of any data
        element or component data within which it is transmitted.  Release
        characters can be inserted by program so that data can be input and output
        without any special manual requirements.

        /But (my assumption) it would count when calculating the whole message
        length?/
        """
        return latin1_to_edifact(s, self.level)


# special ----------------------------------------------------------------{{{2
special = Special()


# Elist ------------------------------------------------------------------{{{2
class Elist(list):
    """
    NOTE! Use Elist instead of list for "any" list, or the number of elements
    will be counted, not their sizes!

    Base class for the different data types.
    Supplies a size() method which can be used to calculate the message size.
    """
    def __init__(self, *a):
        list.__init__(self, a)

    def __str__(self):
        return ''.join([str(x) for x in self])

    def compress(self):
        i = len(self)
        for x in self[::-1]:
            i -= 1
            if x is None or x == '':
                del self[i]
            else:
                break
        for x in self:
            if hasattr(x, 'compress'):
                x.compress()

    def size(self):
        """ Calculate message, (group, ...) sizes. """
        def child_size(i):
            if hasattr(i, "size"):
                return i.size()
            else:
                return len(str(i))
        return sum([child_size(x) for x in self])


# ElistAttr --------------------------------------------------------------{{{2
class ElistAttr(Elist):
    """ Elist with attribute access. """
    def __init__(self, *a):
        Elist.__init__(self, *a)
        self.__template = ()

    def __call__(self, *a):
        """Init the template."""
        self.__template = a
        return self

    def __getattr__(self, name):
        try:
            return self[self.template_index(name)]
        except:
            return ''

    def __setattr__(self, name, value):
        if name.startswith('_') or name == 'tag':
            # avoid recursion
            object.__setattr__(self, name, value)
            return
        ix = self.template_index(name)
        if ix >= len(self):
            self.enlarge(ix + 1)
        self[ix] = value

    def __delattr__(self, name):
        ix = self.template_index(name)
        if ix > len(self):
            return
        self[ix] = ''
        self.compress()

    def enlarge(self, n=None):
        if n is None:
            new_len = self.template_len()
        else:
            new_len = n
        for ix in xrange(len(self), new_len):
            if self.is_composite(ix):
                self.append(Composite()(*self.template(ix)))
            else:
                self.append('')

    def is_composite(self, n):
        return not isinstance(self.__template[n], str)

    def template(self, n):
        return self.__template[n][1]

    def template_index(self, value):
        i = 0
        for x in self.__template:
            if self.is_composite(i):
                try:
                    if value == x[0]:
                        return i
                except:
                    if value == x:
                        return i
            elif value == x:
                return i
            i += 1
        raise AttributeError("Attribute %s does not exist for %s." %
                (value, self.__class__.__name__))

    def template_len(self):
        return len(self.__template)


# Segment ----------------------------------------------------------------{{{2
class Segment(ElistAttr):
    """
    A predefined and identified set of functionally related data elements
    values which are identified by their sequential positions within the set.
    A segment starts with a segment tag and ends with a segment terminator.  It
    can be a service segment or a user data segment.
    """
    def __init__(self, tag=None, *a):
        ElistAttr.__init__(self, *a)
        self.__tag = tag

    def __get_tag(self):
        if self.__tag is None:
            self.__tag = self.__class__.__name__
        return self.__tag

    def __set_tag(self, tag):
        self.__tag = tag

    tag = property(__get_tag, __set_tag)

    def __str__(self):
        def stringify(s):
            # If composite, the let the composite object translate, otherwise
            # we translate here.
            if isinstance(s, str):
                return special.escape(s)
            else:
                return str(s)
        return ''.join((str(self.tag), # To allow for tag being composite
            special.data, 
            special.data.join([stringify(x) for x in self]), 
            special.terminator))

    def size(self):
        return len(str(self))

    def enlarge(self, n=None):
        if n is None:
            new_len = self.template_len()
        else:
            new_len = n
        for ix in xrange(len(self), new_len):
            if self.is_composite(ix):
                self.append(Composite()(*self.template(ix)))
            else:
                self.append('')

    def __getattr__(self, name):
        ix = self.template_index(name)
        try:
            if self.is_composite(ix) and not isinstance(self[ix], Composite):
                self[ix] = Composite(self[ix])(*self.template(ix))
            return self[ix]
        except:
            if self.is_composite(ix):
                return self.Coupler(self, name, self.template(ix))
            else:
                return ''

    def __setattr__(self, name, value):
        if name.startswith('_') or name == 'tag':
            # avoid recursion
            object.__setattr__(self, name, value)
            return
        ix = self.template_index(name)
        if ix >= len(self):
            self.enlarge(ix + 1)
        if isinstance(value, Composite):
            value(*self.template(self.template_index(name)))
        self[ix] = value

    class Coupler(object):
        """Trick to be able to add parent data element on attribute access
        (getattr)."""
        def __init__(self, origin, name, template):
            self.__origin = origin
            self.__name = name
            self.__template = template

        def __setattr__(self, attr, value):
            if attr.startswith('_'):
                object.__setattr__(self, attr, value)
                return
            c = Composite()(*self.__template)
            setattr(c, attr, value)
            setattr(self.__origin, self.__name, c)


# ComplementarySegment ---------------------------------------------------{{{2
class ComplementarySegment(object):
    """For ending segments (UNZ, UNE, UNT, ...)."""
    def __init__(self, tag, partner, envelope):
        self.tag = tag
        self.partner = partner
        self.envelope = envelope

    def __len__(self):
        return len(str(self))

    def __str__(self):
        return special.data.join((self.tag,
            str(len(self.envelope)), 
            special.escape(self.partner.reference))) + special.terminator


# Composite --------------------------------------------------------------{{{2
class Composite(ElistAttr):
    """ A data element containing two or more component data elements. """
    def __str__(self):
        return special.component.join([special.escape(x) for x in self])

    def size(self):
        return len(str(self))

    def __getattr__(self, name):
        ix = self.template_index(name)
        try:
            #return special.escape(self[ix])
            return self[ix]
        except:
            return ''

    def __setattr__(self, name, value):
        if name.startswith('_'):
            # avoid recursion
            object.__setattr__(self, name, value)
            return
        ix = self.template_index(name)
        L = len(self)
        if ix >= L:
            self.extend((ix - L + 1) * [''])
        self[ix] = value


# SegmentTag -------------------------------------------------------------{{{2
class SegmentTag(Composite):
    """In case we use explicite notation (see guidelines 9.5.1 - 9.5.3).  A tag
    can consist of 10 component data elements. First is mandatory and contains
    the unique code to identify the segment. The following are conditional and
    can carry control numbers for repeating segments."""
    def __init__(self, tag):
        self('tag', 'level_1', 'level_2', 'level_3', 'level_4', 'level_5',
                'level_6', 'level_7', 'level_8', 'level_9')
        self.tag = tag


# Element ----------------------------------------------------------------{{{2
class Element(str):
    """ Simple data element, containing one value. """
    def __new__(cls, s):
        return str.__new__(cls, special.escape(s))


# Interchange ------------------------------------------------------------{{{2
class Interchange(Elist):
    """
    UNB .. UNZ
    Communication between partners in the form of a structured set of messages
    and service segments starting with an interchange control header and ending
    with an interchange control trailer.
    """
    def __init__(self, impl, *a, **k):
        self.una = impl.UNA()
        self.unb = impl.UNB(*a, **k)
        self.unz = impl.UNZ(self.unb, self)

    def size(self):
        return len(self.una) + self.unb.size() + Elist.size(self) + len(self.unz)

    def __str__(self):
        if debug:
            delim = '\n'
        else:
            delim = ''
        return delim.join([str(x) for x in [self.una, self.unb] + self + [self.unz]]) 


# FunctionalGroup --------------------------------------------------------{{{2
class FunctionalGroup(Elist):
    """
    UNG .. UNE
    One or more messages of the same type headed by a functional group header
    service segment and ending with a functional group trailer service segment.
    """
    def __init__(self, impl, *a, **k):
        self.ung = impl.UNG(*a, **k)
        self.une = impl.UNE(self.ung, self)

    def size(self):
        return self.ung.size() + Elist.size(self) + len(self.une)

    def __str__(self):
        if debug:
            delim = '\n'
        else:
            delim = ''
        return delim.join([str(x) for x in [self.ung] + self + [self.une]]) 


# Message ----------------------------------------------------------------{{{2
class Message(Elist):
    """
    UNH .. UNT
    An ordered series of characters intended to convey information (ISO
    2382/16) UN/EDIFACT: A set of segments in the order specified in a Message
    directory starting with the Message header and ending with the Message
    trailer.
    """
    def __init__(self, impl, *a, **k):
        self.unh = impl.UNH(*a, **k)
        self.unt = impl.UNT(self.unh, self)

    def __len__(self):
        return list.__len__(self) + 2

    def size(self):
        return self.unh.size() + Elist.size(self) + len(self.unt)

    def __str__(self):
        if debug:
            delim = '\n'
        else:
            delim = ''
        return delim.join([str(x) for x in [self.unh] + self + [self.unt]]) 


# EDIFACT base implementation ============================================{{{1
class EDIFACT(object):
    """
    SERVICE SEGMENTS SPECIFICATIONS  

    The full description of the data elements in the service segments is 
    part of ISO 7372 Trade Data Elements Directory (UNTDED).

    Legend:

    Ref.   The numeric reference tag for the data element as stated in ISO
           7372/UNTDED and, when preceded by S, reference for a composite data
           element used in service segments

    Name   Name of COMPOSITE DATA ELEMENT in capital letters
           Name of DATA ELEMENT in capital letters
           Name of Component data element in small letters

    Repr.  Data value representation:
           a       alphabetic characters
           n       numeric characters
           an      alpha-numeric characters
           a3      3 alphabetic characters, fixed length
           n3      3 numeric characters, fixed length
           an3     3 alpha-numeric characters, fixed length
           a..3    up to 3 alphabetic characters
           n..3    up to 3 numeric characters
           an..3   up to 3 alpha-numeric characters

           M       Mandatory element
           C       Conditional element.

           Note that a mandatory component data element in a conditional
           composite data element must appear when the composite data element
           is used

    Remarks IA    Interchange Agreement between interchanging partners
    """
    
    @classmethod
    def Message(cls, *a, **k):
        return Message(cls, *a, **k)

    @classmethod
    def Interchange(cls, *a, **k):
        return Interchange(cls, *a, **k)

    @classmethod
    def FunctionalGroup(cls, *a, **k):
        return FunctionalGroup(cls, *a, **k)

    class UNA(str):
        """
        UNA, Service String advice

        Function: To define the characters selected for use as delimiters and
        indicators in the rest of the interchange that follows:

        The specifications in the Service string advice take precedence over
        the specifications for delimiters etc. in segment UNB. See clause 4.

        When transmitted, the Service string advice must appear immediately
        before the Interchange Header (UNB) segment and begin with the upper
        case characters UNA immediately followed by the six characters selected
        by the sender to indicate, in sequence, the following functions:

        Repr.        Name                   Remarks

        an1    M     COMPONENT DATA
                     ELEMENT SEPARATOR
        an1    M     DATA ELEMENT SEPARATOR
        an1    M     DECIMAL NOTATION       Comma or full stop
        an1    M     RELEASE INDICATOR      If not used, insert
                                            space character
        an1    M     Reserved for future    Insert space character
                     use
        an1    M     SEGMENT TERMINATOR        

        UNA1 always ':'
        UNA2 always '+'
        UNA3 always '.'
        UNA4 always '?'
        UNA5 always ' ' (space, reserved for future use)
        UNA6 always "'" (single quote)
        """
        def __new__(cls):
            return str.__new__(cls, "UNA%s" % special)


    class UNB(Segment):
        """
        Segment: UNB, Interchange Header

        Function: To start, identify and specify an interchange

        Ref.   Repr.       Name                   Remarks

        S001           M   SYNTAX IDENTIFIER
        0001   a4      M   Syntax identifier      a3, upper case
                                                  Controlling Agency (e.g.
                                                  UNO=UN/ECE) and a1 stating
                                                  level (e.g. A)  (which
                                                  together give UNOA)
        0002   n1      M   Syntax version number  Increments 1 for each new
                                                  version. Shall be 2 to
                                                  indicate this version
        ___________________________________________________________________
        S002           M   INTERCHANGE SENDER
        0004   an..35  M   Sender identification  Code or name as specified
                                                  in IA
        0007   an..4   C   Partner identification Used with sender
                           code qualifier         identification code
        0008   an..14  C   Address for reverse
                           routing
        ___________________________________________________________________
        S003           M   INTERCHANGE RECIPIENT
        0010   an..35  M   Recipient              Code or name as
                           Identification         specified in IA
        0007   an..4   C   Partner identification Used with recipient
                           code qualifier         identification code
        0014   an..14  C   Routing address        If used, normally coded
                                                  sub-address for onward
                                                  routing
        ___________________________________________________________________

        S004           M   DATE/TIME OF PREPARATION
        0017   n6      M   Date                   YYMMDD
        0019   n4      M   Time                   HHMM
        ___________________________________________________________________
        0020   an..14  M   INTERCHANGE CONTROL    Unique reference
                           REFERENCE              assigned by sender
        ___________________________________________________________________
        S005           C   RECIPIENTS REFERENCE,
                           PASSWORD
        0022   an..14  M   Recipient's reference/ As specified in IA. May
                           password               be password to recipient's
                                                  system or to third party
                                                  network
        0025   an2     C   Recipient's reference/ If specified in IA
                           password qualifier
        ___________________________________________________________________
        0026   an..14  C   APPLICATION REFERENCE  Optionally message
                                                  identification if the
                                                  interchange contains only
                                                  one type of message
        ___________________________________________________________________
        0029   a1      C   PROCESSING PRIORITY    Used if specified in IA
                           CODE
        ___________________________________________________________________
        0031   n1      C   ACKNOWLEDGEMENT REQUEST   Set = 1 if sender
                                                  requests acknowledgement,
                                                  i.e.  UNB and UNZ segments
                                                  received and identified
        ___________________________________________________________________
        0032   an..35  C   COMMUNICATIONS         If used, to identify
                           AGREEMENT ID           type of communication
                                                  agreement controlling the
                                                  interchange, e.g.  Customs or
                                                  ECE agreement.  Code or name
                                                  as specified in IA
        ___________________________________________________________________
        0035   n1      C   TEST INDICATOR         Set = 1 if the interchange
                                                  is a test.  Otherwise not
                                                  used
        """
        def __init__(self, *a):
            """ Note: Some of the elements are composites. """
            Segment.__init__(self, 'UNB', *a)
            self(
                ('syntax', ('id', 'version')),
                ('sender', ('id', 'qual', 'routing')),
                ('recipient', ('id', 'qual', 'routing')),
                ('date_time', ('date', 'time')),
                'reference',
                ('password', ('password', 'qual')),
                'application',
                'priority',
                'ack_req',
                'agreement_id',
                'test_indicator',
            )


    class UNZ(ComplementarySegment):
        """
        Segment: UNZ, Interchange Trailer

        Function: To end and check the completeness of an interchange

        Ref.   Repr.       Name                   Remarks

        0036   n..6    M   INTERCHANGE CONTROL    The count of the number of
                           COUNT                  messages or, if used, the
                                                  number of functional groups
                                                  in the interchange.  One of
                                                  these counts shall appear.
        ___________________________________________________________________
        0020   an..14  M   INTERCHANGE CONTROL    Shall be identical to
                           REFERENCE              0020 in UNB
        """
        def __init__(self, unb, interchange):
            """ Will get count and reference from it's UNB "partner". """
            ComplementarySegment.__init__(self, 'UNZ', unb, interchange)


    class UNG(Segment):
        """
        Segment: UNG, Functional Group Header

        Function: To head, identify and specify a Functional Group

        Ref.   Repr.       Name                   Remarks

        0038   an..6   M   FUNCTIONAL GROUP       Identifies the one
                           IDENTIFICATION         message type in the
                                                  functional group
        ___________________________________________________________________
        S006           M   APPLICATION SENDER'S
                           IDENTIFICATION
        0040   an..35  M   Application sender's   Code or name identifying
                           identification         the division, department
                                                  etc. within the originating
                                                  sender's organization
        0007   an..4   C   Partner identification May be used if sender
                           code qualifier         identification is a code
        ___________________________________________________________________
        S007           M   APPLICATION RECIPIENTS
                           IDENTIFICATION
        0044   an..35  M   Recipient's            Code or name identifying
                           identification         the division,department
                                                  etc. within the recipients
                                                  organization for which the
                                                  group of messages is intended
        0007   an..4   C   Recipients             May be used if recipient
                           identification         identification is a code
                           qualifier
        ___________________________________________________________________
        S004           M   DATE/TIME OF PREPARATION
        0017   n6      M   Date                   YYMMDD
        0019   n4      M   Time                   HHMM
        ___________________________________________________________________
        0048   an..14  M   FUNCTIONAL GROUP       Unique reference number
                           REFERENCE NUMBER       assigned by sender's
                                                  division, department etc.
        ___________________________________________________________________
        0051   an..2   M   CONTROLLING AGENCY     Code to identify the agency
                                                  controlling the
                                                  specification, maintenance
                                                  and publication of the
                                                  message type
        ___________________________________________________________________
        S008           M   MESSAGE VERSION
        0052   an..3   M   Message version number Version number of the message
                                                  type the functional group
        0054   an..3   M   Message release number Release number within current
                                                  version number
        0057   an..6   C   Association assigned   A code assigned by the
                           Code                   association responsible for
                                                  the design and maintenance of
                                                  the type of message concerned
        ___________________________________________________________________
        0058   an..14  C   APPLICATION PASSWORD   Password to recepient's
                                                  division, department or
                                                  sectional system (if
                                                  required)
        """
        def __init__(self, *a):
            Segment.__init__(self, 'UNG', *a)
            self(
                'group_id',
                ('sender', ('id', 'qual')),
                ('recipient', ('id', 'qual')),
                ('date_time', ('date', 'time')),
                'reference',
                'agency',
                ('version', ('number', 'release', 'code')),
                'password',
            )


    class UNE(ComplementarySegment):
        """
        Segment: UNE, Functional Group Trailer

        Function: To end and check the completeness of a Functional Group

        Ref.   Repr.       Name                   Remarks

        0060   n..6    M   NUMBER OF MESSAGES     The count of the number of
                                                  messages in the functional
                                                  group
        ___________________________________________________________________
        0048   an..14  M   FUNCTIONAL GROUP       Shall be identical to
                           REFERENCE NUMBER       0048 in UNG
        """
        def __init__(self, ung, functionalgroup):
            ComplementarySegment.__init__(self, 'UNE', ung, functionalgroup)


    class UNH(Segment):
        """
        Segment: UNH, Message Header

        Function: To head, identify and specify a Message

        Ref.   Repr.       Name                   Remarks

        0062   an..14  M   MESSAGE REFERENCE      A sender's unique message
                           NUMBER                 reference
        ___________________________________________________________________
        S009           M   MESSAGE IDENTIFIER
        0065   an..6   M   Message type           Type of message being
                                                  transmitted
        0052   an..3   M   Message version number Version number of the
                                                  message type. If UNG is used,
                                                  0052 shall be identical
        0054   an..3   M   Message release number Release number within
                                                  current version number
        0051   an..2   M   Controlling agency     Code to identify the agency
                                                  controlling the
                                                  specification, maintenance
                                                  and publication of the
                                                  message type
        0057   an..6   C   Association assigned   A code assigned by the
                           code                   association responsible for
                                                  the design and maintenance of
                                                  the message type
        ___________________________________________________________________
        0068   an..35  C   COMMON ACCESS          Key to relate all
                           REFERENCE              subsequent transfers of data
                                                  to the same business case of
                                                  file. Within the 35
                                                  characters the IA may specify
                                                  component elements
        ___________________________________________________________________
        S010           C   STATUS OF THE TRANSFER
        0070   n..2    M   Sequence of transfers  Starts at 1 and is
                                                  incremented by 1 for each
                                                  transfer
        0073   a1      C   First and last         C = Creation, must be
                           transfer               present for first transfer if
                                                  more than one foreseen
                                                  F = Final, must be present
                                                  for last transfer
        ___________________________________________________________________
        S016           C   MESSAGE SUBSET IDENTIFICATION
        0115   an..14  M   Message subset         Coded identification of a
                           identification         message subset, assigned by
                                                  its controlling agency.
        0116   an..3   C   Message subset         Version number of the message
                           version number         subset.
        0118   an..3   C   Message subset         Release number within the
                           release number         message subset version
                                                  number.
        0051   an..3   C   Controlling agency,    Code identifying a
                           coded                  controlling agency.
        ___________________________________________________________________
        S017           C   MESSAGE IMPLEMENTATION GUIDELINE IDENTIFICATION
        0115   an..14  M   Message implementation Coded identification of the
                           guideline              message implementation
                           identification         guideline, assigned by its
                                                  controlling agency.
        0116   an..3   C   Message implementation Version number of the message
                           guideline version      implementation guideline.
                           number
        0118   an..3   C   Message implementation Release number within the
                           guideline release      message implementation
                           number                 guideline version number.
        0051   an..3   C   Controlling agency,    Code identifying a
                           coded                  controlling agency.
        ___________________________________________________________________
        S018           C   SCENARIO IDENTIFICATION
        0115   an..14  M   Scenario               Coded identifying scenario.
                           identification
        0116   an..3   C   Scenario version       Version number of a scenario.
                           number
        0118   an..3   C   Scenario release       Release number within the
                           number                 scenario version number.
        0051   an..3   C   Controlling agency,    Code identifying a
                           coded                  controlling agency.
        *) Not required if provided in UNG
        (020, 050, 060) Data element S009/0057 is retained for upward compatibility.
        The use of S016 and/or S017 is encouraged in preference.
        (010, 020) The combination fo the values carried in data elements 0062 and S009 shall
        be used to identify uniquely the message within its group (if used) or if not used,
        within its interchange, for the purpose of acknowledgement.
        """
        def __init__(self, reference=None, id=None, access_reference=None, status=None, *a):
            Segment.__init__(self, 'UNH', *a)
            self(
                'reference',
                ('id', ('type', 'version', 'release', 'agency', 'association')),
                'access_reference',
                ('status', ('sequence', 'first_last')),
                ('subset', ('id', 'version', 'release', 'agency')),
                ('guideline', ('id', 'version', 'release', 'agency')),
                ('scenario', ('id', 'version', 'release', 'agency'))
            )
            if not reference is None:
                self.reference = reference
            if not id is None:
                self.id = id
            if not access_reference is None:
                self.access_reference = access_reference
            if not status is None:
                self.status = status


    class UNT(ComplementarySegment):
        """
        Segment: UNT, Message Trailer

        Function: To end and check the completeness of a Message

        Ref.   Repr.       Name                   Remarks

        0074   n..6    M   NUMBER OF SEGMENTS IN  Control count
                           THE MESSAGE            including UNH and UNT
        ___________________________________________________________________
        0062   an..14  M   MESSAGE REFERENCE      Shall be identical to
                           NUMBER                 0062 in UNH
        """
        def __init__(self, unt, message):
            ComplementarySegment.__init__(self, 'UNT', unt, message)

    
    class TXT(Segment):
        """
        Segment: TXT, Text

        Function: To give information in addition to that in other segments in
        the service message, as required

        NOTE: Can not be machine processed. Should be avoided if not
        necessarily required. Normally a conditional segment. It may repeat up
        to the number of times indicated in the message specification which may
        not be higher than 5.

        Ref.   Repr.       Name                   Remarks

        0077   an3     C   TEXT REFERENCE CODE    Qualifies and identifies the
                                                  purpose and function of the
                                                  segment if indicated in the
                                                  message specification
        ___________________________________________________________________
        0078   an..70  M   FREE FORM TEXT         Not machine-processable
                                                  information
        """
        def __init__(self, *a):
            Segment.__init__(self, 'TXT', *a)
            self(
                'code',
                'text',
            )


    class UNS(Segment):
        """
        Segment: UNS, Section Control

        Function: To separate Header, Detail and Summary sections of a message

        NOTE:   To be used by message designers when required to avoid
        ambiguities. Mandatory only if specified for the type of message
        concerned.

        Ref.   Repr.       Name                   Remarks

        0081   a1      M   SECTION IDENTIFICATION Separates sections in a
                                                  message by one of the
                                                  following codes: D separates
                                                  the header and detail
                                                  sections S separates the
                                                  detail and summary sections
        """
        def __init__(self, id):
            Segment.__init__(self, 'UNS', id)
            self('id')


# Implementation notes ==================================================={{{1
# UN/EDIFACT - ISO 9735   http://www.unece.org/

#decoding_map = codecs.make_identity_dict(range(256))
#for x in range(0x80, 0xa0):
#    decoding_map[x] = ord('?') # undefined

# decoding_map.update(
#     {
#         0x00a1: ord('!'), # ¡
#         0x00a2: ord('c'), # ¢
#         0x00a3: ord('#'), # £
#         0x00a4: ord('o'), # ¤
#         0x00a5: ord('Y'), # ¥
#         0x00a6: ord('|'), # ¦
#         0x00a7: ord('S'), # §
#         0x00a8: ord('"'), # ¨
#         0x00a9: ord('c'), # ©
#         0x00aa: ord('a'), # ª
#     })

#for x, y in xlate_latin.iteritems():
#    decoding_map[ord(x)] = unicode(y)
#encoding_map = codecs.make_encoding_map(decoding_map)

# NOTE these characters should maybe have some kind of translation
###   xlate_special = {
###       u'\N{ACUTE ACCENT}': "'",
###       u'\N{BROKEN BAR}': '|',
###       u'\N{CEDILLA}': '{cedilla}',
###       u'\N{CENT SIGN}': '{cent}',
###       u'\N{COMMERCIAL AT}': '{at}',
###       u'\N{COPYRIGHT SIGN}': '{C}',
###       u'\N{CURRENCY SIGN}': '{currency}',
###       u'\N{DEGREE SIGN}': '{degrees}',
###       u'\N{DIAERESIS}': '{umlaut}',
###       u'\N{DIVISION SIGN}': '/',
###       u'\N{DOLLAR SIGN}': '{dollar}',
###       u'\N{FEMININE ORDINAL INDICATOR}': '{^a}',
###       u'\N{INVERTED EXCLAMATION MARK}': '!',
###       u'\N{INVERTED QUESTION MARK}': '?',
###       u'\N{LEFT-POINTING DOUBLE ANGLE QUOTATION MARK}': '<<',
###       u'\N{LEFT SQUARE BRACKET}': '{rightbracket}', 
###       u'\N{LOW LINE}': '{underscore}',
###       u'\N{MACRON}': '_',
###       u'\N{MASCULINE ORDINAL INDICATOR}': '{^o}',
###       u'\N{MICRO SIGN}': '{micro}',
###       u'\N{MIDDLE DOT}': '*',
###       u'\N{MULTIPLICATION SIGN}': '*',
###       u'\N{NOT SIGN}': '{not}',
###       u'\N{NUMBER SIGN}': '{number}',
###       u'\N{PILCROW SIGN}': '{paragraph}',
###       u'\N{PLUS-MINUS SIGN}': '{+/-}',
###       u'\N{POUND SIGN}': '{pound}',
###       u'\N{REGISTERED SIGN}': '{R}',
###       u'\N{REVERSE SOLIDUS}': '{backslash}',
###       u'\N{RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK}': '>>',
###       u'\N{RIGHT SQUARE BRACKET}': '{leftbracket}',
###       u'\N{SECTION SIGN}': '{section}',
###       u'\N{SOFT HYPHEN}': '-',
###       u'\N{SUPERSCRIPT ONE}': '{^1}',
###       u'\N{SUPERSCRIPT THREE}': '{^3}',
###       u'\N{SUPERSCRIPT TWO}': '{^2}',
###       u'\N{TILDE}': '{tilde}',
###       u'\N{VERTICAL LINE}': '{verticalline}',
###       u'\N{VULGAR FRACTION ONE HALF}': '{1/2}',
###       u'\N{VULGAR FRACTION ONE QUARTER}': '{1/4}',
###       u'\N{VULGAR FRACTION THREE QUARTERS}': '{3/4}',
###       u'\N{YEN SIGN}': '{yen}'
###   }

# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=2:
# eof
