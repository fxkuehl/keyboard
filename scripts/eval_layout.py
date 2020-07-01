#!/usr/bin/python3

import sys
import math
import random
import operator

# Keyboard layout evaluator

# Inputs: layout, text file

# Evaluation criteria:
# - heat map deviation from ideal (normalized to 0-1 represent worst and best possible score)
# - finger travel distance (in key units, assuming ortholinear keyboard)
# - adjusted finger travel distance (taking into account linked movement of adjacent fingers)
# - average run length within one hand

# Layout format: Python list of pairs (lower, upper case) for 30 keys
# representing 3 rows of keys like this:
#
#       0 |  1 |  2 |  3    4 ||  5    6 |  7 |  8 |  9
#      10 | 11 | 12 | 13   14 || 15   16 | 17 | 18 | 19
#      20 | 21 | 22 | 23   24 || 25   26 | 27 | 28 | 29
#         |    |    |         ||         |    |    |
#   pinky |ring|mid |  index  ||  index  | mid|ring|pinky
#                             ||
#          left hand          ||         right hand

layout_QWERTY = [
    'qQ', 'wW', 'eE', 'rR', 'tT',   'yY', 'uU', 'iI', 'oO', 'pP',
    'aA', 'sS', 'dD', 'fF', 'gG',   'hH', 'jJ', 'kK', 'lL', ';:',
    'zZ', 'xX', 'cC', 'vV', 'bB',   'nN', 'mM', ',<', '.>', '/?'
]

layout_DVORAK = [
    '\'"',',<', '.>', 'pP', 'yY',   'fF', 'gG', 'cC', 'rR', 'lL',
    'aA', 'oO', 'eE', 'uU', 'iI',   'dD', 'hH', 'tT', 'nN', 'sS',
    ';:', 'qQ', 'jJ', 'kK', 'xX',   'bB', 'mM', 'wW', 'vV', 'zZ'
]

layout_PLUM = [
    'pP', 'lL', 'uU', 'mM', ';:',   '\'"','cC', 'fF', 'gG', 'qQ',
    'rR', 'eE', 'aA', 'dD', 'oO',   'nN', 'tT', 'hH', 'iI', 'sS',
    'kK', 'jJ', 'vV', 'bB', ',<',   '.>', 'wW', 'xX', 'yY', 'zZ'
]

layout_COLEMAK = [
    'qQ', 'wW', 'fF', 'pP', 'gG',   'jJ', 'lL', 'uU', 'yY', ';:',
    'aA', 'rR', 'sS', 'tT', 'dD',   'hH', 'nN', 'eE', 'iI', 'oO',
    'zZ', 'xX', 'cC', 'vV', 'bB',   'kK', 'mM', ',<', '.>', '/?'
]

layout_COLEMAKDH = [
    'qQ', 'wW', 'fF', 'pP', 'bB',   'jJ', 'lL', 'uU', 'yY', ';:',
    'aA', 'rR', 'sS', 'tT', 'gG',   'kK', 'nN', 'eE', 'iI', 'oO',
    'zZ', 'xX', 'cC', 'dD', 'vV',   'mM', 'hH', ',<', '.>', '/?'
]

layout_WORKMAN = [
    'qQ', 'dD', 'rR', 'wW', 'bB',   'jJ', 'fF', 'uU', 'pP', ';:',
    'aA', 'sS', 'hH', 'tT', 'gG',   'yY', 'nN', 'eE', 'oO', 'iI',
    'zZ', 'xX', 'mM', 'cC', 'vV',   'kK', 'lL', ',<', '.>', '/?'
]

# [ B ] [ K ] [ H ] [; :] [ X ] | [ Z ] [ Q ] [. >] [ U ] [ W ]
#  2.7   1.2   9.7   0.3   0.1  |  0.1   0.2   2.7   4.7   3.3
# [ N ] [ T ] [ R ] [ A ] [, <] | [ F ] [ S ] [ E ] [ I ] [ D ]
# 11.5  14.9   8.8  12.6   2.4  |  4.0  10.2  20.2  11.7   6.1
# [ P ] [ M ] [ L ] [ O ] [' "] | [ G ] [ V ] [ J ] [ Y ] [ C ]
#  3.4   3.9   7.8  12.5   1.4  |  3.3   1.7   0.2   2.9   5.4
# 17.6  20.0  26.3  29.4        |       19.5  23.1  19.4  14.7
#Heatmap score: 0.900074
#Bad bigrams:     166
#Fast bigrams:  12111
#Finger travel: 33055: [57, 49, 135, 116, 85, 28, 73, 66]
#Adjusted travel: 35676: [61, 70, 135, 119, 86, 43, 76, 68]
#Hand runs mean, max: (1.738695831128359, 1.4731006906579425), (8, 8)
layout_NTRA = [
    'bB', 'kK', 'hH', 'qQ', 'xX',   'zZ', 'jJ', '.>', 'uU', 'wW',
    'nN', 'tT', 'rR', 'aA', '\'"',  'fF', 'sS', 'eE', 'iI', 'dD',
    'pP', 'mM', 'lL', 'oO', ';:',   'gG', 'vV', ',<', 'yY', 'cC'
]

