import pandas as pd
import os.path
import random
from itertools import cycle, islice

from psychopy import prefs
prefs.hardware['audioLib'] = ['ptb']
from psychopy.sound.backend_ptb import SoundPTB as Sound
from psychopy import visual, core, event
from psychtoolbox import GetSecs, WaitSecs, hid
from psychopy.hardware.keyboard import Keyboard

def get_keyboard(dev_name):
    devs = hid.get_keyboard_indices()
    idxs = devs[0]
    names = devs[1]
    try:
        idx = [idxs[i] for i, nm in enumerate(names) if nm == dev_name][0]
    except:
        raise Exception(
        'Cannot find %s! Available devices are %s.'%(dev_name, ', '.join(names))
        )
    return Keyboard(idx)

def open_log(SUB_NUM, BLOCK_NUM):
    log = "data/logs/sub-" + SUB_NUM + "_blk-" + BLOCK_NUM + ".log"

    if not os.path.isfile(log): # create log file if it doesn't exist
        print(f"Creating {log}")
        d = {
        'seed': [],
        'sub_num': [],
        'block_num': [],
        'predictable': [],
        'seq_num': [],
        'target': [],
        'n_target_plays': [],
        'tone_num' : [],
        'freq': [],
        'mark': [],
        'is_target': [],
        'n_targets': [],
        'response': [],
        'correct': [],
        'score': [],
        }
        print(d)
        df = pd.DataFrame(data = d)
        df.to_csv(log, mode='w', index = False)
    return(log)

def get_score(LOG):
    log = pd.read_csv(LOG)
    scores = log['score']
    if len(scores) == 0:
        score = 0
    else:
        score = scores.iloc[-1]
    score = int(score)
    return(score)

def get_seq_num(LOG):
    log = pd.read_csv(LOG)
    seq_nums = log['seq_num']
    if len(seq_nums) == 0:
        seq_num = 1
    else:
        seq_num = seq_nums.iloc[-1]
    seq_num = int(seq_num)
    return(seq_num)

def get_predictability_order(SUB_NUM, BLOCK_NUM):
    predictability_orders = [(True, False, True, False), (False, True, False, True)]
    predictability_order = predictability_orders[int(SUB_NUM)%2]
    predictable = predictability_order[int(BLOCK_NUM) - 1] # boolean
    return predictable

def fixation(WIN):
    fixation = visual.TextStim(WIN, '+')
    fixation.draw()
    WIN.flip()
    return(fixation)

def welcome(WIN, BLOCK_NUM):
    if BLOCK_NUM == '1':
        welcome_text = visual.TextStim(WIN, text = f"Welcome to the study. Press 'enter' to continue.")
    else:
        welcome_text = visual.TextStim(WIN, text = f"Welcome to block number {BLOCK_NUM}/4. Please remember to minimize any movement and blinks. In some blocks the tones will appear in a pattern, in others they will be random. Please keep your gaze fixed on the + when it appears. Press 'enter' to begin.")
    welcome_text.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])

def hear_tones(WIN, TONE_LEN, FREQS):
    p1 = Sound(FREQS[0], secs = TONE_LEN)
    p2 = Sound(FREQS[1], secs = TONE_LEN)
    p3 = Sound(FREQS[2], secs = TONE_LEN)

    p1_txt = visual.TextStim(WIN, text = "You will be listening to random sequences of three different tones. You will now hear a sample of each of the three tones. Press 'enter' to hear the first tone now.")
    p1_txt.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    p1.play()
    core.wait(1)

    p2_txt = visual.TextStim(WIN, text = "Press 'enter' to hear second tone.")
    event.clearEvents(eventType = None)
    p2_txt.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    p2.play()
    core.wait(1)

    p3_txt = visual.TextStim(WIN, text = "Press 'enter' to hear third tone.")

    event.clearEvents(eventType = None)
    p3_txt.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    p3.play()
    core.wait(1)

def instructions(WIN, SCORE_NEEDED):
    instruction1_text = visual.TextStim(WIN, text = "At the beginning of each trial, one of the three tones will be randomly selected to be the 'target tone'. You will be asked to count the number of times you hear the target tone. At the beginning of each trial you will get the chance to listen to the target tone as many times as you like. Press 'enter' to continue...")
    event.clearEvents(eventType = None)
    instruction1_text.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    WIN.flip()
    print('instruction1')
    
    instruction2_text = visual.TextStim(WIN, text = f"In some blocks the tones will be played in a pattern, in others they will be random. At the end of each trial you will be asked how many times you heard the target tone during the trial. Use the number keys at the top of the keyboard to input your answer and then press 'enter' to submit it. Press 'enter' to continue...")
    event.clearEvents(eventType = None)
    instruction2_text.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    WIN.flip()
    print('instruction2')
    
    instruction3_text = visual.TextStim(WIN, text = f"At the end of each trial you will be asked how many times you heard the target tone during the trial. If you accurately report the number of target tones– or come close to the actual number of target tones by 2– your 'score' will increase by 1. To finish each block, you will have to reach a score of {SCORE_NEEDED}. There will be 4 total blocks. Please ask your experimenter any questions you may have about the task. Press 'enter' to continue...")
    event.clearEvents(eventType = None)
    instruction3_text.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    WIN.flip()
    print('instruction3')

    instruction4_text = visual.TextStim(WIN, text = "It is important for you not to move your eyes or blink while the tones are playing. We also ask that you hold the rest of your body as still as possible. To help with this, a fixation cross '+' will be shown during the tone sequence. Keep your gaze on the fixation cross and hold your body and gaze as still as you can while the cross is on the screen. Press 'enter' to continue...")
    event.clearEvents(eventType = None)
    instruction4_text.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    WIN.flip()
    print('instruction4')

    instruction5_text = visual.TextStim(WIN, text = "You will now complete one practice trial before experiment blocks begin. Press 'enter' to begin the practice trial...")
    event.clearEvents(eventType = None)
    instruction5_text.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    WIN.flip()
    print('instruction5')

