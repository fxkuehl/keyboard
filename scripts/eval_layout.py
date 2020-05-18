#!/usr/bin/python3

import sys
import math
import random

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

layout_COLEMAK = [
    'qQ', 'wW', 'fF', 'pP', 'gG',   'jJ', 'lL', 'uU', 'yY', ';:',
    'aA', 'rR', 'sS', 'tT', 'dD',   'hH', 'nN', 'eE', 'iI', 'oO',
    'zZ', 'xX', 'cC', 'vV', 'bB',   'kK', 'mM', ',<', '.>', '/?'
]

layout_WORKMAN = [
    'qQ', 'dD', 'rR', 'wW', 'bB',   'jJ', 'fF', 'uU', 'pP', ';:',
    'aA', 'sS', 'hH', 'tT', 'gG',   'yY', 'nN', 'eE', 'oO', 'iI',
    'zZ', 'xX', 'mM', 'cC', 'vV',   'kK', 'lL', ',<', '.>', '/?'
]

layout_SOUL = [
    'zZ', 'qQ', 'tT', 'hH', ';:',   ',<', 'gG', 'eE', 'iI', 'kK',
    'pP', 'aA', 'dD', 'nN', 'rR',   'cC', 'sS', 'oO', 'uU', 'lL',
    'bB', 'xX', 'mM', 'vV', '/?',   '.>', 'fF', 'jJ', 'yY', 'wW'
]

layout_AIR = [
    ';:', 'uU', 'lL', 'qQ', 'xX',   '/?', 'zZ', 'oO', 'kK', 'wW',
    'aA', 'iI', 'rR', 'sS', 'gG',   'bB', 'nN', 'eE', 'tT', 'dD',
    'pP', 'yY', 'mM', 'fF', 'vV',   ',<', 'hH', '.>', 'jJ', 'cC'
]

layouts = {
    "QWERTY": layout_QWERTY,
    "Dvorak": layout_DVORAK,
    "Colemak": layout_COLEMAK,
    "Workman": layout_WORKMAN,
    "SOUL": layout_SOUL,
    "AIR": layout_AIR,
}

class TextStats:
    def __calc_symbol_freqs(self):
        self.symbol_freq = {}
        for c in self.text:
            if c in self.symbol_freq:
                self.symbol_freq[c] += 1
            else:
                self.symbol_freq[c] = 1

    def __calc_bigraphs(self):
        self.bigraphs = {}
        prev = ' '
        for c in self.text.lower():
            if c.isalpha() and prev.isalpha():
                bigraph = (prev, c)
                if bigraph in self.bigraphs:
                    self.bigraphs[bigraph] += 1
                else:
                    self.bigraphs[bigraph] = 1
            prev = c

    def __init__(self, text):
        self.text = text
        self.__calc_symbol_freqs()
        self.__calc_bigraphs()
        #b = [(s[0]+s[1], f) for s, f in self.bigraphs.items()]
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

    def key_strokes(self, t):
        return len([1 for c in t.text if c in self.keymap])

    def calc_heatmap(self, t):
        heatmap = [0 for k in range(30)]
        for symbol, key_props in self.keymap.items():
            if symbol in t.symbol_freq:
                heatmap[key_props[0]] += t.symbol_freq[symbol]
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

    def calc_bigraphs_same_finger(self, t, debug = 0):
        num = 0
        for sym, freq in t.bigraphs.items():
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

    def eval(self, text, debug = 0):
        self.strokes = self.key_strokes(text)

        self.heatmap = self.calc_heatmap(text)
        self.heatmap_score = score_heatmap(self.heatmap)
        self.normalized_heatmap = normalize(self.heatmap, sum(key_weights) / self.strokes)
        self.finger_heatmap = finger_heat(self.normalized_heatmap)
        self.finger_score = score_finger_heat(self.finger_heatmap)

        self.finger_travel = self.calc_finger_travel(text)
        self.adjusted_travel = self.calc_adjusted_travel(text)
        self.normalized_travel = normalize(self.finger_travel, 1000 / self.strokes)
        self.norm_adj_travel = normalize(self.adjusted_travel, 1000 / self.strokes)

        self.hand_runs = self.calc_hand_runs(text, debug)

        self.bad_bigraphs = self.calc_bigraphs_same_finger(text, debug)

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

    def print_summary(self):
        self.print_layout_heatmap()
        print("Heatmap score: %f" % self.heatmap_score)
        print("Finger travel: %d: %s" % (sum(self.finger_travel), [int(a) for a in self.normalized_travel]))
        print("Adjusted travel: %d: %s" % (sum(self.adjusted_travel), [int(a) for a in self.norm_adj_travel]))
        print("Hand runs mean, max: %s, %s" % (repr(mean_runs(self.hand_runs)), repr(max_runs(self.hand_runs))))
        print("Bad bigraphs: %d" % self.bad_bigraphs)

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

    score = sum((a * b for a, b in zip(heatmap, key_weights)))

    sorted_heatmap = heatmap[:]
    sorted_heatmap.sort()
    best_score = sum((a * b for a, b in zip(sorted_heatmap, sorted_key_weights)))
    sorted_heatmap.reverse()
    worst_score = sum((a * b for a, b in zip(sorted_heatmap, sorted_key_weights)))

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

    score = sum((a * b for a, b in zip(heatmap, finger_weights)))

    sorted_heatmap = heatmap[:]
    sorted_heatmap.sort()
    best_score = sum((a * b for a, b in zip(sorted_heatmap, sorted_finger_weights)))
    sorted_heatmap.reverse()
    worst_score = sum((a * b for a, b in zip(sorted_heatmap, sorted_finger_weights)))

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

