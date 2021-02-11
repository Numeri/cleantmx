from typing import Any, Callable, Dict, Text
import os.path
import pickle
import re
import sys
import unicodedata

def _parse16(match : re.Match) -> Text:
    return match.group(1) + chr(int(match.group(2), base=16))

def _parse8(match : re.Match) -> Text:
    return match.group(1) + chr(int(match.group(2), base=8))

def _make_charsets() -> Dict[str, Any]:
    charsets = dict()

    # Fill Unicode categories
    charsets['unicode_categories'] = dict()
    for c in map(chr, range(sys.maxunicode + 1)):
        category = unicodedata.category(c) 
        if category not in charsets['unicode_categories']:
            charsets['unicode_categories'][category] = list(c)
        else:
            charsets['unicode_categories'][category].append(c)

    # All Unicode whitespace
    charsets['whitespace'] = charsets['unicode_categories']['Zl'] + charsets['unicode_categories']['Zs'] + charsets['unicode_categories']['Zp'] + charsets['unicode_categories']['Cc']

    # Match an even number of preceeding backslashes
    # This prevents escaped backslashes from being consumed
    # as regular backslashes in lettered escapes
    _even_backslash = r'((?:^|[^\\])(?:\\\\)*)'

    charsets['string_escapes'] = {
            re.compile(_even_backslash + r"\\'"):  "\1'",
            re.compile(_even_backslash + r'\\"'):  '\1"',
            re.compile(_even_backslash + r'\\a'):  '\1\a',
            re.compile(_even_backslash + r'\\b'):  '\1\b',
            re.compile(_even_backslash + r'\\f'):  '\1\f',
            re.compile(_even_backslash + r'\\n'):  '\1\n',
            re.compile(_even_backslash + r'\\r'):  '\1\r',
            re.compile(_even_backslash + r'\\t'):  '\1\t',
            re.compile(_even_backslash + r'\\v'):  '\1\v',
            re.compile(_even_backslash + r'\\u([0-9a-f]{4})'): _parse16,
            re.compile(_even_backslash + r'\\U([0-9a-f]{8})'): _parse16,
            re.compile(_even_backslash + r'\\([0-7]{3})'):     _parse8,
            re.compile(_even_backslash + r'\\([0-9a-f]{2})'):  _parse16,
            re.compile('\\\\\\\\'): '\\\\',
            }

    return charsets

def _load_charsets(dump_filename : str = '.charsets') -> Dict[str, Any]:
    if os.path.exists(dump_filename):
        with open(dump_filename, 'rb') as dumpfile:
            charsets = pickle.load(dumpfile)
            return charsets

    charsets = _make_charsets()
    try:
        with open(dump_filename, 'wb') as dumpfile:
            pickle.dump(charsets, dumpfile)
    except Exception as e:
        print(f'cleantmx.charsets could not save cached character sets: {e}\nThis will not result in any issues, but will result in decreased performance.')

    return charsets

charsets = _load_charsets()
for name, cs in charsets.items():
    globals()[name] = cs

__all__ = charsets.keys()