def end_practice(WIN):
    instruction1_text = visual.TextStim(WIN, text = "Thank you for completing the practice trial. Press 'enter' to proceed to the experiment trials.")
    event.clearEvents(eventType = None)
    instruction1_text.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    WIN.flip()
    print('end_practice')
    
def play_target(WIN, TONE_LEN, target):
    t_snd = Sound(target, secs = TONE_LEN)

    target_text = visual.TextStim(WIN, text = "Press 'space' to hear the target tone. Press 'enter' to continue")
    target_text.draw()
    WIN.flip()
    target_played = False
    n_target_plays = 0
    while True:
        keys = event.getKeys(keyList = ['space', 'return'])
        if 'space' in keys:
            t_snd.play()
            target_played = True
            n_target_plays += 1
            print('Target played')
        elif 'return' in keys and target_played:
            break

    return(n_target_plays)

def ready(WIN):
    block_begin = visual.TextStim(WIN, text = "Please count how many times you hear the target tone. Press 'enter' to begin!")
    block_begin.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    WIN.flip()

def play_random_sequence(MARKER, FREQS, TONE_LEN, ISI, predictable, target, n_tones):
    n_targets = 0
    force = False
    one_back = 0
    two_back = 0

    # play first tone
    tone_nums, freqs, marks, is_targets = play_first_tone(MARKER, FREQS, TONE_LEN, ISI, predictable, target)

    for tone_num in range(2, n_tones + 1):
        print(tone_num, end = ', ', flush = True)

        # select tone
        if not force:
            i = random.randint(0, len(FREQS)-1)
        freq = FREQS[i]
        mark = get_mark(FREQS, predictable, target, i)
        snd = Sound(freq, secs = TONE_LEN)

        # increment target count
        is_target, n_targets = check_target(freq, target, n_targets)

        # schedule sound
        now = GetSecs()
        snd.play(when = now + 0.1)
        WaitSecs(0.1)
        MARKER.send(mark)
        WaitSecs(TONE_LEN)

        # Add ISI - buffer + jitter
        WaitSecs(ISI - 0.1 + random.uniform(0, 0.05))

        # save tone info
        tone_nums.append(tone_num)
        freqs.append(freq)
        marks.append(mark)
        is_targets.append(is_target)

        # check for repeats
        force, i, one_back, two_back = check_repeats(FREQS, freq, one_back, two_back)

    print('')
    return(tone_nums, freqs, marks, is_targets, n_targets)

def get_starting_point(pattern, target):
    i = random.randint(0, len(pattern)-1)
    while pattern[i] == target:
        i = random.randint(0, len(pattern)-1)
    return i

def get_predictable_sequence(FREQS, PATTERN, target, n_tones):
    
    # Pick a random starting point that is not the target tone
    start_i = get_starting_point(PATTERN, target)
            
    # Generate patterns from the starting index
    for i, tone in enumerate(PATTERN):
        if start_i == i:
            sequence = list(islice(cycle(PATTERN), i, i+n_tones))
            
    print(f'sequence: {sequence}')
    return sequence
    
def play_predictable_sequence(MARKER, FREQS, TONE_LEN, ISI, PATTERN, predictable, target, n_tones):
    n_targets = 0
    force = False
    one_back = 0
    two_back = 0
    
    tone_nums = []
    freqs = []
    marks = []
    is_targets = []
    
    sequence = get_predictable_sequence(FREQS, PATTERN, target, n_tones)
    tone_num = 1
    for freq in sequence:
        print(tone_num, end = ', ', flush = True)
        mark = get_mark(FREQS, predictable, target, FREQS.index(freq))
        snd = Sound(freq, secs = TONE_LEN)

        # increment target count
        is_target, n_targets = check_target(freq, target, n_targets)

        # schedule sound
        now = GetSecs()
        snd.play(when = now + 0.1)
        WaitSecs(0.1)
        MARKER.send(mark)
        WaitSecs(TONE_LEN)

        # Add ISI - buffer + jitter
        WaitSecs(ISI - 0.1 + random.uniform(0, 0.05))

        # save tone info
        tone_nums.append(tone_num)
        freqs.append(freq)
        marks.append(mark)
        is_targets.append(is_target)
        
        # increment tone number
        tone_num += 1

    print('')
    return(tone_nums, freqs, marks, is_targets, n_targets)

