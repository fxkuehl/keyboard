#!/usr/bin/python3

import sys
import math

# Keyboard layout evaluator

# Inputs: layout, text file

# Evaluation criteria:
# - heat map deviation from ideal (normalized to 0-1 represent worst and best possible score)
# - finger travel distance (in key units, assuming ortholinear keyboard)
# - adjusted finger travel distance (taking into account linked movement of adjacent fingers)
# - average run length within one hand

# Layout format: Python list of pairs (lower, upper case) for 32 keys
# representing 3 rows of keys like this:
#
#       0 |  1 |  2 |  3    4 ||  5    6 |  7 |  8 |  9
# 10   11 | 12 | 13 | 14   15 || 16   17 | 18 | 19 | 20   21
#      22 | 23 | 24 | 25   26 || 27   28 | 29 | 30 | 31
#         |    |    |         ||         |    |    |
#   pinky |ring|mid |  index  ||  index  | mid|ring|pinky
#                             ||
#          left hand          ||         right hand

layout_QWERTY = [
    ('q', 'Q'), ('w', 'W'), ('e', 'E'), ('r', 'R'), ('t', 'T'),
    ('y', 'Y'), ('u', 'U'), ('i', 'I'), ('o', 'O'), ('p', 'P'),
    ('-', '_'), ('a', 'A'), ('s', 'S'), ('d', 'D'), ('f', 'F'), ('g', 'G'),
    ('h', 'H'), ('j', 'J'), ('k', 'K'), ('l', 'L'), (';', ':'), ('\'', '\"'),
    ('z', 'Z'), ('x', 'X'), ('c', 'C'), ('v', 'V'), ('b', 'B'),
    ('n', 'N'), ('m', 'M'), (',', '<'), ('.', '>'), ('/', '?')
]

layout_DVORAK = [
    ('\'', '\"'), (',', '<'), ('.', '>'), ('p', 'P'), ('y', 'Y'),
    ( 'f',  'F'), ('g', 'G'), ('c', 'C'), ('r', 'R'), ('l', 'L'),
    ( '/',  '?'), ('a', 'A'), ('o', 'O'), ('e', 'E'), ('u', 'U'), ('i', 'I'),
    ( 'd',  'D'), ('h', 'H'), ('t', 'T'), ('n', 'N'), ('s', 'S'), ('-', '_'),
    ( ';',  ':'), ('q', 'Q'), ('j', 'J'), ('k', 'K'), ('x', 'X'),
    ( 'b',  'B'), ('m', 'M'), ('w', 'W'), ('v', 'V'), ('z', 'Z')
]

layout_COLEMAK = [
    ('q', 'Q'), ('w', 'W'), ('f', 'F'), ('p', 'P'), ('g', 'G'),
    ('j', 'J'), ('l', 'L'), ('u', 'U'), ('y', 'Y'), (';', ':'),
    ('-', '_'), ('a', 'A'), ('r', 'R'), ('s', 'S'), ('t', 'T'), ('d', 'D'),
    ('h', 'H'), ('n', 'N'), ('e', 'E'), ('i', 'I'), ('o', 'O'), ('\'', '\"'),
    ('z', 'Z'), ('x', 'X'), ('c', 'C'), ('v', 'V'), ('b', 'B'),
    ('k', 'K'), ('m', 'M'), (',', '<'), ('.', '>'), ('/', '?')
]

layout_WORKMAN = [
    ('q', 'Q'), ('d', 'D'), ('r', 'R'), ('w', 'W'), ('b', 'B'),
    ('j', 'J'), ('f', 'F'), ('u', 'U'), ('p', 'P'), (';', ':'),
    ('-', '_'), ('a', 'A'), ('s', 'S'), ('h', 'H'), ('t', 'T'), ('g', 'G'),
    ('y', 'Y'), ('n', 'N'), ('e', 'E'), ('o', 'O'), ('i', 'I'), ('\'', '\"'),
    ('z', 'Z'), ('x', 'X'), ('m', 'M'), ('c', 'C'), ('v', 'V'),
    ('k', 'K'), ('l', 'L'), (',', '<'), ('.', '>'), ('/', '?')
]

layouts = {
    "QWERTY": layout_QWERTY,
    "Dvorak": layout_DVORAK,
    "Colemak": layout_COLEMAK,
    "Workman": layout_WORKMAN
}

# Translate layouts into efficient lookup tables (maps):
# keymap_... = {symbol : (key, shift, hand, finger, x, y), ...}
#
# where each symbol maps to a tuple of shift, hand, finger and x/y
# coordinate. x/y is relative to the finger's home position.
#
# Fingers are numbered: 0=index, 1=middle, 2=ring, 3=pinky
def calculate_key_props(key):
    if key >= 22:
        row = 2
    elif key >= 10:
        row = 1
    else:
        row = 0

    row_start = (-1, 10, 21)
    col = key - row_start[row]

    fingers = (3, 3, 2, 1, 0, 0, 0, 0, 1, 2, 3, 3)
    finger = fingers[col]

    hand = (col >= 6)

    home_cols = (1, 1, 2, 3, 4, 4, 7, 7, 8, 9, 10, 10)
    x = col - home_cols[col]
    y = row - 1

    return (hand, finger, x, y)

key_props = [calculate_key_props(k) for k in range(32)]

def make_keymap(layout):
    keymap = {}
    for i in range(len(layout)):
        keymap[layout[i][0]] = (i, False) + key_props[i]
        keymap[layout[i][1]] = (i, True ) + key_props[i]

    return keymap

keymaps = {}
for name, layout in layouts.items():
    keymaps[name] = make_keymap(layout)

