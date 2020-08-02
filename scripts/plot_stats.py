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

score_buckets = Buckets(0.0004)
heat_buckets = Buckets(0.00125)
finger_buckets = Buckets(0.004)
bad_buckets = Buckets(0.08)
slow_buckets = Buckets(2)
fasttri_buckets = Buckets(0.6)
fast_buckets = Buckets(2)
travel_buckets = Buckets(1)

for line in sys.stdin:
    try:
        #num, heat, bad, fast, slow, fasttri, score = line.split()
        num, score, heat, finger, bad, slow, fasttri, fast, travel = line.split()

        score_buckets.add(float(score), int(num))
        heat_buckets.add(float(heat), int(num))
        finger_buckets.add(float(finger), int(num))
        bad_buckets.add(float(bad), int(num))
        slow_buckets.add(float(slow), int(num))
        fasttri_buckets.add(float(fasttri), int(num))
        fast_buckets.add(float(fast), int(num))
        travel_buckets.add(float(travel), int(num))
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
print("Finger score distributions")
print("==========================")
print()
finger_buckets.plot("  %5.3f   ")

print()
print("Bad bigrams distributions")
print("=========================")
print()
bad_buckets.plot("  %5.2f   ")

print()
print("Slow bigrams distribution")
print("=========================")
print()
slow_buckets.plot("   %3d    ")

print()
print("Fast trigrams distribution")
print("==========================")
print()
fasttri_buckets.plot(" %5.1f    ")

print()
print("Fast bigrams distributions")
print("==========================")
print()
fast_buckets.plot("   %3d    ")

print()
print("Finger travel distributions")
print("===========================")
print()
travel_buckets.plot("   %3d    ")