# [ B ] [ G ] [ H ] [ Q ] [ X ] | [ J ] [ W ] [. >] [ Y ] [ Z ]
#  2.2   3.2   7.8   0.3   0.2  |  0.6   2.7   2.9   2.6   0.1
# [ N ] [ T ] [ R ] [ O ] [, <] | [ F ] [ C ] [ E ] [ I ] [ S ]
# 12.1  15.5  10.2  13.0   2.5  |  4.3   6.7  19.9  11.7  10.1
# [ P ] [ K ] [ L ] [ A ] [; :] | [ M ] [ D ] [' "] [ U ] [ V ]
#  3.8   1.0   6.8  12.5   0.3  |  3.9   5.9   0.8   4.5   1.8
# 18.1  19.7  24.8  28.9        |       24.1  23.7  18.8  12.0
#Heatmap score: 0.9212
#Bad bigrams:      286
#Fast bigrams:   21592
#Finger travel: 58455: [56, 44, 116, 115, 144, 31, 69, 18]
#Adjusted travel: 63244: [60, 60, 118, 118, 144, 47, 71, 24]
#Hand runs mean, max: (1.755061942187292, 1.4950978773974186), (9, 9)
layout_NTRO = [
    'bB', 'gG', 'hH', 'qQ', 'xX',   'jJ', 'wW', '.>', 'yY', 'zZ',
    'nN', 'tT', 'rR', 'oO', '\'"',  'fF', 'cC', 'eE', 'iI', 'sS',
    'pP', 'kK', 'lL', 'aA', ';:',   'mM', 'dD', ',<', 'uU', 'vV'
]

# [; :] [ Y ] [ P ] [ J ] [ Z ] | [ X ] [ Q ] [ O ] [ F ] [ W ]
#  0.3   2.6   3.8   0.6   0.1  |  0.2   0.3  13.0   4.3   2.7
# [ A ] [ I ] [ N ] [ T ] [ M ] | [ L ] [ R ] [ E ] [ S ] [ C ]
# 12.5  11.7  12.1  15.5   3.9  |  6.8  10.2  19.9  10.1   6.7
# [. >] [ U ] [ B ] [ D ] [ K ] | [' "] [ H ] [, <] [ V ] [ G ]
#  2.9   4.5   2.2   5.9   1.0  |  0.8   7.8   2.5   1.8   3.2
# 15.7  18.8  18.1  27.1        |       26.1  35.5  16.2  12.6
#Heatmap score: 0.9373
#Bad bigrams:     311
#Fast bigrams:  22772
#Finger travel: 59321: [27, 69, 56, 106, 113, 127, 54, 49]
#Adjusted travel: 62073: [33, 73, 61, 107, 115, 131, 58, 51]
#Hand runs mean, max: (1.5600638869065824, 1.7686769899483836), (10, 9)
layout_AINT = [
    ';:', 'yY', 'pP', 'jJ', 'zZ',   'xX', 'qQ', 'oO', 'fF', 'wW',
    'aA', 'iI', 'nN', 'tT', 'mM',   'lL', 'rR', 'eE', 'sS', 'cC',
    '\'"','uU', 'bB', 'dD', 'kK',   ',<', 'hH', '.>', 'vV', 'gG'
]

