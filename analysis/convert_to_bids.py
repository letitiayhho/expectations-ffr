#!/usr/bin/env python3

#SBATCH --time=00:15:00
#SBATCH --partition=bigmem2
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=256G # 96 enough for most, 256 G sometimes?
#SBATCH --mail-type=all
#SBATCH --mail-user=letitiayhho@uchicago.edu
#SBATCH --output=logs/convert-to-bids_%j.log

from mne_bids import BIDSPath, write_raw_bids, get_anonymization_daysback
import random
import pandas as pd
import numpy as np
import itertools
import mne
import os
import sys
import re

def main(fpath, sub, task, run) -> None:
    print(fpath, sub, task, run)

    RAW_DIR = '../data/raw/' 
    MAPS_DIR = '../data/captrak/'
    BIDS_DIR = '../data/bids/'

    # load data with MNE function for your file format
    fpath = os.path.join(RAW_DIR, fpath)
    print(fpath)
    raw = mne.io.read_raw_brainvision(fpath)
    raw.load_data()
    raw.set_channel_types({'Aux': 'stim'})

    # add some info BIDS will want
    print("Add line_freq to raw.info")
    raw.info['line_freq'] = 60 # the power line frequency in the building we collected in
    raw.add_reference_channels(ref_channels = ['FCz'])

    # checks
    if len(raw.ch_names) != 65:
        sys.exit(f"Incorrect number of channels, there should be 65 (stim incl) channels, instead there are {n_chans} channels")

    # map channels to their coordinates
    print("Map channels to their captrak coordinates")
    captrak_found = False
    captrak_sub = sub
    while not captrak_found:
        print("Looking for captrak file")
        captrak_path = MAPS_DIR + 'sub-' + str(captrak_sub) + '.bvct'
        print(captrak_path)
        if os.path.isfile(captrak_path):
            print(f"Using captrak file from {captrak_sub}")
            dig = mne.channels.read_dig_captrak(captrak_path)
            raw.set_montage(dig, on_missing = 'warn')
            captrak_found = True
        else:
            captrak_sub = random.randint(3, 30)

    # drop meaningless event name
    print("Set annotations")
    events, event_ids = mne.events_from_annotations(raw)
    events = events[events[:,2] != event_ids['New Segment/'], :]
    if raw.info['sfreq'] == 10000.0: 
        events[:,0] = events[:,0] + 1000 # Fix timestamp
    elif raw.info['sfreq'] == 5000.0:
        events[:,0] = events[:,0] + 500 # Fix timestamp

    # set event information and add line freq 
    annot = mne.annotations_from_events(events, sfreq = raw.info['sfreq'])
    raw.set_annotations(annot)

    # get range of dates the BIDS specification will accept
    daysback_min, daysback_max = get_anonymization_daysback(raw)

    # write data into BIDS directory, while anonymizing
    print("Write data into BIDS directory")
    bids_path = BIDSPath(
            run = run,
            subject = sub,
            task = task,
            datatype = 'eeg',
            root = BIDS_DIR
    )

    write_raw_bids(
        raw,
        bids_path = bids_path,
        allow_preload = True, # whether to load full dataset into memory when copying
        format = 'BrainVision', # format to save to
        anonymize = dict(daysback = daysback_min), # shift dates by daysback
        overwrite = True,
    )

__doc__ = "Usage: ./convert-to-bids.py <fpath> <sub> <task> <run>"

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)
    fpath = sys.argv[1]
    sub = sys.argv[2]
    task = sys.argv[3]
    run = sys.argv[4]
    main(fpath, sub, task, run)

