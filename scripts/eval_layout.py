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

def eval_layout(layout):
    keymap = Keymap(layout)
    keymap.eval(TextStats(sys.stdin.read()))
    keymap.print_summary()
    if save_to_db:
        keymap.save_to_db()

save_to_db = False
for arg in sys.argv[1:]:
    if arg == "-h" or arg == "--help":
        print_help(0)
    elif arg == "-d" or arg == "--db":
        save_to_db = True
    else:
        print("Invalid option: '%s'" % arg)
        print_help(1)