# [ X ] [ F ] [. >] [ K ] [ Q ] | [ Z ] [ J ] [ A ] [ U ] [ W ]
#  0.1   4.0   2.7   1.2   0.2  |  0.1   0.2  12.6   4.7   3.3
# [ H ] [ S ] [ E ] [ T ] [ G ] | [ M ] [ N ] [ O ] [ I ] [ C ]
#  9.7  10.2  20.2  14.9   3.3  |  3.9  11.5  12.5  11.7   5.4
# [ R ] [ V ] [' "] [ D ] [ B ] | [; :] [ L ] [, <] [ Y ] [ P ]
#  8.8   1.7   1.4   6.1   2.7  |  0.3   7.8   2.4   2.9   3.4
# 18.6  15.9  24.3  28.4        |       23.9  27.5  19.4  12.0
#Heatmap score: 0.934840
#Finger travel: 32882: [57, 52, 39, 131, 95, 108, 73, 51]
#Adjusted travel: 35031: [61, 54, 56, 132, 97, 111, 82, 54]
#Hand runs mean, max: (1.6430906389301634, 1.7795863004408274), (8, 9)
#Bad bigrams: 173
#Fast bigrams: 12606
layout_HSETG = [
    'xX', 'fF', '.>', 'kK', 'qQ',   'zZ', 'jJ', 'aA', 'uU', 'wW',
    'hH', 'sS', 'eE', 'tT', 'gG',   'mM', 'nN', 'oO', 'iI', 'cC',
    'rR', 'vV', ',<', 'dD', 'bB',   ';:', 'lL', '\'"','yY', 'pP'
]

# [ Z ] [ U ] [ A ] [; :] [ Q ] | [ J ] [ K ] [. >] [ F ] [ X ]
#  0.1   4.7  12.6   0.3   0.2  |  0.2   1.2   2.7   4.0   0.1
# [ R ] [ I ] [ O ] [ N ] [ B ] | [ M ] [ T ] [ E ] [ S ] [ H ]
#  8.8  11.7  12.5  11.5   2.7  |  3.9  14.9  20.2  10.2   9.7
# [ W ] [ Y ] [, <] [ P ] [ V ] | [ G ] [ D ] [' "] [ C ] [ L ]
#  3.3   2.9   2.4   3.4   1.7  |  3.3   6.1   1.4   5.4   7.8
# 12.2  19.4  27.5  19.8        |       29.6  24.3  19.6  17.6
#Heatmap score: 0.9491
#Bad bigrams:     187
#Fast bigrams:  11324
#Finger travel: 32713: [29, 73, 108, 79, 142, 39, 83, 50]
#Adjusted travel: 34964: [33, 82, 110, 81, 143, 59, 82, 54]
#Hand runs mean, max: (1.6300638270157615, 1.6100541204039502), (9, 8)
layout_HSETM = [
    'xX', 'fF', '.>', 'kK', 'jJ',   'qQ', ';:', 'aA', 'uU', 'zZ',
    'hH', 'sS', 'eE', 'tT', 'mM',   'bB', 'nN', 'oO', 'iI', 'rR',
    'lL', 'cC', ',<', 'dD', 'gG',   'vV', 'pP', '\'"','yY', 'wW'
]

# [ F ] [ M ] [ O ] [ Q ] [ Z ] | [ B ] [ G ] [ L ] [ Y ] [ X ]
#  4.0   3.9  12.5   0.2   0.1  |  2.7   3.3   7.8   2.9   0.1
# [ S ] [ T ] [ E ] [ R ] [, <] | [ P ] [ D ] [ N ] [ I ] [ A ]
# 10.2  14.9  20.2   8.8   2.4  |  3.4   6.1  11.5  11.7  12.6
# [ V ] [ K ] [; :] [ H ] [ J ] | [ W ] [ C ] [' "] [ U ] [. >]
#  1.7   1.2   0.3   9.7   0.2  |  3.3   5.4   1.4   4.7   2.7
# 15.9  20.0  33.0  21.5        |       24.1  20.7  19.4  15.4
#Heatmap score: 0.936347
#Finger travel: 33273: [52, 49, 99, 86, 160, 68, 73, 26]
#Adjusted travel: 35271: [54, 59, 106, 88, 161, 75, 77, 32]
#Hand runs mean, max: (1.7881112774451098, 1.6797442216745486), (10, 9)
#Bad bigrams: 183
#Fast bigrams: 12735
layout_STER = [
    'fF', 'mM', 'oO', 'qQ', 'zZ',   'bB', 'gG', 'lL', 'yY', 'xX',
    'sS', 'tT', 'eE', 'rR', '\'"',  'pP', 'dD', 'nN', 'iI', 'aA',
    'vV', 'kK', ';:', 'hH', 'jJ',   'wW', 'cC', ',<', 'uU', '.>'
]

