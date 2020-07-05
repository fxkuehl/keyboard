#!/usr/bin/python3

import sys
import math

class Buckets:
    def __init__(self, bucket_size):
        self.bucket_size = bucket_size
        self.buckets = {}

    def add(self, key, val):
        bucket = int(math.floor(key / self.bucket_size))
        try:
            self.buckets[bucket] += val
        except KeyError:
            self.buckets[bucket] = val

    def plot(self, format):
        min_x = min(self.buckets.keys())
        max_x = max(self.buckets.keys())
        y = max(self.buckets.values())
        while y > 0:
            if y % 5 == 0:
                print("    %3u+" % y, end='')
            else:
                print("       |", end='')
            x = min_x
            while x <= max_x:
                if x in self.buckets and self.buckets[x] >= y:
                    print("#", end='')
                else:
                    print(" ", end='')
                x += 1
            y -= 1
            print()
        print("        ", end='')
        x = min_x
        while x <= max_x:
            print("+---------", end='')
            x += 10
        print()
        print("    ", end='')
        x = min_x
        while x <= max_x:
            print(format % (x * self.bucket_size), end='')
            x += 10
        print()

heat_buckets = Buckets(0.002)
bad_buckets = Buckets(5)
fast_buckets = Buckets(150)
score_buckets = Buckets(0.0005)

for line in sys.stdin:
    try:
        num, heat, bad, fast, score = line.split()

        heat_buckets.add(float(heat), int(num))
        bad_buckets.add(float(bad), int(num))
        fast_buckets.add(float(fast), int(num))
        score_buckets.add(float(score), int(num))
    except ValueError:
        pass

print()
print("Overall score distributions")
print("===========================")
print()
score_buckets.plot("  %5.3f   ")

print()
print("Heatmap score distributions")
print("===========================")
print()
heat_buckets.plot("  %5.3f   ")

print()
print("Bad bigrams distributions")
print("=========================")
print()
bad_buckets.plot("  %5d   ")

print()
print("Fast bigrams distributions")
print("==========================")
print()
fast_buckets.plot("  %5d   ")
