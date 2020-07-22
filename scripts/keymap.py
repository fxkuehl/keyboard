import sys
import math
import operator
import itertools

# Translate layouts into efficient lookup tables (maps):
# keymap_... = {symbol : (key, shift, hand, finger, x, y), ...}
#
# where each symbol maps to a tuple of shift, hand, finger and x/y
# coordinate. x/y is relative to the finger's home position.
#
# Fingers are numbered left to right 0 to 7
def _calculate_key_props(key):
    row = int(key / 10)
    col = key - 10*row

    fingers = (0, 1, 2, 3, 3, 4, 4, 5, 6, 7)
    finger = fingers[col]

    hand = (col >= 5)

    home_cols = (0, 1, 2, 3, 3, 6, 6, 7, 8, 9)
    x = col - home_cols[col]
    y = row - 1

    return (hand, finger, x, y)

def _mirror_key(k):
    return k + 9 - 2 * (k % 10)

class Keymap:
    _key_props = [_calculate_key_props(k) for k in range(30)]

    def __init__(self, layout):
        self.layout = layout
        self.keymap = {}
        for i in range(len(layout)):
            self.keymap[layout[i][0]] = (i, False) + self._key_props[i]
            self.keymap[layout[i][1]] = (i, True ) + self._key_props[i]

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

    _finger_linkage = ((1   , 0.25, 0  , 0  , 0  , 0  , 0   , 0   ),
                       (0.25, 1   , 0.5, 0  , 0  , 0  , 0   , 0   ),
                       (0   , 0.5 , 1  , 0.1, 0  , 0  , 0   , 0   ),
                       (0   , 0   , 0.1, 1  , 0  , 0  , 0   , 0   ),
                       (0   , 0   , 0  , 0  , 1  , 0.1, 0   , 0   ),
                       (0   , 0   , 0  , 0  , 0.1, 1  , 0.5 , 0   ),
                       (0   , 0   , 0  , 0  , 0  , 0.5, 1   , 0.25),
                       (0   , 0   , 0  , 0  , 0  , 0  , 0.25, 1   )
    )
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
                    finger_pos[g][0] += self._finger_linkage[f][g]*dx
                    finger_pos[g][1] += self._finger_linkage[f][g]*dy
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

    _finger_keys = (
            (0, 10, 20),
            (1, 11, 21),
            (2, 12, 22),
            (3, 4, 13, 14, 23, 24),
            (5, 6, 15, 16, 25, 26),
            (7, 17, 27),
            (8, 18, 28),
            (9, 19, 29))
    _same_finger_bigrams = []
    for keys in _finger_keys:
        _same_finger_bigrams += list(itertools.permutations(keys, 2))

    # Favourable bigrams that are easy and fast to type
    # Left hand only, right hand will be auto-generated
    # From fast bigrams we can also construct fast 3-grams
    # that go in one direction left-right or right-left.
    # Changing direction is awkward.
    _fast_bigrams_lr = [( 1,  2), ( 1, 13),
                        ( 2, 13),
                        (10,  2), (10, 11), (10, 12), (10, 13), (10, 23),
                        (11, 12), (11, 13), (11, 23),
                        (12, 13), (12, 23),
                        (20, 11), (20, 12), (20, 13), (20, 23)]
    _fast_bigrams_rl = [(13,  1), (13,  2), (13, 10), (13, 11), (13, 12), (13, 20),
                        (23, 10), (23, 11), (23, 12), (23, 20),
                        ( 2,  1), ( 2, 10),
                        (12, 11), (12, 10), (12, 20),
                        (11, 10), (11, 20)]
    _fast_bigrams = _fast_bigrams_lr + _fast_bigrams_rl
    _fast_bigrams += [(_mirror_key(a), _mirror_key(b)) for a, b in _fast_bigrams]

    # Discourage non-fast bi-grams in the same hand.
    _slow_bigrams = list(itertools.permutations(
            (0, 1, 2, 3, 4, 10, 11, 12, 13, 14, 20, 21, 22, 23, 24), 2))
    _slow_bigrams += [(_mirror_key(a), _mirror_key(b))
                      for a, b in _slow_bigrams]
    for bigram in _fast_bigrams:
        _slow_bigrams.remove(bigram)

    def _calc_bigrams(self, t, bigrams, freq_map=None):
        num = 0
        for a, b in bigrams:
            bigram = (self.layout[a][0], self.layout[b][0])
            try:
                num += t.bigrams[bigram]
                if freq_map != None:
                    freq_map[bigram] = t.bigrams[bigram]
            except KeyError:
                pass
        return num
    def calc_bad_bigrams(self, t, freq_map=None):
        return self._calc_bigrams(t, self._same_finger_bigrams, freq_map)
    def calc_fast_bigrams(self, t, freq_map=None):
        return self._calc_bigrams(t, self._fast_bigrams, freq_map)
    def calc_slow_bigrams(self, t, freq_map=None):
        return self._calc_bigrams(t, self._slow_bigrams, freq_map)

    _fast_trigrams = [(a[0], a[1], b[1]) for a, b in
            itertools.permutations(_fast_bigrams_lr, 2) if a[1] == b[0]]
    _fast_trigrams += [(a[0], a[1], b[1]) for a, b in
            itertools.permutations(_fast_bigrams_rl, 2) if a[1] == b[0]]
    _fast_trigrams += [(_mirror_key(a), _mirror_key(b), _mirror_key(c))
                       for a, b, c in _fast_trigrams]
    #print("bad bigrams:", len(_same_finger_bigrams))
    #print("fast bigrams:", len(_fast_bigrams))
    #print("slow bigrams:", len(_slow_bigrams))
    #print(_slow_bigrams)
    #print("fast trigrams:", len(_fast_trigrams))
    #print(_fast_trigrams)
    def calc_fast_trigrams(self, t, freq_map=None):
        num = 0
        for a, b, c in self._fast_trigrams:
            trigram = (self.layout[a][0], self.layout[b][0], self.layout[c][0])
            try:
                num += t.trigrams[trigram]
                if freq_map != None:
                    freq_map[trigram] = t.trigrams[trigram]
            except KeyError:
                pass
        return num

    _key_weights = [ 1,  6,  7,  2, 1,   1,  2,  7,  6,  1,
                    10, 12, 15, 10, 4,   4, 10, 15, 12, 10,
                     4,  2,  3,  5, 3,   3,  5,  3,  2,  4]
    @staticmethod
    def _vector_distance(v1, v2):
        """ Vector distance measure that measures the magnitude of the
        ratio of elements rather than the absolute value difference. """
        return math.sqrt(sum(math.log(a / b)**2 for a, b in zip(v1, v2)))

    _finger_weights = [15, 20, 25, 25,   25, 25, 20, 15]
    _sorted_key_weights = _key_weights[:]
    _sorted_key_weights.sort()
    _sorted_finger_weights = _finger_weights[:]
    _sorted_finger_weights.sort()

    def _score_heatmap(self):
        score = self._vector_distance(self.normalized_heatmap,
                                      self._key_weights)

        sorted_heatmap = self.normalized_heatmap[:]
        sorted_heatmap.sort()
        best_score = self._vector_distance(sorted_heatmap,
                                           self._sorted_key_weights)
        sorted_heatmap.reverse()
        worst_score = self._vector_distance(sorted_heatmap,
                                            self._sorted_key_weights)

        return (score - worst_score) / (best_score - worst_score)

    def _score_heatmap2(self):
        score = sum(map(operator.mul, self.heatmap, self._key_weights))

        sorted_heatmap = self.heatmap[:]
        sorted_heatmap.sort()
        best_score = sum(map(operator.mul,
                             sorted_heatmap, self._sorted_key_weights))
        sorted_heatmap.reverse()
        worst_score = sum(map(operator.mul,
                              sorted_heatmap, self._sorted_key_weights))

        return (score - worst_score) / (best_score - worst_score)

    @staticmethod
    def _normalize(heatmap, factor):
        return [h * factor for h in heatmap]

    @staticmethod
    def _finger_heat(h):
        f = [h[ 0]+h[10]+h[20],
             h[ 1]+h[11]+h[21],
             h[ 2]+h[12]+h[22],
             h[ 3]+h[ 4]+h[13]+h[14]+h[23]+h[24],
             h[ 5]+h[ 6]+h[15]+h[16]+h[25]+h[26],
             h[ 7]+h[17]+h[27],
             h[ 8]+h[18]+h[28],
             h[ 9]+h[19]+h[29]]
        return f

    def _score_finger_heat(self):
        score = self._vector_distance(self.finger_heatmap,
                                      self._finger_weights)

        sorted_heatmap = self.finger_heatmap[:]
        sorted_heatmap.sort()
        best_score = self._vector_distance(sorted_heatmap,
                                           self._sorted_finger_weights)
        sorted_heatmap.reverse()
        worst_score = self._vector_distance(sorted_heatmap,
                                            self._sorted_finger_weights)

        return (score - worst_score)**2 / (best_score - worst_score)**2

    def _score_finger_heat2(self):
        finger_heatmap = self._finger_heat(self.heatmap)

        score = sum(map(operator.mul, finder_heatmap, self._finger_weights))

        sorted_heatmap = finger_heatmap[:]
        sorted_heatmap.sort()
        best_score = sum(map(operator.mul,
                             sorted_heatmap, self._sorted_finger_weights))
        sorted_heatmap.reverse()
        worst_score = sum(map(operator.mul,
                              sorted_heatmap, self._sorted_finger_weights))

        return (score - worst_score) / (best_score - worst_score)

    def _heatmap_metric(self):
        #return (2.0 - (1.0 - key_score)**2 - (1.0 - finger_score)**2) / 2
        return (math.sqrt(self.heatmap_score) +
                math.sqrt(self.finger_score)) / 2
        #return (key_score + finger_score) / 2

    def _bad_bigrams_metric(self):
        bad_bigrams = self.bad_bigrams / self.strokes
        return 1.0 - bad_bigrams**(1/3)

    def _slow_bigrams_metric(self):
        slow_bigrams = self.slow_bigrams / self.strokes
        return 1.0 - math.sqrt(slow_bigrams)

    def _fast_bigrams_metric(self):
        fast_bigrams = self.fast_bigrams / self.strokes
        return math.sqrt(fast_bigrams)

    def _fast_trigram_metric(self):
        # Fast trigrams only move in one direction. So worst case is
        # two overlapping trigrams in four key strokes. Hence normalize
        # with self.strokes/2.
        fast_trigrams = self.fast_trigrams / (self.strokes/2)
        return math.sqrt(fast_trigrams)

    def eval_score(self, text, full=False):
        self.heatmap = self.calc_heatmap(text)
        self.strokes = sum(self.heatmap)
        self.normalized_heatmap = self._normalize(self.heatmap,
                sum(self._key_weights) / self.strokes)
        self.heatmap_score = self._score_heatmap()
        self.finger_heatmap = self._finger_heat(self.normalized_heatmap)
        self.finger_score = self._score_finger_heat()

        if full:
            self.bad_bigram_freq = {}
            self.fast_bigram_freq = {}
            self.slow_bigram_freq = {}
            self.fast_trigram_freq = {}
        else:
            self.bad_bigram_freq = None
            self.fast_bigram_freq = None
            self.slow_bigram_freq = None
            self.fast_trigram_freq = None
        self.bad_bigrams = self.calc_bad_bigrams(text,
                freq_map=self.bad_bigram_freq)
        #self.fast_bigrams = self.calc_fast_bigrams(text,
        #        freq_map=self.fast_bigram_freq)
        self.slow_bigrams = self.calc_slow_bigrams(text,
                freq_map=self.slow_bigram_freq)
        self.fast_trigrams = self.calc_fast_trigrams(text,
                freq_map=self.fast_trigram_freq)

        self.scores = (self._heatmap_metric(),
                       self._bad_bigrams_metric(),
                       self._slow_bigrams_metric(),
                       #self._fast_bigrams_metric(),
                       self._fast_trigram_metric())
        w = (1, 3, 1, 1)
        self.overall_score = sum((w[i] * self.scores[i] for i in range(len(self.scores)))) / sum(w)

        return self.overall_score

    def eval(self, text, debug = 0):
        self.eval_score(text, full=True)
        self.fast_bigrams = self.calc_fast_bigrams(text,
                freq_map=self.fast_bigram_freq)

        self.finger_travel = self.calc_finger_travel(text)
        self.adjusted_travel = self.calc_adjusted_travel(text)
        self.normalized_travel = self._normalize(self.finger_travel, 1000 / self.strokes)
        self.norm_adj_travel = self._normalize(self.adjusted_travel, 1000 / self.strokes)

        self.hand_runs = self.calc_hand_runs(text, debug)

    def print_layout_heatmap(self, file=sys.stdout):
        l = [a == b.lower() and '[ ' + b + ' ]' or '[' + a + ' ' + b + ']' for a, b in self.layout]
        h = self.normalized_heatmap
        f = self.finger_heatmap
        print(" %5.5s %5.5s %5.5s %5.5s %5.5s | %5.5s %5.5s %5.5s %5.5s %5.5s" % tuple(l[0:10]), file=file)
        print("%5.1f %5.1f %5.1f %5.1f %5.1f  |%5.1f %5.1f %5.1f %5.1f %5.1f" % tuple(h[0:10]), file=file)
        print(" %5.5s %5.5s %5.5s %5.5s %5.5s | %5.5s %5.5s %5.5s %5.5s %5.5s" % tuple(l[10:20]), file=file)
        print("%5.1f %5.1f %5.1f %5.1f %5.1f  |%5.1f %5.1f %5.1f %5.1f %5.1f" % tuple(h[10:20]), file=file)
        print(" %5.5s %5.5s %5.5s %5.5s %5.5s | %5.5s %5.5s %5.5s %5.5s %5.5s" % tuple(l[20:30]), file=file)
        print("%5.1f %5.1f %5.1f %5.1f %5.1f  |%5.1f %5.1f %5.1f %5.1f %5.1f" % tuple(h[20:30]), file=file)
        print("%5.1f %5.1f %5.1f %5.1f        |      %5.1f %5.1f %5.1f %5.1f" % tuple(f), file=file)

    def print_short_summary(self, file=sys.stdout):
        self.print_layout_heatmap(file=file)
        print("Heatmap score: %.4f (%.4f)" % (self.heatmap_score, self.scores[0]), file=file)
        print("Bad bigrams:   %6d (%.4f)" % (self.bad_bigrams, self.scores[1]), file=file)
        print("Slow bigrams:  %6d (%.4f)" % (self.slow_bigrams, self.scores[2]), file=file)
        #print("Fast bigrams:  %6d (%.4f)" % (self.fast_bigrams, self.scores[2]), file=file)
        print("Fast trigrams: %6d (%.4f)" % (self.fast_trigrams, self.scores[3]), file=file)
        print("Overall score: %.4f" % self.overall_score, file=file)

    def _mean_runs(self):
        mean = [0, 0]
        for hand in range(2):
            nom = 0
            denom = 0
            for length, num in self.hand_runs[hand].items():
                nom += length*num
                denom += num
            if denom:
                mean[hand] = nom / denom
        return (mean[0], mean[1])

    def _median_runs(self):
        median = [0, 0]
        for hand in range(2):
            num = 0
            for length, num in self.hand_runs[hand].items():
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

    def _max_runs(self):
        return (max(self.hand_runs[0].keys()), max(self.hand_runs[1].keys()))

    @staticmethod
    def _print_gram_freqs(items, file=sys.stdout):
        # Sort most frequent first
        items.sort(key=lambda item: item[1], reverse=True)
        for sym, freq in items:
            print("%s:%d" % (''.join(sym), freq), end=' ', file=file)
        print(file=file)

    def print_summary(self, file=sys.stdout):
        self.print_short_summary(file=file)
        print("Fast bigrams:  %6d" % self.fast_bigrams, file=file)
        print("Finger travel: %d: %s" % (sum(self.finger_travel), [int(a) for a in self.normalized_travel]), file=file)
        print("Adjusted travel: %d: %s" % (sum(self.adjusted_travel), [int(a) for a in self.norm_adj_travel]), file=file)
        print("Hand runs mean, max: %s, %s" % (repr(self._mean_runs()), repr(self._max_runs())), file=file)

        print("\nBad bigrams: ", end="", file=file)
        self._print_gram_freqs(list(self.bad_bigram_freq.items()), file=file)
        print("\nSlow bigrams: ", end="", file=file)
        self._print_gram_freqs(list(self.slow_bigram_freq.items()), file=file)
        print("\nFast bigrams: ", end="", file=file)
        self._print_gram_freqs(list(self.fast_bigram_freq.items()), file=file)
        print("\nFast trigrams: ", end="", file=file)
        self._print_gram_freqs(list(self.fast_trigram_freq.items()), file=file)

    def save_to_db(self):
        """
        Generate a unique file name from the layout and store
        its information. If the name already exits, the layout
        has already been discovered and nothing needs to be
        saved. In that case append a # character to indicate a
        count of how often a given layout has been found.

        The name is made up of all the alphabetic characters
        in the layout in order. Punctuations are replaced with
        _, since their exact position is less relevant.

        To eliminate redundancy due to symmetry, the layout is
        mirrored such that the letter A is always in the left
        hand.

        The file format is a python script with the layout
        formated as a list, and additional information in a
        multi-line string comment. Eventually this is going to
        be made a functioning script to evaluate a stored
        layout with other input texts.
        """
        if self.keymap['a'][2] != 0:
            layout = []
            for i in range(3):
                row = self.layout[i*10 : i*10 + 10]
                row.reverse()
                layout += row
        else:
            layout = self.layout[:]
        name = ''.join((k[0] if k[0].isalpha() else '_' for k in layout))
        path = '/'.join(('db', name))
        try:
            with open(path, 'x') as dbfile:
                print('"""', file=dbfile)
                self.print_summary(file=dbfile)
                print('"""', file=dbfile)
                print("\nlayout = [\n   ", end='', file=dbfile)
                for i in range(30):
                    print("%5s" % repr(self.layout[i]),
                          end = '\n]\n\n' if i == 29 else
                                ',\n   ' if i % 10 == 9 else
                                ',   ' if i % 10 == 4 else
                                ',',
                          file=dbfile)
                print("from eval_layout import eval_layout\neval_layout(layout)\n", file=dbfile)
                print("# The number of # on the following line counts discoveries of this layout.",
                        end='\n#', file=dbfile)
        except FileExistsError:
            with open(path, 'a') as dbfile:
                print("#", end='', file=dbfile)
