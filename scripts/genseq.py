#!/usr/bin/python3

import sys

# Keys are numbered 0-31. Even numbers are left hand, odd numbers are
# right hand, arranged such that for every left hand key x, the right
# hand mirror image is x+1.
#
#       8 |  6 |  4 |  2    0 ||  1    3 |  5 |  7 |  9           | 0
# 20   18 | 16 | 14 | 12   10 || 11   13 | 15 | 17 | 19   21      | 1
#      30 | 28 | 26 | 24   22 || 23   25 | 27 | 29 | 31           | 2
#         |    |    |         ||         |    |    |
#   pinky |ring|mid |  index  ||  index  | mid|ring|pinky
#       3 |  2 |  1 |      0  ||  0      | 1  | 2  | 3
#                             ||
#          left hand          ||         right hand
#               0             ||               1

def key_hand(key):
    return key & 1

def key_row(key):
    if key < 10:
        return 0
    elif key < 22:
        return 1
    else:
        return 2

def key_col(key):
    row_start = (0, 10, 22)
    r = key_row(key)
    return (key - row_start[r]) >> 1

def col_finger(col):
    fingers = (0, 0, 1, 2, 3, 3)
    return fingers[col]

def key_finger(key):
    return col_finger(key_col(key))

def key_number(h, r, c):
    row_start = (0, 10, 22)
    return row_start[r] + (c << 1) + h

all_keys = range(32)
lh_keys = [key for key in all_keys if key_hand(key) == 0]
rh_keys = [key for key in all_keys if key_hand(key) == 1]

def gen_pairs():
    pairs = []
    # left hand pairs
    pairs += [(k, l) for k in lh_keys for l in lh_keys]
    # right hand pairs
    pairs += [(k, l) for k in rh_keys for l in rh_keys]
    # left hand with one key from right hand in either order
    pairs += [(k, 15) for k in lh_keys]
    pairs += [(15, k) for k in lh_keys]
    # right hand with one key from left hand in either order
    pairs += [(k, 14) for k in rh_keys if k != 15]
    pairs += [(14, k) for k in rh_keys if k != 15]

    return pairs

categories = {0: "same key",
              1: "same finger adj key up",   # only mid, botton row
              2: "same finger adj key down", # only top, mid row
              3: "same finger adj key side", # only pinky and index finger
              4: "same finger dist key",     # skipping a row, top/bottom row
              5: "adj finger + row 0",
              6: "adj finger + row 1",
              7: "adj finger + row 2",
              8: "adj finger - row 0",
              9: "adj finger - row 1",
              10: "adj finger - row 2",
              11: "dist finger row 1",
              12: "dist finger row 1",
              13: "dist finger row 1",
              14: "other hand"}              # middle finger, home row

def pick_next_key(key, cat):
    if cat == 0: # same key, this one is easy
        return key

    h = key_hand(key)
    r = key_row(key)
    c = key_col(key)
    f = col_finger(c)

    if cat == 1: # same finger, adjacent key up
        if r == 0:
            return None
        elif c == 5:
            return key_number(h, r-1, 4)
        else:
            return key_number(h, r-1, c)
    elif cat == 2: # same finger, adjacent key down
        if r == 2:
            return None
        elif c == 5:
            return key_number(h, r+1, 4)
        else:
            return key_number(h, r+1, c)
    elif cat == 3: # same finger, adjacent key side
        if c == 0 or c == 4:
            return key + 2
        elif c == 1 or c == 5:
            return key - 2
        else:
            return None
    elif cat == 4: # same finger, distant key (skipping one row)
        if r == 0:
            return key_number(h, 2, c)
        elif r == 2:
            return key_number(h, 0, c)
        else:
            return None
    elif cat <= 7:
        if f == 3:
            return None
        else:
            if c == 0:
                c = 1
            return key_number(h, cat - 5, c+1)
    elif cat <= 10:
        if f == 0:
            return None
        else:
            if c == 5:
                c = 4
            return key_number(h, cat - 8, c-1)
    elif cat <= 13:
        if c < 3:
            c = 4
        else:
            c = 1
        return key_number (h, cat - 11, c)
    elif cat == 14:
        h = (h + 1) & 1
        return key_number (h, 1, 2)
    else:
        return None

def gen_cat_triplets(pairs):
    triplets = []

    for pair in pairs:
        for cat in range(15):
            lead = (pick_next_key(pair[0], cat), pair[0], pair[1])
            trail = (pair[0], pair[1], pick_next_key(pair[1], cat))

            if lead[0] != None and lead not in triplets:
                triplets.append(lead)
            if trail[2] != None and trail not in triplets:
                triplets.append(trail)

    return triplets

def gen_all_triplets(pairs):
    triplets = [(pair1[0], pair1[1], pair2[1])
                for pair1 in pairs for pair2 in pairs
                if pair1[1] == pair2[0]]

    return triplets

def triplet_filter(t):
    h = key_hand(t[0]) + key_hand(t[1]) + key_hand(t[2])
    if h != 0:
        return False

    r = [key_row(k) for k in t]
    
    # If all 3 keys are in the same row, let the equivalent triplet on
    # the home row represent it
    if r[0] == r[1] and r[0] == r[2]:
        return r[0] == 1

    # If the keys are using only two adjacent rows, let the equivalent
    # triplet on the top two rows represent it, but be careful not to
    # eliminate triplets using column 5, which only exists on row 1.
    # row.
    c5 = [k for k in t if key_col(k) == 5]
    r12 = [x for x in r if x >= 1]
    if not c5 and len(r12) == 3:
        return False

    return True

pairs = gen_pairs()
cat_triplets = gen_cat_triplets(pairs)
all_triplets = gen_all_triplets(pairs)
filtered_triplets = [t for t in all_triplets if triplet_filter(t)]

print("Complete list of triples:  %d" % len(all_triplets))
print("Category-based triplets:   %d" % len(cat_triplets))
print("Filtered list of triplets: %d" % len(filtered_triplets))
