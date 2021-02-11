#!/bin/python3
"""A pipeline to convert multiple .tmx files into two aligned text files

Usage:
  process_tmx.py -o <sourceout> <targetout> -i <inputs>...
  process_tmx.py -h

Options:
  -h --help                       Show this screen.

"""

from docopt import docopt
from translate.storage import tmx
from typing import Tuple, Optional, Dict

import cleantmx
from cleantmx.filters import *

def process_unit(unit : tmx.tmxunit) -> Optional[Tuple[str, str]]:
    pair = (unit.source, unit.target)
    pair = process_text(pair)

    if pair is None:
        return None

    return pair

if __name__ == '__main__':
    # Calculated based on corpora to be about the 3.5th std distribution
    # from the mean token length in both English and Swedish.
    # Testing shows this removes all URLs and other non-text entries.
    ensv_maxTL = 25

    process_text = cleantmx.applyFilters(
            UnescapeHTML,
            UnescapeStandard,
            NormalizeWhitespace,
            (NormalizeQuotationEN, NormalizeQuotationSV),
            RemoveXML,
            RemoveNonText(min_token_length=2, max_token_length=ensv_maxTL),
            RemoveOnWordcount(min_wordcount=3, max_wordcount=100),
            RemoveOnSourceTargetRatio(max_ratio=2),
            RemoveEmpty
            )

    arguments = docopt(__doc__, version='TMX Pipeline 0.1')

    source_filename = arguments['<sourceout>']
    target_filename = arguments['<targetout>']
    input_filenames = arguments['<inputs>']

    entries = set()

    for filename in input_filenames:
        print(f'Processing input file: {filename}')
        with open(filename, 'rb') as infile:
            tmxfile = tmx.tmxfile(infile)
            file_entries = map(process_unit, tmxfile.units)
            entries.update(file_entries)

    if None in entries:
        entries.remove(None)

    print(f'Processing complete. {len(entries)} valid pairs found.')

    source, target = map(list, zip(*entries))

    print(f'Writing source entries to: {source_filename}')
    with open(source_filename, 'w') as source_outfile:
        source_outfile.write('\n'.join(source))

    print(f'Writing target entries to: {target_filename}')
    with open(target_filename, 'w') as target_outfile:
        target_outfile.write('\n'.join(target))