# [; :] [ Y ] [ P ] [ W ] [ Z ] | [ Q ] [ J ] [ O ] [ K ] [ X ]
#  0.3   2.6   3.8   2.7   0.1  |  0.3   0.6  13.0   1.0   0.2
# [ A ] [ I ] [ N ] [ C ] [ F ] | [ L ] [ R ] [ E ] [ T ] [ S ]
# 12.5  11.7  12.1   6.7   4.3  |  6.8  10.2  19.9  15.5  10.1
# [' "] [ U ] [ B ] [ D ] [ M ] | [. >] [ H ] [, <] [ G ] [ V ]
#  0.8   4.5   2.2   5.9   3.9  |  2.9   7.8   2.5   3.2   1.8
# 13.7  18.8  18.1  23.6        |       28.5  35.5  19.7  12.1
#Heatmap score: 0.9365
#Bad bigrams:     294
#Fast bigrams:  22674
#Finger travel: 58489: [11, 69, 56, 137, 131, 127, 44, 19]
#Adjusted travel: 62570: [18, 72, 62, 138, 132, 132, 58, 23]
#Hand runs mean, max: (1.5390484416612682, 1.7983133079352676), (9, 10)
layout_STERL = [
    'xX', 'kK', 'oO', 'jJ', 'qQ',   'zZ', 'wW', 'pP', 'yY', ';:',
    'sS', 'tT', 'eE', 'rR', 'lL',   'fF', 'cC', 'nN', 'iI', 'aA',
    'vV', 'gG', ',<', 'hH', '.>',   'mM', 'dD', 'bB', 'uU', '\'"'
]


layouts = {
    "QWERTY": layout_QWERTY,
    "Dvorak": layout_DVORAK,
    "PLUM": layout_PLUM,
    "Colemak": layout_COLEMAK,
    "Colemak-DH": layout_COLEMAKDH,
    "Workman": layout_WORKMAN,
    "NTRA": layout_NTRA,
    "NTRO": layout_NTRO,
    "AINT": layout_AINT,
    "HSETG": layout_HSETG,
    "HSETM": layout_HSETM,
    "STER": layout_STER,
    "STERL": layout_STERL
}

class TextStats:
    def __calc_symbol_freqs(self):
        self.symbol_freq = {}
        for c in self.text:
            if c in self.symbol_freq:
                self.symbol_freq[c] += 1
            else:
                self.symbol_freq[c] = 1

    def __calc_bigrams(self):
        self.bigrams = {}
        prev = ' '
        for c in self.text.lower():
            if c.isalpha() and prev.isalpha():
                bigram = (prev, c)
                if bigram in self.bigrams:
                    self.bigrams[bigram] += 1
                else:
                    self.bigrams[bigram] = 1
            prev = c

    def __init__(self, text):
        self.text = text
        self.__calc_symbol_freqs()
        self.__calc_bigrams()
        #b = [(s[0]+s[1], f) for s, f in self.bigrams.items()]
        #b.sort(key=lambda a: a[1])
        #print(b)

# Translate layouts into efficient lookup tables (maps):
# keymap_... = {symbol : (key, shift, hand, finger, x, y), ...}
#
# where each symbol maps to a tuple of shift, hand, finger and x/y
# coordinate. x/y is relative to the finger's home position.
#
# Fingers are numbered left to right 0 to 7
def calculate_key_props(key):
    row = int(key / 10)
    col = key - 10*row

    fingers = (0, 1, 2, 3, 3, 4, 4, 5, 6, 7)
    finger = fingers[col]

    hand = (col >= 5)

    home_cols = (0, 1, 2, 3, 3, 6, 6, 7, 8, 9)
    x = col - home_cols[col]
    y = row - 1

    return (hand, finger, x, y)

# Favourable bigrams that are easy and fast to type
# Left hand only, right hand will be auto-generated
fast_bigrams = [( 1,  2), ( 1, 13),
                 ( 2, 13),
                 (10,  2), (10, 12), (10, 13), (10, 23),
                 (11,  2), (11, 12), (11, 13), (11, 23),
                 (12, 13), (12, 23),
                 (13,  1), (13,  2), (13, 10), (13, 11), (13, 12), (13, 20),
                 (20, 12), (20, 13), (20, 22), (20, 23),
                 (21, 12), (21, 13), (21, 22), (21, 23),
                 (22, 23),
                 (23, 10), (23, 11), (23, 12), (23, 20), (23, 21), (23, 22)]
def mirror_key(k):
    return k + 9 - 2 * (k % 10)
fast_bigrams.extend([(mirror_key(a), mirror_key(b)) for a, b in fast_bigrams])
# Now turn it into a map for fasts lookup
fast_bigrams_map = {}
for a, b in fast_bigrams:
    if a in fast_bigrams_map:
        fast_bigrams_map[a].append(b)
    else:
        fast_bigrams_map[a] = [b]

