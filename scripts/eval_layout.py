#!/usr/bin/python3

import sys
from keymap import Keymap
from textstats import TextStats

def print_help(ret):
    print("Usage: %s [options ...]" % sys.argv[0])
    print()
    print("Options:")
    print("  -h | --help    Print this help")
    print("  -d | --db      Save layout to database")
    sys.exit(ret)

def eval_layout_with_text(layout, text):
    keymap = Keymap(layout)
    keymap.eval(text)
    keymap.print_summary()
    if save_to_db:
        keymap.save_to_db()

def eval_layout(layout):
    text = TextStats(sys.stdin.read())
    eval_layout_with_text(layout, text)

save_to_db = False
for arg in sys.argv[1:]:
    if arg == "-h" or arg == "--help":
        print_help(0)
    elif arg == "-d" or arg == "--db":
        save_to_db = True
    else:
        print("Invalid option: '%s'" % arg)
        print_help(1)

def main():
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
    layouts = {
        "QWERTY": layout_QWERTY,
        "Dvorak": layout_DVORAK,
        "PLUM": layout_PLUM,
        "Colemak": layout_COLEMAK,
        "Colemak-DH": layout_COLEMAKDH,
        "Workman": layout_WORKMAN,
    }

    text = TextStats(sys.stdin.read())
    for name, layout in layouts.items():
        print("*** Layout: %s ***" % name)
        eval_layout_with_text(layout, text)

if __name__ == "__main__":
    main()
