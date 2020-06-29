#!/usr/bin/python3

import sys
import re

missing_words = set()
with open(sys.argv[1]) as wordfile:
    words = frozenset( (s.lower() for s in wordfile.read().split()) )

    in_text = sys.stdin.read()
    in_words_sep = re.split(r"([^\w']+)", in_text)
    
    while in_words_sep:
        word = in_words_sep.pop(0).strip("'")
        sep = None
        if in_words_sep:
            sep = in_words_sep.pop(0)

        if word.lower() in words:
            sys.stdout.write(word)
        else:
            missing_words.add(word.lower())
        if sep:
            sys.stdout.write(sep)

    if len(sys.argv) >= 3:
        with open(sys.argv[2], 'w') as missingfile:
            for word in missing_words:
                missingfile.write(word + '\n')
