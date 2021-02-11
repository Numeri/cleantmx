from cleantmx.core import *
import cleantmx.charsets as charsets

from typing import Callable, Dict, Iterable, Optional, Text, Union
import html
import re

__all__ = ['RemoveSmaller', 'RemoveLarger', 'RemoveEmpty', 'UnescapeHTML', 'UnescapeStandard', 'NormalizeWhitespace', 'Replace', 'NormalizeQuotationEN', 'NormalizeQuotationSV', 'RemoveXML', 'RemoveNonText', 'RemoveOnWordcount', 'RemoveOnSourceTargetRatio']

# Define various filters that can be composed with the `applyFilters` function
# Note that some allow for customization via parameters, but others should
# be passed to applyFilters without being called

def RemoveSmaller(min_length : int) -> FilterType:
    """Remove all entries shorter than `min_length`

Args:
  min_length: The minimum length in characters.

Returns:
  A filter function which removes all entries with less than `min_length` characters
"""
    def _RemoveSmaller(text : Text) -> Optional[Text]:
        if len(text) < min_length:
            return None
        return text
    return _RemoveSmaller

RemoveEmpty = RemoveSmaller(1)
RemoveEmpty.__doc__ = "Remove all empty entries"


def RemoveLarger(max_length : int) -> FilterType:
    """Remove all entries longer than `max_length`

Args:
  max_length: The maximum length in characters.

Returns:
  A filter function which removes all entries with more than `max_length` characters
"""
    def _RemoveLarger(text : Text) -> Optional[Text]:
        if len(text) > max_length:
            return None
        return text
    return _RemoveLarger


def UnescapeHTML(text : Text) -> Optional[Text]:
    """Replace HTML escape sequences with their Unicode values"""
    return html.unescape(text)


def UnescapeStandard(text : Text) -> Optional[Text]:
    """Replace standard C-style escape codes with their Unicode values"""
    for pattern, replacement in charsets.string_escapes.items():
        text = re.sub(pattern, replacement, text)

    return text


whitespace_pattern = re.compile('|'.join(charsets.whitespace) + '+')
def NormalizeWhitespace(text : Text) -> Optional[Text]:
    """Replace all whitespace in the Unicode category 'Z' with a single space"""
    return re.sub(whitespace_pattern, ' ', text)


def Replace(input_set : Union[Iterable[chr], chr], output : chr) -> FilterType:
    """Replace characters in `input_set` with the character `output`"""
    input_set = map(re.escape, input_set)
    pattern = re.compile('|'.join(input_set))
    def _Replace(text : Text) -> Optional[Text]:
        return re.sub(pattern, output, text)
    return _Replace


all_quotes = charsets.unicode_categories['Pi'] + charsets.unicode_categories['Pf']
single_quotes = [q for q in all_quotes if 'SINGLE' in charsets.unicodedata.name(q)]
other_quotes  = [q for q in all_quotes if q not in single_quotes]

_ReplaceSingleEN = Replace(single_quotes, "'")
_ReplaceDoubleEN = Replace(other_quotes, '"')
def NormalizeQuotationEN(text : Text) -> Optional[Text]:
    """Replace all quotation marks with standard symbols based on English quotation rules.

All quotation marks in the Unicode category 'Pi' (initial quotes) and 'Pf' (final quotes)
with the word 'SINGLE' in their Unicode name are replaced with '\\x27' ('APOSTROPHE').
All others are replaced with '\\x22' ('QUOTATION MARK')."""
    text = _ReplaceSingleEN(text)
    text = _ReplaceDoubleEN(text)
    return text


_ReplaceSingleSV = Replace(single_quotes, '\u2019')
_ReplaceDoubleSV = Replace(other_quotes, '\u201D')
def NormalizeQuotationSV(text : Text) -> Optional[Text]:
    """Replace all quotation marks with standard symbols based on Swedish quotation rules.

All quotation marks in the Unicode category 'Pi' (initial quotes) and 'Pf' (final quotes)
with the word 'SINGLE' in their Unicode name are replaced with '\\u2019' ('RIGHT SINGLE QUOTATION MARK').
All others are replaced with '\\u201D' ('RIGHT DOUBLE QUOTATION MARK')."""
    text = _ReplaceSingleSV(text)
    text = _ReplaceDoubleSV(text)
    return text


xml_pattern = re.compile(r'<.[^(><)]+>')
def RemoveXML(text : Text) -> Optional[Text]:
    """Remove all XML markup in the text (including HTML markup)"""
    text = re.sub(xml_pattern, '', text)
    return text


def RemoveNonText(min_token_length : int, max_token_length : int) -> FilterType:
    """Removes segments suspected of being non-text content.

It does so by calculating `text`'s average token length, split by whitespace.
If this is above `max_token_length` or below `min_token_length`, it rejects the text. It is suggested that
the user examine the corpora they would like to use to choose the proper value for
`max_token_length`, as this will vary by language. A recommended value is `m + 3*std`,
where `m` is the mean token length in the corpus and `std` is the standard distribution 
of the token length."""
    def _RemoveNonText(text : Text) -> Optional[Text]:
        num_tokens = len(text.split())
        if num_tokens == 0:
            return None

        avg_token_length = len(text) / num_tokens
        if avg_token_length > max_token_length or avg_token_length < min_token_length:
            return None

        return text
    return _RemoveNonText


def RemoveOnWordcount(min_wordcount : int, max_wordcount : int) -> FilterType:
    """Remove all segments with less than `min_wordcount` tokens or more than `max_wordcount` tokens (split by whitespace)."""
    def _RemoveOnWordcount(text : Text) -> Optional[Text]:
        num_words = len(text.split())
        if num_words < min_wordcount or num_words > max_wordcount:
            return None
        return text
    return _RemoveOnWordcount

def RemoveOnSourceTargetRatio(max_ratio : float) -> ParallelFilterType:
    """Remove all units with a source to target or target to source character ratio larger than `max_ratio`."""
    def _RemoveOnSourceTargetRatio(unit : Unit) -> Optional[Unit]:
        source = unit[0]
        target = unit[1]
        source_chars = len(source)
        target_chars = len(target)

        if source_chars / target_chars > max_ratio or target_chars / source_chars > max_ratio:
            return None

        return unit
    return _RemoveOnSourceTargetRatio