def get_mark(FREQS, predictable, target, i):
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

    # Get A
    target_mark = FREQS.index(target) + 1
    if predictable:
        predictable_and_target_mark = target_mark
    else:
        predictable_and_target_mark = 3 + target_mark

    # Get B
    tone_mark = i + 1
    mark = int(str(predictable_and_target_mark) + str(tone_mark))
    return(mark)

def play_first_tone(MARKER, FREQS, TONE_LEN, ISI, predictable, target):
    print('1', end = ', ', flush = True)

    indexes = [1, 2]
    i = random.choice(indexes)
    freq = FREQS[i]
    mark = get_mark(FREQS, predictable, target, i)

    # schedule sound
    now = GetSecs()
    snd = Sound(freq, secs = TONE_LEN)
    snd.play(when = now + 0.1) # 0.1 msec buffer
    WaitSecs(0.1)
    MARKER.send(mark)
    WaitSecs(TONE_LEN)

    # Add ISI - buffer + jitter
    WaitSecs(ISI - 0.1 + random.uniform(0, 0.05))

    tone_nums = [1]
    freqs = [freq]
    marks = [mark]
    is_targets = [0]

    return(tone_nums, freqs, marks, is_targets)

def check_target(freq, target, n_targets):
    if freq == target:
        is_target = 1
        n_targets += 1
    else:
        is_target = 0
    return(is_target, n_targets)

def check_repeats(FREQS, freq, one_back, two_back):
    if freq == one_back == two_back:
        force = True
        drop = FREQS.index(freq)
        indexes = [0, 1, 2]
        indexes.pop(drop)
        i = random.choice(indexes)
    else:
        force = False
        i = None
    two_back = one_back
    one_back = freq
    return(force, i, one_back, two_back)

def broadcast(n_tones, var):
    if not isinstance(var, list):
        broadcasted_array = [var]*n_tones
    return(broadcasted_array)

def write_log(LOG, n_tones, SEED, SUB_NUM, BLOCK_NUM, predictable, seq_num, target, n_target_plays, 
              tone_nums, freqs, marks, is_targets, n_targets, response, correct, score):
    print("Writing to log file")
    d = {
        'seed': broadcast(n_tones, SEED),
        'sub_num': broadcast(n_tones, SUB_NUM),
        'block_num': broadcast(n_tones, BLOCK_NUM),
        'predictable': broadcast(n_tones, predictable),
        'seq_num': broadcast(n_tones, seq_num),
        'target': broadcast(n_tones, target),
        'n_target_plays': broadcast(n_tones, n_target_plays),
        'tone_num' : tone_nums,
        'freq': freqs,
        'mark': marks,
        'is_target': is_targets,
        'n_targets': broadcast(n_tones, n_targets),
        'response': broadcast(n_tones, response),
        'correct': broadcast(n_tones, correct),
        'score': broadcast(n_tones, score),
        }
    df = pd.DataFrame(data = d)
    df.to_csv(LOG, mode='a', header = False, index = False)

def get_response(WIN):
    # Prompt response
    ask_response = visual.TextStim(WIN, text = "How many times did you hear the target tone?")
    ask_response.draw()
    WIN.flip()

    # Fetch response
    keylist = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'return', 'backspace']
    response = []
    response_text = ''

    while True:
        keys = event.getKeys(keyList = keylist)
        if response_text and 'return' in keys: # empty response not accepted
            break
        elif keys:
            if 'return' in keys:
                None
            elif 'backspace' in keys:
                response = response[:-1]
            else:
                response.append(keys)
            response_text = ''.join([item for sublist in response for item in sublist])
            WIN.flip()
            show_response = visual.TextStim(WIN, text = response_text)
            show_response.draw()
            WIN.flip()

    response = int(response_text)
    return(response)

def update_score(WIN, n_targets, response, score, SCORE_NEEDED):
    if abs(n_targets - response) == 0:
        correct = 2
        score += 1
        update = visual.TextStim(WIN, text = f"You are correct! There were {n_targets} targets. Your score is now {score}/{SCORE_NEEDED}. Press 'enter' to continue.")
    elif abs(n_targets - response) <= 2:
        correct = 1
        score += 1
        update = visual.TextStim(WIN, text = f"Close enough! There were {n_targets} targets. Your score is now {score}/{SCORE_NEEDED}. Press 'enter' to continue.")
    else:
        correct = 0
        update = visual.TextStim(WIN, text = f"There were {n_targets} targets. Your score remains {score}/{SCORE_NEEDED}. Press 'enter' to continue.")

    update.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    WIN.flip()

    return(correct, score)

def block_end(WIN, BLOCK_NUM):
    if BLOCK_NUM == "6":
        block_end_text = visual.TextStim(WIN, text = f"Congratulations, you have completed the experiment! Your experimenter will be with you shortly. Thank you for participating.")
    else:
        block_end_text = visual.TextStim(WIN, text = f"Congratulations, you have completed the experiment block. Your experimenter will be with you shortly.")
    block_end_text.draw()
    WIN.flip()
    WaitSecs(15)
