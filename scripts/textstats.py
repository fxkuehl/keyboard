class TextStats:
    def _calc_symbol_freqs(self):
        self.symbol_freq = {}
        for c in self.text:
            if c in self.symbol_freq:
                self.symbol_freq[c] += 1
            else:
                self.symbol_freq[c] = 1

    @staticmethod
    def _is_valid_bigram(a, b):
        """ 0nly count bigrams with 2 unique letters, as only those can
        be optimiazed. Consider ' a letter, as it tends occur in common
        words, such as "don't". """
        return (a.isalpha() or a == "'") and \
               (b.isalpha() or b == "'") and a != b

    @staticmethod
    def _is_valid_trigram(a, b, c):
        """ 0nly count trigrams with 3 unique letters, as only those can
        be optimiazed. Consider ' a letter, as it tends occur in common
        words, such as "don't". """
        return (a.isalpha() or a == "'") and \
               (b.isalpha() or b == "'") and \
               (c.isalpha() or c == "'") and \
               a != b and b != c and c != a

    def _calc_bigrams(self):
        self.bigrams = {}
        prev = ' '
        for c in self.text.lower():
            if self._is_valid_bigram(prev, c):
                bigram = (prev, c)
                if bigram in self.bigrams:
                    self.bigrams[bigram] += 1
                else:
                    self.bigrams[bigram] = 1
            prev = c

    def _calc_trigrams(self):
        self.trigrams = {}
        prev2, prev1 = ' ', ' '
        for c in self.text.lower():
            if self._is_valid_trigram(prev2, prev1, c):
                trigram = (prev2, prev1, c)
                if trigram in self.trigrams:
                    self.trigrams[trigram] += 1
                else:
                    self.trigrams[trigram] = 1
            prev2, prev1 = prev1, c

    def __init__(self, text):
        self.text = text
        self._calc_symbol_freqs()
        self._calc_bigrams()
        self._calc_trigrams()
        #t = [(s[0]+s[1]+s[2], f) for s, f in self.trigrams.items() if "'" in s]
        #t.sort(key=lambda a: a[1])
        #print(t)
        #print(len(self.bigrams))
        #print(len(self.trigrams))
