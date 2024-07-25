#!/usr/bin/env python

import re
import os
import itertools
from typing import Tuple, Iterator

KeyType = Tuple[str, str, str, str]

def iter_raw_paths(data_dir) -> Iterator[KeyType]:
    fnames = os.listdir(data_dir)

    for fname in fnames:
        if 'sub' not in fname or '.vhdr' not in fname:
            continue

        # Get subject number
        filt = re.compile('(([0-9]|[1-9][0-9]){1,2})')
        sub = re.search(filt, fname).group(0)

        # Get task name
        task = 'expectations'

        # Get run number
        filt = re.compile('\w+[0-9]_([0-9]).*')
        run = re.findall(filt, fname)
        run = '1' if run == [] else run[0]

        key = (fname, sub, task, run)
        print(key)
        yield key

__all__ = ['iter_raw_paths']