class Keymap:
    key_props = [calculate_key_props(k) for k in range(30)]
    finger_linkage = ((1   , 0.25, 0  , 0  , 0  , 0  , 0   , 0   ),
                      (0.25, 1   , 0.5, 0  , 0  , 0  , 0   , 0   ),
                      (0   , 0.5 , 1  , 0.1, 0  , 0  , 0   , 0   ),
                      (0   , 0   , 0.1, 1  , 0  , 0  , 0   , 0   ),
                      (0   , 0   , 0  , 0  , 1  , 0.1, 0   , 0   ),
                      (0   , 0   , 0  , 0  , 0.1, 1  , 0.5 , 0   ),
                      (0   , 0   , 0  , 0  , 0  , 0.5, 1   , 0.25),
                      (0   , 0   , 0  , 0  , 0  , 0  , 0.25, 1   )
    )

    def __init__(self, layout):
        self.layout = layout
        self.keymap = {}
        for i in range(len(layout)):
            self.keymap[layout[i][0]] = (i, False) + self.key_props[i]
            self.keymap[layout[i][1]] = (i, True ) + self.key_props[i]

    def calc_heatmap(self, t):
        heatmap = [0 for k in range(30)]
        for symbol, key_props in self.keymap.items():
            try:
                heatmap[key_props[0]] += t.symbol_freq[symbol]
            except KeyError:
                pass
        return heatmap

    def calc_finger_travel(self, t):
        finger_pos = [(0, 0) for f in range(8)]
        dist = [0 for f in range(8)]
        for c in t.text:
            if c in self.keymap:
                (key, shift, hand, f, x, y) = self.keymap[c]
                d = math.sqrt((x - finger_pos[f][0])**2 + (y - finger_pos[f][1])**2)
                finger_pos[f] = (x, y)
                dist[f] += d

        return [int(a) for a in dist]

    def calc_adjusted_travel(self, t):
        finger_pos = [[0, 0] for f in range(8)]
        dist = [0 for f in range(8)]
        for c in t.text:
            if c in self.keymap:
                (key, shift, hand, f, x, y) = self.keymap[c]
                dx = x - finger_pos[f][0]
                dy = y - finger_pos[f][1]
                d = math.sqrt(dx*dx + dy*dy)
                for g in range(8):
                    finger_pos[g][0] += self.finger_linkage[f][g]*dx
                    finger_pos[g][1] += self.finger_linkage[f][g]*dy
                dist[f] += d

        return [int(a) for a in dist]

    def calc_hand_runs(self, t, debug = 0):
        last_hand = -1
        run_length = 0
        runs = ({}, {})
        hands = [c not in self.keymap and -1 or int(self.keymap[c][2]) for c in t.text]
        i = 0
        for hand in hands:
            if hand != last_hand:
                if last_hand >= 0:
                    if run_length in runs[last_hand]:
                        runs[last_hand][run_length] += 1
                    else:
                        runs[last_hand][run_length] = 1
                    if debug and run_length >= debug:
                        print("'%s'(%d), " % (t.text[i-run_length:i], run_length), end="")
                run_length = 0
                last_hand = hand

            run_length += 1
            i += 1

        if debug:
            print()
        return runs

    def calc_bigrams_same_finger(self, t, debug = 0):
        num = 0
        for sym, freq in t.bigrams.items():
            if sym[0] == sym[1]:
                continue
            if sym[0] in self.keymap and sym[1] in self.keymap:
                f1 = self.keymap[sym[0]][3]
                f2 = self.keymap[sym[1]][3]
                if f1 == f2:
                    num += freq
                    if debug:
                        print("%s%s(%d), " % (sym[0], sym[1], freq), end="")
        if debug:
            print()
        return num

    def calc_fast_bigrams(self, t, debug = 0):
        global fast_bigrams_map

        num = 0
        for sym, freq in t.bigrams.items():
            if sym[0] == sym[1]:
                continue
            if sym[0] not in self.keymap or sym[1] not in self.keymap:
                continue
            a = self.keymap[sym[0]][0]
            b = self.keymap[sym[1]][0]
            if a in fast_bigrams_map and b in fast_bigrams_map[a]:
                num += freq
                if debug:
                    print("%s%s(%d), " % (sym[0], sym[1], freq), end="")
        if debug:
            print()
        return num

    def eval_opt(self, text, debug = 0):
        self.heatmap = self.calc_heatmap(text)
        self.strokes = sum(self.heatmap)
        self.heatmap_score = score_heatmap(self.heatmap)
        self.normalized_heatmap = normalize(self.heatmap,
                sum(key_weights) / self.strokes)
        self.finger_heatmap = finger_heat(self.normalized_heatmap)
        self.finger_score = score_finger_heat(self.finger_heatmap)

        self.bad_bigrams = self.calc_bigrams_same_finger(text, debug)
        self.fast_bigrams = self.calc_fast_bigrams(text, debug)

    def eval(self, text, debug = 0):
        self.eval_opt(text, debug)

        self.finger_travel = self.calc_finger_travel(text)
        self.adjusted_travel = self.calc_adjusted_travel(text)
        self.normalized_travel = normalize(self.finger_travel, 1000 / self.strokes)
        self.norm_adj_travel = normalize(self.adjusted_travel, 1000 / self.strokes)

        self.hand_runs = self.calc_hand_runs(text, debug)

    def print_layout_heatmap(self):
        l = [a == b.lower() and '[ ' + b + ' ]' or '[' + a + ' ' + b + ']' for a, b in self.layout]
        h = self.normalized_heatmap
        f = self.finger_heatmap
        print(" %5.5s %5.5s %5.5s %5.5s %5.5s | %5.5s %5.5s %5.5s %5.5s %5.5s" % tuple(l[0:10]))
        print("%5.1f %5.1f %5.1f %5.1f %5.1f  |%5.1f %5.1f %5.1f %5.1f %5.1f" % tuple(h[0:10]))
        print(" %5.5s %5.5s %5.5s %5.5s %5.5s | %5.5s %5.5s %5.5s %5.5s %5.5s" % tuple(l[10:20]))
        print("%5.1f %5.1f %5.1f %5.1f %5.1f  |%5.1f %5.1f %5.1f %5.1f %5.1f" % tuple(h[10:20]))
        print(" %5.5s %5.5s %5.5s %5.5s %5.5s | %5.5s %5.5s %5.5s %5.5s %5.5s" % tuple(l[20:30]))
        print("%5.1f %5.1f %5.1f %5.1f %5.1f  |%5.1f %5.1f %5.1f %5.1f %5.1f" % tuple(h[20:30]))
        print("%5.1f %5.1f %5.1f %5.1f        |      %5.1f %5.1f %5.1f %5.1f" % tuple(f))

    def print_short_summary(self):
        self.print_layout_heatmap()
        print("Heatmap score: %.4f" % self.heatmap_score)
        print("Bad bigrams:   %6d" % self.bad_bigrams)
        print("Fast bigrams:  %6d" % self.fast_bigrams)

    def print_summary(self):
        self.print_short_summary()
        print("Finger travel: %d: %s" % (sum(self.finger_travel), [int(a) for a in self.normalized_travel]))
        print("Adjusted travel: %d: %s" % (sum(self.adjusted_travel), [int(a) for a in self.norm_adj_travel]))
        print("Hand runs mean, max: %s, %s" % (repr(mean_runs(self.hand_runs)), repr(max_runs(self.hand_runs))))

