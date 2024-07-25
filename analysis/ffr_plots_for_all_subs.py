#!/usr/bin/env python3

from matplotlib import pyplot as plt
from itertools import product
import seaborn as sns
import subprocess
import pandas as pd
import os.path as op
import argparse
import re
import numpy as np
import matplotlib.pyplot as plt
import mne
from scipy import signal
from scipy.fft import fftshift
from bids import BIDSLayout
from statsmodels.stats.anova import AnovaRM

def main(subs, skips):
    # Look at FFR by target tone identity
    BIDS_ROOT = '../data/bids'
    layout = BIDSLayout(BIDS_ROOT, derivatives = True)
    sublist = layout.get_subjects(scope = 'preprocess_ffr')
    sublist.sort(key = int)

    BADS = ['4', '8', '10']

    for sub in sublist:
        if sub in BADS:
            continue

        if bool(subs) and sub not in subs:
            continue

        if sub in skips:
            continue
    
        print(f"subprocess.check_call(\"sbatch ./ffr_plots.py %s\" % ({sub}), shell=True)")
        subprocess.check_call(f"sbatch ./ffr_plots.py {sub}", shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run plot_ffr.py over given subjects')
    parser.add_argument('--subs', 
                        type = str, 
                        nargs = '*', 
                        help = 'subjects to preprocess (e.g. 3 14 8), provide no argument to run over all subjects', 
                        default = [])
    parser.add_argument('--skips', 
                        type = str, 
                        nargs = '*', 
                        help = 'subjects NOT to preprocess (e.g. 1 9)', 
                        default = [])
    args = parser.parse_args()
    subs = args.subs
    skips = args.skips
    print(f"subs: {subs}, skips : {skips}")
    if bool(subs) & bool(skips):
        raise ValueError('Cannot specify both subs and skips')
    main(subs, skips)