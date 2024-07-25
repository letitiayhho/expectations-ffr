#!/usr/bin/env python3

#SBATCH --time=00:05:00 # 20 for all figs
#SBATCH --partition=bigmem2
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=16G
#SBATCH --mail-type=all
#SBATCH --mail-user=letitiayhho@uchicago.edu
#SBATCH --output=logs/ffr_plots-%j.log

from matplotlib import pyplot as plt
from itertools import product
import seaborn as sns
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

def read_epochs(sub, desc, BIDS_ROOT):
    '''
    reads and concatenates epochs across runs
    '''
    layout = BIDSLayout(BIDS_ROOT, derivatives = True)
    run = lambda f: int(re.findall('run-(\w+)_', f)[0])
    fnames = layout.get(
        return_type = 'filename',
        subject = sub, 
        desc = desc
        )
    print(fnames)
    fnames.sort(key = run)
    epochs_all = [mne.read_epochs(f) for f in fnames]
    epochs = mne.concatenate_epochs(epochs_all)
    epochs = epochs.pick('eeg')
    return epochs

def compute_power_dB(evokeds):
    poststim = evokeds.compute_psd(tmin = 0., tmax = 0.2)
    baseline = evokeds.compute_psd(tmin = -0.2, tmax = 0.)
    power = 10 * np.log10(poststim.get_data() / baseline.get_data())
    power = np.squeeze(power)
    freqs = poststim.freqs
    return freqs, power