keymaps = {}
for name, layout in layouts.items():
    keymaps[name] = Keymap(layout)

#key_weights = [1,     12, 21,  6, 3,   3,  6, 21, 12,  1,
#               3,  5, 12, 18, 18, 9,   9, 18, 18, 12,  5,  3,
#               4,      6,  6,  6, 3,   3,  6,  6,  6,  4]
key_weights = [ 1,  6,  7,  2, 1,   1,  2,  7,  6,  1,
               10, 12, 15, 10, 4,   4, 10, 15, 12, 10,
                4,  2,  3,  5, 3,   3,  5,  3,  2,  4]
finger_weights = [15, 20, 25, 25,   25, 25, 20, 15]
sorted_key_weights = key_weights[:]
sorted_key_weights.sort()
sorted_finger_weights = finger_weights[:]
sorted_finger_weights.sort()

def score_heatmap(heatmap):
    global key_weights, sorted_key_weigts

    score = sum(map(operator.mul, heatmap, key_weights))

    sorted_heatmap = heatmap[:]
    sorted_heatmap.sort()
    best_score = sum(map(operator.mul, sorted_heatmap, sorted_key_weights))
    sorted_heatmap.reverse()
    worst_score = sum(map(operator.mul, sorted_heatmap, sorted_key_weights))

    return (score - worst_score) / (best_score - worst_score)

def normalize(heatmap, factor):
    return [h * factor for h in heatmap]

def finger_heat(h):
    f = [h[ 0]+h[10]+h[20],
         h[ 1]+h[11]+h[21],
         h[ 2]+h[12]+h[22],
         h[ 3]+h[ 4]+h[13]+h[14]+h[23]+h[24],
         h[ 5]+h[ 6]+h[15]+h[16]+h[25]+h[26],
         h[ 7]+h[17]+h[27],
         h[ 8]+h[18]+h[28],
         h[ 9]+h[19]+h[29]]
    return f

