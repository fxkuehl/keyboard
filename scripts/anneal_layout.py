#!/usr/bin/python3

import sys
import time
import random
from textstats import TextStats
from keymap import Keymap

# The Dvorak layout serves as a good starting point for the set of symbols
# represented by the core 30 keys.
layout_DVORAK = [
    '\'"',',<', '.>', 'pP', 'yY',   'fF', 'gG', 'cC', 'rR', 'lL',
    'aA', 'oO', 'eE', 'uU', 'iI',   'dD', 'hH', 'tT', 'nN', 'sS',
    ';:', 'qQ', 'jJ', 'kK', 'xX',   'bB', 'mM', 'wW', 'vV', 'zZ'
]

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
ranked_weight_index = [(Keymap._key_weights[i], i) for i in range(30)]
ranked_weight_index.sort(key = lambda a: a[0])
key_from_rank = [wi[1] for wi in ranked_weight_index]
def mutate_swap_ranks(layout, rand):
    window_size = 8
    window_start = rand.randint(0, 30-window_size)
    a, b = rand.sample(range(window_start, window_start+window_size), k=2)
    a = key_from_rank[a]
    b = key_from_rank[b]
    return [layout[b] if i == a else
            layout[a] if i == b else
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
    print_interval = 10000
    count = print_interval
    last_time = time.time()
    rate = 0

    while noise > noise_floor:
        new_layout = mutate(layout, rand)
        new_keymap = Keymap(new_layout)
        new_score = function(new_keymap)

        if new_score > best_score:
            print("%.5f %.5f %.5f" % (noise, new_score, best_score))
            count = 1
            last_time = None
            # VT100 clear line (top row of the last keymap)
            print("\x1b[2K")
            # Print a new keymap one row lower
            new_keymap.print_short_summary()
            # VT100: cursor up 13 rows
            print("\x1b[13A", end="")
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
            this_time = time.time()
            if last_time:
                delta_time = this_time - last_time
                rate = print_interval / delta_time
            last_time = this_time
            flag = ' '
            if accepted_score < 0:
                accepted_score = -accepted_score
                flag = '!'
            print("%.5f %.5f %.5f %6.0f%c" %
                    (noise, accepted_score, best_score, rate, flag),
                    end='\r')
            count = print_interval
            accepted_score = -accepted_score

    print()
    return best_layout

text = TextStats(sys.stdin.read())

def optimize(keymap):
    global text

    keymap.eval_score(text)
    return keymap.overall_score

new_layout = anneal(layout_DVORAK, optimize, seed=None, shuffle=True)

new_keymap = Keymap(new_layout, auto_mirror=True)
new_keymap.eval(text, 6)
new_keymap.print_summary()
new_keymap.save_to_db()