def mutate(layout, rand):
    a = rand.randint(0, 29)
    b = rand.randint(0, 28)
    if b >= a:
        b += 1
    new_layout = [i == a and layout[b] or i == b and layout[a] or layout[i] for i in range(30)]
    return new_layout

def anneal(layout, function):
    """Simulated annealing optimizatio

    Start with layout. Use function to calculate a score for the
    layout. The function should return floats in range 0-1 with 0
    being the worst and 1 the best possible score.

    Returns the optimized layout.

    """
    rand = random.Random()
    rand.seed(0xdeadbeef)
    noise = 0.5
    noise_step = 0.9999
    countdown = 1000

    score = function(layout)
    while noise > 0.00001 and countdown > 0:
        new_layout = mutate(layout, rand)
        new_score = function(new_layout)
        if noise > 0:
            noisy_score = new_score + rand.uniform(0, noise)
            noise *= noise_step
        else:
            noisy_score = new_score
        if noisy_score > score:
            layout = new_layout
            score = new_score
            print("%.5f %4d %.5f" % (noise, countdown, new_score), end='\r')
            countdown = 1000
        else:
            countdown -= 1
#        print(noise)

    print()
    return new_layout

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
    return (score_heatmap(heatmap) + score_finger_heat(fingers)) / 2

def optimize_bigraphs(keymap):
    global text

    bad_bigraphs = keymap.calc_bigraphs_same_finger(text) / keymap.key_strokes(text)
    if bad_bigraphs < 0.05:
        return 1.0 - bad_bigraphs * 10
    else:
        return 0.525 - bad_bigraphs / 2

def optimize(layout):
    keymap = Keymap(layout)
    scores = (#optimize_runs(keymap),
              optimize_weights(keymap),
              optimize_bigraphs(keymap))
    w = (1, 1)
    wsum = sum((w[i] * scores[i] for i in range(len(scores))))

    return wsum / sum(w)

new_layout = anneal(layout_QWERTY, optimize)
#new_layout = layout_AIR

new_keymap = Keymap(new_layout)
new_keymap.eval(text, 6)
new_keymap.print_summary()

max_means = 0
min_means = 100
max_keymap = None
min_keymap = None
for swap_mask in range(8):
    swap_layout = swap_fingers(new_layout, swap_mask)
    swap_keymap = Keymap(swap_layout)
    runs = swap_keymap.calc_hand_runs(text)
    means = sum(mean_runs(runs))
    print("%d: %f" % (swap_mask, means))
    if means > max_means:
        max_means = means
        max_keymap = swap_keymap
    if means < min_means:
        min_means = means
        min_keymap = swap_keymap

max_keymap.eval(text, 6)
max_keymap.print_summary()
min_keymap.eval(text, 6)
min_keymap.print_summary()