def score_finger_heat(heatmap):
    global finger_weights, sorted_finger_weights

    score = sum(map(operator.mul, heatmap, finger_weights))

    sorted_heatmap = heatmap[:]
    sorted_heatmap.sort()
    best_score = sum(map(operator.mul, sorted_heatmap, sorted_finger_weights))
    sorted_heatmap.reverse()
    worst_score = sum(map(operator.mul, sorted_heatmap, sorted_finger_weights))

    return (score - worst_score) / (best_score - worst_score)

def mean_runs(runs):
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

def median_runs(runs):
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

def max_runs(runs):
    return (max(runs[0].keys()), max(runs[1].keys()))

# Different transformations to a keyboard layout that make bigger
# changes while trying to leave some properties intact. The hope is,
# that this will make it more likely to find good gradients to follow
# in the search for an optimal layout.

# Swapping fingers does not change same-finger bigrams.
def mutate_swap_fingers(layout, rand):
    a, b = rand.sample((0, 1, 2, 3, 7, 8, 9), k=2)
    if a == 3 or b == 3:
        return [(lambda l, i, c:
                 l[i + 9 - 2*c] if c >= 3 and c <= 6 else l[i])(layout, i, i%10)
                for i in range(30)]
    else:
        return [(lambda l, i, c:
                 l[i - a + b] if c == a else
                 l[i - b + a] if c == b else
                 l[i])(layout, i, i%10) for i in range(30)]

# Swapping rows does not change same-finger bigrams. Swap rows in one
# hand only.
def mutate_swap_rows(layout, rand):
    h = rand.randint(0, 1)
    a, b = rand.sample(range(3), k=2)
    return [(lambda l, i, r:
             l[i + (b - a) * 10] if r == a else
             l[i + (a - b) * 10] if r == b else
             l[i])(layout, i, int(i / 10)) if int((i % 10) / 5) == h else
             layout[i] for i in range(30)]

# Swapping keys belonging to the same finger does not change same finger
# bigrams.
def mutate_swap_finger_keys(layout, rand):
    f = rand.randint(0, 7)
    if f < 3:
        keys = (f, f + 10, f + 20)
    elif f < 5:
        c0 = f * 2 - 3
        keys = (c0, c0 + 1, c0 + 10, c0 + 11, c0 + 20, c0 + 21)
    else:
        keys = (f + 2, f + 12, f + 22)
    a, b = rand.sample(keys, k=2)
    return [layout[b] if i == a else
            layout[a] if i == b else
            layout[i] for i in range(30)]

# Swap a pair of keys with similar weight minimize impact on the heat
# map score
#
# Calculate a ranking of keys by weight to help with that
ranked_weight_index = [(key_weights[i], i) for i in range(30)]
ranked_weight_index.sort(key = lambda a: a[0])
key_from_rank = [wi[1] for wi in ranked_weight_index]
rank_from_key = [key_from_rank.index(k) for k in range(30)]
def mutate_swap_ranks(layout, rand):
    window_size = 8
    window_start = rand.randint(0, 30-window_size)
    a, b = rand.sample(range(window_start, window_start+window_size), k=2)
    return [layout[key_from_rank[b]] if rank_from_key[i] == a else
            layout[key_from_rank[a]] if rank_from_key[i] == b else
            layout[i] for i in range(30)]

# Basic mutation by swapping a random pair of keys
# This does not attemt to preserve any layout properties.
def mutate_swap_keys(layout, rand):
    a, b = rand.sample(range(30), k=2)
    return [layout[b] if i == a else
            layout[a] if i == b else
            layout[i] for i in range(30)]

mutations = (
    mutate_swap_fingers,
    mutate_swap_finger_keys,
    mutate_swap_ranks,
    mutate_swap_keys
)

def mutate(layout, rand):
    op = rand.randint(0, len(mutations)-1)
    return mutations[op](layout, rand)