text = sys.stdin.read()

def calculate_heatmap(keymap, text):
    heatmap = [0 for k in range(32)]
    for c in text:
        if c in keymap:
            k = keymap[c][0]
            heatmap[k] += 1

    return heatmap

key_weights = [2,      6,  9,  6, 3,   3,  6,  9,  6,  2,
               3,  6, 18, 27, 18, 9,   9, 18, 27, 18,  6,  3,
               2,      6,  9,  6, 3,   3,  6,  9,  6,  2]
sorted_key_weights = key_weights[:]
sorted_key_weights.sort()

def score_heatmap(heatmap):
    global key_weights, sorted_key_weigts

    score = sum([a * b for a, b in zip(heatmap, key_weights)])

    heatmap.sort()
    best_score = sum([a * b for a, b in zip(heatmap, sorted_key_weights)])
    heatmap.reverse()
    worst_score = sum([a * b for a, b in zip(heatmap, sorted_key_weights)])

    return (score - worst_score) / (best_score - worst_score)

def calculate_finger_travel(keymap, text):
    finger_pos = [(0, 0) for f in range(8)]
    dist = [0 for f in range(8)]
    for c in text:
        if c in keymap:
            (key, shift, hand, f, x, y) = keymap[c]
            if hand:
                f += 4
            else:
                f = 3 - f
            d = math.sqrt((x - finger_pos[f][0])**2 + (y - finger_pos[f][1])**2)
            finger_pos[f] = (x, y)
            dist[f] += d

    return [int(a) for a in dist]

def calculate_adjusted_travel(keymap, text):
    finger_linkage = ((1   , 0.25, 0  , 0  , 0  , 0  , 0   , 0   ),
                      (0.25, 1   , 0.5, 0  , 0  , 0  , 0   , 0   ),
                      (0   , 0.5 , 1  , 0.1, 0  , 0  , 0   , 0   ),
                      (0   , 0   , 0.1, 1  , 0  , 0  , 0   , 0   ),
                      (0   , 0   , 0  , 0  , 1  , 0.1, 0   , 0   ),
                      (0   , 0   , 0  , 0  , 0.1, 1  , 0.5 , 0   ),
                      (0   , 0   , 0  , 0  , 0  , 0.5, 1   , 0.25),
                      (0   , 0   , 0  , 0  , 0  , 0  , 0.25, 1   )
    )
    finger_pos = [[0, 0] for f in range(8)]
    dist = [0 for f in range(8)]
    for c in text:
        if c in keymap:
            (key, shift, hand, f, x, y) = keymap[c]
            if hand:
                f += 4
            else:
                f = 3 - f
            dx = x - finger_pos[f][0]
            dy = y - finger_pos[f][1]
            d = math.sqrt(dx*dx + dy*dy)
            for g in range(8):
                finger_pos[g][0] += finger_linkage[f][g]*dx
                finger_pos[g][1] += finger_linkage[f][g]*dy
            dist[f] += d

    return [int(a) for a in dist]

def calculate_hand_runs(keymap, text, debug = False):
    last_hand = -1
    run_length = 0
    runs = ({}, {})
    for c in text:
        if c in keymap:
            (key, shift, hand, f, x, y) = keymap[c]
            hand = int(hand)

            if hand == last_hand:
                run_length += 1
                run += c
        else:
            hand = -1

        if hand != last_hand:
            if last_hand >= 0:
                if run_length in runs[last_hand]:
                    runs[last_hand][run_length] += 1
                else:
                    runs[last_hand][run_length] = 1
                if debug:
                    print("Run (%d): %s" % (run_length, run))
            run_length = 1
            run = c
            last_hand = hand

    return runs

def calculate_mean_runs(runs):
    mean = [0, 0]
    for hand in range(2):
        nom = 0
        denom = 0
        for length, num in runs[hand].items():
            nom += length*num
            denom += num
        if denom:
            mean[hand] = nom / denom
    return (mean[0], mean[1])

def calculate_median_runs(runs):
    median = [0, 0]
    for hand in range(2):
        num = 0
        for length, num in runs[hand].items():
            num += num
        lengths = list(runs[hand].keys())
        lengths.sort()
        num /= 2
        for length in lengths:
            num -= runs[hand][length]
            if num <= 0:
                median[hand] = length
                break
    return (median[0], median[1])

def calculate_max_runs(runs):
    return (max(runs[0].keys()), max(runs[1].keys()))

heatmaps = {}
heatmap_scores = {}
finger_travel = {}
adjusted_travel = {}
hand_runs = {}

for name, keymap in keymaps.items():
    heatmaps[name] = calculate_heatmap(keymap, text)
    heatmap_scores[name] = score_heatmap(heatmaps[name])
    finger_travel[name] = calculate_finger_travel(keymap, text)
    adjusted_travel[name] = calculate_adjusted_travel(keymap, text)
    hand_runs[name] = calculate_hand_runs(keymap, text)

for name, score in heatmap_scores.items():
    print("*** Layout: %s ***" % name)
    print("Heatmap score: %f" % score)
    print("Finger travel: %d: %s" % (sum(finger_travel[name]), repr(finger_travel[name])))
    print("Adjusted travel: %d: %s" % (sum(adjusted_travel[name]), repr(adjusted_travel[name])))
    print("Hand runs mean: %s" % repr(calculate_mean_runs(hand_runs[name])))
    print("Hand runs median: %s" % repr(calculate_median_runs(hand_runs[name])))
    print("Hand runs max: %s" % repr(calculate_max_runs(hand_runs[name])))