def main(sub):
    spectrums = pd.read_csv('spectrums.csv', sep = '\t')

    # Select data
    fig, ax = plt.subplots(figsize=(8, 6))
    spectrums_150 = spectrums[spectrums.tone == 150]
    spectrums_150 = spectrums_150[spectrums_150.target == 150]

    # Exclude sub
    spectrums_150 = spectrums_150[spectrums_150.subject != sub]
    graph = sns.lineplot(data = spectrums_150, x = "frequency", y = "dB", hue = "target", style = 'predictable', palette = 'tab10', ax = ax)
    graph.axvline(110, linestyle = 'dashed', color = 'blue')
    graph.axvline(150, linestyle = 'dashed', color = 'orange')
    graph.axvline(210, linestyle = 'dashed', color = 'green')
    graph.legend(title = 'Stim freq (Hz)')
    graph.set_ylabel("Power (dB)")
    graph.set_xlabel("Frequency (Hz)")
    graph.set_xlim(50, 250)
    print(f"Saving to ../figs/drop-sub-{sub}_predictability-210.png")
    plt.savefig(f"../figs/drop-sub-{sub}_predictability-210.png")
    
    # # Look at FFR by target tone identity
    # BIDS_ROOT = '../data/bids'
    # layout = BIDSLayout(BIDS_ROOT, derivatives = True)
    # subs = layout.get_subjects(scope = 'preprocess_ffr')
    # subs.sort(key = int)
    # spectrums = []
    
    # condition_mapping = {
    #     # two values: AB
    #     # A: predictable is True, and target is 110 Hz then A = 1
    #     # 	 predictable is True, and target is 150 Hz then mark A = 2
    #     # 	 predictable is True, and target is 210 Hz then mark A = 3
    #     # 	 predictable is False, and target is 110 Hz then mark A = 4
    #     # 	 predictable is False, and target is 150 Hz then mark A = 5
    #     # 	 predictable is False, and target is 210 Hz then mark A = 6
    #     # B: if tone is 110 Hz then B = 1
    #     #    if tone is 150 Hz then B = 2
    #     #    if tone is 210 Hz then B = 3
    #     '1': [True, 110], # [predictable, target tone]
    #     '2': [True, 150],
    #     '3': [True, 210],
    #     '4': [False, 110],
    #     '5': [False, 150],
    #     '6': [False, 210],
    # }
    
    # tone_mapping = {'1': 110,
    #                 '2': 150,
    #                 '3': 210}
        
    # # Read epochs object
    # epochs = read_epochs(sub, 'forFFR', BIDS_ROOT)
    
    # # Get evoked potentials
    # conditions = list(epochs.event_id.keys())
    # evokeds = {c:epochs[c].average() for c in conditions}
    
    # # Iterate over conditions
    # for condition in conditions:
    #     predictable = condition_mapping[condition[0]][0]
    #     target = condition_mapping[condition[0]][1]
    #     tone = tone_mapping[condition[1]]
        
    #     # Compute power in dB
    #     freqs, dB = compute_power_dB(evokeds[condition])
    #     df = pd.DataFrame(
    #         {'subject': sub,
    #          'predictable': predictable,
    #          'target': target,
    #          'tone': tone,
    #          'frequency': freqs,
    #          'dB': dB
    #         }
    #     )
    
    # # FFR
    # fig, ax = plt.subplots(figsize=(8, 6))
    # graph = sns.lineplot(data = df, x = "frequency", y = "dB", hue = "tone", ax = ax)
    # graph.axvline(110, linestyle = 'dashed', color = 'blue')
    # graph.axvline(150, linestyle = 'dashed', color = 'orange')
    # graph.axvline(210, linestyle = 'dashed', color = 'green')
    # graph.legend(title = 'Stim freq (Hz)')
    # graph.set_ylabel("Power (dB)")
    # graph.set_xlabel("Frequency (Hz)")
    # graph.set_xlim(50, 250)
    # graph.set_ylim(-2, 10)
    # plt.savefig(f"../figs/sub-{sub}_ffr.png")
    
    # # Effect of target 110
    # fig, ax = plt.subplots(figsize=(8, 6))
    # spectrums_110 = df[df.tone == 110]
    # graph = sns.lineplot(data = spectrums_110, x = "frequency", y = "dB", hue = "target", ax = ax)
    # graph.axvline(110, linestyle = 'dashed', color = 'blue')
    # graph.axvline(150, linestyle = 'dashed', color = 'orange')
    # graph.axvline(210, linestyle = 'dashed', color = 'green')
    # graph.legend(title = 'Stim freq (Hz)')
    # graph.set_ylabel("Power (dB)")
    # graph.set_xlabel("Frequency (Hz)")
    # graph.set_xlim(50, 250)
    # graph.set_ylim(-2, 10)
    # plt.savefig(f"../figs/sub-{sub}_target-110.png")
    
    # # Effect of target 150
    # fig, ax = plt.subplots(figsize=(8, 6))
    # spectrums_150 = df[df.tone == 150]
    # graph = sns.lineplot(data = spectrums_150, x = "frequency", y = "dB", hue = "target", ax = ax)
    # graph.axvline(110, linestyle = 'dashed', color = 'blue')
    # graph.axvline(150, linestyle = 'dashed', color = 'orange')
    # graph.axvline(210, linestyle = 'dashed', color = 'green')
    # graph.legend(title = 'Stim freq (Hz)')
    # graph.set_ylabel("Power (dB)")
    # graph.set_xlabel("Frequency (Hz)")
    # graph.set_xlim(50, 250)
    # graph.set_ylim(-2, 10)
    # plt.savefig(f"../figs/sub-{sub}_target-150.png")
    
    # # Effect of target 210
    # fig, ax = plt.subplots(figsize=(8, 6))
    # spectrums_210 = df[df.tone == 210]
    # graph = sns.lineplot(data = spectrums_210, x = "frequency", y = "dB", hue = "target", ax = ax)
    # graph.axvline(110, linestyle = 'dashed', color = 'blue')
    # graph.axvline(150, linestyle = 'dashed', color = 'orange')
    # graph.axvline(210, linestyle = 'dashed', color = 'green')
    # graph.legend(title = 'Stim freq (Hz)')
    # graph.set_ylabel("Power (dB)")
    # graph.set_xlabel("Frequency (Hz)")
    # graph.set_xlim(50, 250)
    # graph.set_ylim(-2, 10)
    # plt.savefig(f"../figs/sub-{sub}_target-210.png")
    
    # # Effect of target x predictability for target 110
    # fig, ax = plt.subplots(figsize=(8, 6))
    # spectrums_110 = df[df.tone == 110]
    # spectrums_110 = spectrums_110[spectrums_110.target == 110]
    # graph = sns.lineplot(data = spectrums_110, x = "frequency", y = "dB", hue = "target", style = 'predictable', ax = ax)
    # graph.axvline(110, linestyle = 'dashed', color = 'blue')
    # graph.axvline(150, linestyle = 'dashed', color = 'orange')
    # graph.axvline(210, linestyle = 'dashed', color = 'green')
    # graph.legend(title = 'Stim freq (Hz)')
    # graph.set_ylabel("Power (dB)")
    # graph.set_xlabel("Frequency (Hz)")
    # graph.set_xlim(50, 250)
    # graph.set_ylim(-2, 10)
    # plt.savefig(f"../figs/sub-{sub}_predictability-110.png")
    
    # # Effect of target x predictability for target 150
    # fig, ax = plt.subplots(figsize=(8, 6))
    # spectrums_150 = df[df.tone == 150]
    # spectrums_150 = spectrums_150[spectrums_150.target == 150]
    # graph = sns.lineplot(data = spectrums_150, x = "frequency", y = "dB", hue = "target", style = 'predictable', ax = ax)
    # graph.axvline(110, linestyle = 'dashed', color = 'blue')
    # graph.axvline(150, linestyle = 'dashed', color = 'orange')
    # graph.axvline(210, linestyle = 'dashed', color = 'green')
    # graph.legend(title = 'Stim freq (Hz)')
    # graph.set_ylabel("Power (dB)")
    # graph.set_xlabel("Frequency (Hz)")
    # graph.set_xlim(50, 250)
    # graph.set_ylim(-2, 10)
    # plt.savefig(f"../figs/sub-{sub}_predictability-150.png")
    
    # # Effect of target x predictability for target 210
    # fig, ax = plt.subplots(figsize=(8, 6))
    # spectrums_210 = df[df.tone == 210]
    # spectrums_210 = spectrums_210[spectrums_210.target == 210]
    # graph = sns.lineplot(data = spectrums_210, x = "frequency", y = "dB", hue = "target", style = 'predictable', ax = ax)
    # graph.axvline(110, linestyle = 'dashed', color = 'blue')
    # graph.axvline(150, linestyle = 'dashed', color = 'orange')
    # graph.axvline(210, linestyle = 'dashed', color = 'green')
    # graph.legend(title = 'Stim freq (Hz)')
    # graph.set_ylabel("Power (dB)")
    # graph.set_xlabel("Frequency (Hz)")
    # graph.set_xlim(50, 250)
    # graph.set_ylim(-2, 10)
    # plt.savefig(f"../figs/sub-{sub}_predictability-210.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('sub', type = str)
    args = parser.parse_args()
    main(args.sub)