def anneal(layout, function, seed=None, shuffle=False):
    """Simulated annealing optimizatio

    Start with layout. Use function to calculate a score for the
    layout. The function should return floats in range 0-1 with 0
    being the worst and 1 the best possible score.

    Returns the optimized layout.

    """
    rand = random.Random()
    rand.seed(seed)
    if shuffle:
        layout = rand.sample(layout, k=len(layout))
    noise = 0.5
    noise_step = 0.000001
    noise_floor = 0.005
    best_score = function(Keymap(layout))
    accepted_score = best_score
    best_layout = layout
    print_interval = 100
    count = print_interval

    while noise > noise_floor:
        new_layout = mutate(layout, rand)
        new_keymap = Keymap(new_layout)
        new_score = function(new_keymap)

        if new_score > best_score:
            print("%.5f %.5f %.5f" % (noise, new_score, best_score))
            count = 1
            # VT100 clear line (top row of the last keymap)
            print("\x1b[2K")
            # Print a new keymap one row lower
            new_keymap.print_short_summary()
            # VT100: cursor up 11 rows
            print("\x1b[11A", end="")
            # Improving the score is like going to a lower energy state,
            # which is exothermic. This allows finding more paths from
            # the new best solution.
            noise += new_score - best_score
            best_score = new_score
            best_layout = new_layout

        if noise > 0:
            noisy_score = new_score + noise
            noise *= 1 - noise_step
        else:
            noisy_score = new_score

        if noisy_score > best_score:
            layout = new_layout
            accepted_score = new_score
        elif new_score + 5*noise < best_score:
            # We're stuck in a local optimum with little hope of
            # getting back to the best known optimum. Reset.
            layout = best_layout

        count -= 1
        if count <= 0:
            flag = ' '
            if accepted_score < 0:
                accepted_score = -accepted_score
                flag = '!'
            print("%.5f %.5f %.5f%c" % (noise, accepted_score, best_score,
                                        flag), end='\r')
            count = print_interval
            accepted_score = -accepted_score

    print()
    return best_layout

def swap_fingers(layout, mask):
    swap = (((0, 9), (10, 19), (20, 29)),
            ((1, 8), (11, 18), (21, 28)),
            ((2, 7), (12, 17), (22, 27)),
            ((3, 6), (4, 5), (13, 16), (14, 15), (23, 26), (24, 25)))

    new_layout = layout[:]

    for bit in range(4):
        if (1 << bit) & mask:
            for l, r in swap[bit]:
                new_layout[r] = layout[l]
                new_layout[l] = layout[r]

    return new_layout

text = TextStats(sys.stdin.read())

for name, keymap in keymaps.items():
    print("*** Layout: %s ***" % name)
    keymap.eval(text)
    keymap.print_summary()



def optimize_runs(keymap):
    global text

    runs = keymap.calc_hand_runs(text)
    means = mean_runs(runs)
    mean = sum(means) / len(means)
    return (1.0 - 1/mean)

def optimize_weights(keymap):
    global text

    heatmap = keymap.calc_heatmap(text)
    fingers = finger_heat(heatmap)
    key_score = score_heatmap(heatmap)
    finger_score = score_finger_heat(fingers)
    #return (2.0 - (1.0 - key_score)**2 - (1.0 - finger_score)**2) / 2
    return (math.sqrt(key_score) + math.sqrt(finger_score)) / 2
    #return (key_score + finger_score) / 2

def optimize_bad_bigrams(keymap):
    bad_bigrams = keymap.bad_bigrams / keymap.strokes
    return 1.0 - bad_bigrams**(1/3)

def optimize_fast_bigrams(keymap):
    good_bigrams = keymap.fast_bigrams / keymap.strokes
    return math.sqrt(good_bigrams)

def optimize_travel(keymap):
    global text

    travel = sum(keymap.calc_finger_travel(text)) / keymap.strokes / 2
    return 1 - travel

def optimize(keymap):
    global text

    keymap.eval_opt(text)
    scores = (optimize_weights(keymap),
              optimize_bad_bigrams(keymap),
              optimize_fast_bigrams(keymap))
    w = (1, 2, 1)
    wsum = sum((w[i] * scores[i] for i in range(len(scores))))

    return wsum / sum(w)

new_layout = anneal(layout_DVORAK, optimize, seed=None, shuffle=True)
#new_layout = layout_GAU

new_keymap = Keymap(new_layout)
new_keymap.eval(text, 6)
new_keymap.print_summary()

# max_means = 0
# min_means = 100
# max_keymap = None
# min_keymap = None
# for swap_mask in range(8):
#     swap_layout = swap_fingers(new_layout, swap_mask)
#     swap_keymap = Keymap(swap_layout)
#     runs = swap_keymap.calc_hand_runs(text)
#     means = sum(mean_runs(runs))
#     print("%d: %f" % (swap_mask, means))
#     if means > max_means:
#         max_means = means
#         max_keymap = swap_keymap
#     if means < min_means:
#         min_means = means
#         min_keymap = swap_keymap

# max_keymap.eval(text, 6)
# max_keymap.print_summary()
# min_keymap.eval(text, 6)
# min_keymap.print_summary()
