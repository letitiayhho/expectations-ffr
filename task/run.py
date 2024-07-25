#!/usr/bin/env python3

from psychopy import visual, core, event
from psychtoolbox import WaitSecs
from events import EventMarker
from functions import *

# constants
FREQS = [110, 150, 210]
    # two values: AB
    # A: predictable is True, and target is 110 Hz then A = 1
    # 	 predictable is True, and target is 150 Hz then mark A = 2
    # 	 predictable is True, and target is 210 Hz then mark A = 3
    # 	 predictable is False, and target is 110 Hz then mark A = 4
    # 	 predictable is False, and target is 150 Hz then mark A = 5
    # 	 predictable is False, and target is 210 Hz then mark A = 6
    # B: if tone is 110 Hz then B = 1
    #    if tone is 150 Hz then B = 2
    #    if tone is 210 Hz then B = 3
PATTERN = [FREQS[0], FREQS[0], FREQS[1], FREQS[1], FREQS[2], FREQS[2]]
SEQ_LEN_MIN = 42
SEQ_LEN_MAX = 50
TONE_LEN = 0.3
ISI = 0.2
SCORE_NEEDED = 24
PRACTICE_SCORE_NEEDED = 1

# ask for subject and block number
SUB_NUM = input("Input subject number: ")
BLOCK_NUM = input("Input block number (1-4): ")
TUTORIAL = input("Run tutorial and instructions (y/n)? ")

# set subject number and block as seed
SEED = int(SUB_NUM + "0" + BLOCK_NUM)
print("Current seed: " + str(SEED))
random.seed(SEED)

# set up keyboard, window and RTBox
WIN = visual.Window(#size = (1600, 900) # 1600, 900
    screen = -1,
    units = "norm",
    fullscr = True,
    pos = (0, 0),
    allowGUI = False)
#KB = get_keyboard('Dell USB Keyboard')
MARKER = EventMarker()

# open log file
LOG = open_log(SUB_NUM, BLOCK_NUM)
score = get_score(LOG)
print(f"score: {score}")
seq_num = get_seq_num(LOG)
print(f"seq_num: {seq_num}")

# randomly select condition
predictable = get_predictability_order(SUB_NUM, BLOCK_NUM)
print(f'predictable: {predictable}')

# listen to all three tones and display instructions
welcome(WIN, BLOCK_NUM) 
if TUTORIAL == "y":
    hear_tones(WIN, TONE_LEN, FREQS)
    instructions(WIN, SCORE_NEEDED)

# practice trial
practice_score = 0
if TUTORIAL == "y":
    while practice_score < PRACTICE_SCORE_NEEDED:
        target = random.choice(FREQS)

        # Play target
        n_target_plays = play_target(WIN, TONE_LEN, target)
        ready(WIN)
        WaitSecs(1)

        # Play tones
        fixation(WIN)
        WaitSecs(1)
        if predictable:
            tone_nums, freqs, marks, is_targets, n_targets = play_predictable_sequence(
                MARKER, FREQS, TONE_LEN, ISI, PATTERN, predictable, target, 30)
        else:
            tone_nums, freqs, marks, is_targets, n_targets = play_random_sequence(
                MARKER, FREQS, TONE_LEN, ISI, predictable, target, 30)
        WIN.flip()
        WaitSecs(0.5)

        # Get response
        response = get_response(WIN)
        correct, practice_score = update_score(WIN, n_targets, response, practice_score, 1)
    end_practice(WIN)
    
# experiment block
# play sequences until SCORE_NEEDED is reached or seq_num >= 25
while score < SCORE_NEEDED:
    n_tones = random.randint(SEQ_LEN_MIN, SEQ_LEN_MAX)
    target = random.choice(FREQS)
    print(f'target: {target}')

    # Play target
    n_target_plays = play_target(WIN, TONE_LEN, target)
    ready(WIN)
    WaitSecs(1)

    # Play tones
    fixation(WIN)
    WaitSecs(1)
    if predictable:
        tone_nums, freqs, marks, is_targets, n_targets = play_predictable_sequence(
            MARKER, FREQS, TONE_LEN, ISI, PATTERN, predictable, target, n_tones)
    else:
        tone_nums, freqs, marks, is_targets, n_targets = play_random_sequence(
            MARKER, FREQS, TONE_LEN, ISI, predictable, target, n_tones)
    WaitSecs(0.5)

    # Get response
    print(f'n_targets: {n_targets}')
    response = get_response(WIN)
    print(f'response: {response}')
    correct, score = update_score(WIN, n_targets, response, score, SCORE_NEEDED)
    print(f'score: {score}')
    print(f'seq_num: {seq_num}')

    # Write log file
    write_log(LOG, n_tones, SEED, SUB_NUM, BLOCK_NUM, predictable, seq_num, target, n_target_plays, tone_nums,
              freqs, marks, is_targets, n_targets, response, correct, score)
    WaitSecs(1)
    
    # Break if 3 extra sequences have been played
    seq_num += 1
    if seq_num >= SCORE_NEEDED + 3:
        break
        
block_end(WIN, BLOCK_NUM)

print("Block over.")

core.quit()
