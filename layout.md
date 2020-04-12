Searching for optimal keyboard layout

# Introduction

There are a few common keyboard layouts in use today. The most common one is QWERTY and derivatives. There have been a few attempts at optimizing keyboard layouts in the past for more speed, comfort or versatility. Those include Dvorak, Colemak and Neo layouts.

I have personally used QWERTZ (German version of QWERTY), QWERTY, Dvorak and Colemak. Learning a new layout is a time-consuming process. Whether using one keyboard layout over another leads to more speed or comfort is hard to judge objectively.

This study attempts to tackle the problem of the optimal keyboard layout by computer simulation and solving it as an optimization problem. The quality of the existing layouts can be quantified objectively using different criteria, and a potentially more optimal layout could be found by searching the space of all possible keyboard layouts for a global optimum.

# Assumptions and choices

Typical computer keyboards have between roughly 50 to 100 keys. Many of those keys are assigned to special functions or rarely used symbols. Many of those special keys are used very differently by different users, depending on whether they are writing text, computer programs, performing data entry, using CAD applications, gaming, etc. Therefore this study is going to focus on the central area of the keyboard containing the alphabetical keys and the most common punctuation characters. This should make it applicable to a wide range of keyboards, including minimalist ones.

Any user willing to adopt a radically different keyboard layout for purposes of efficiency or comfort is also likely to be willing to switch to a programmable, ergonomic or ortholinear keyboard. So some assumptions of typical QWERTY keyboards with staggered rows can be abandoned. Specifically the keys at the position of TAB, Caps-Lock, left shift keys could be mapped to actual characters. The shift key can alias a regular character key that behaves differently depending on whether it is tapped or held down as a modifier. Furthermore, ergonomic keyboards have more keys available to the thumbs to take over functions such as Enter, Tab, Backspace, etc. Therefore even on a minimalist keyboard, more keys within easy reach of the home row can be used for typing than would be available otherwise.

## Reduced keyboard layout

I am going to assume three rows of keys with 12 keys per row available for typing. A QWERTY layout can be represented in this reduced keyboard as follows:

       Q  W  E  R  T  Y  U  I  O  P
    -_ A  S  D  F  G  H  J  K  L  ;: '"
       Z  X  C  V  B  N  M  ,< .> /?

The `-_` key was moved from the number row because it is commonly used for punctuation and is hard to reach in its usual position. Less common punctuation keys were dropped from consideration in this study: `\[\{`, `\]\}`, `\`~`, `=+`, `\\|`. The numbers row is missing altogether. On a keyboard with a numbers row, it can be added back. On a smaller keyboard it would be reached on a separate layer. Either way, it is not considered for layout optimization in this study.

This leaves four keys unassigned in positions which are harder to reach for the pinky. They can be used for domain-specific punctuation or modifier keys. They will not be used in this optimization.

## Search space

With the keyboard layout assumed above, there are 32 key positions to be assigned to 32 keys. That means the total number of possible layouts is 32! = 2.631308369\*10<sup>35</sup>. That search space is too large for a brute-force search. A computer that could hypothetically evaluate one million layouts per second would take about 10<sup>22</sup> years, which is longer than the life time of the universe.

The optimization will need to use a heuristic or statistical approach, such as a genetic algorithm or simulated annealing.

# Quality function

## Criteria

### Speed

Typing text can be broken down into short sequences of key-presses, for example just two keys. Some of those sequences are faster to type than others. Factors that affect the speed are:

* Same or different hand
* Same or different finger
* Same or different row
* Keys in adjacent columns of further separated

The influence of these factors can be guessed or measured.

### Comfort

The goal for comfortable typing is to maximize use of the home row and the use of strong fingers. On the other hand, different fingers have different numbers of keys assigned to them in the reduced layout:

* Pinky: 4
* Ring finger: 3
* Middle finger: 3
* Index finger: 6

A comfortable layout should not over-stress one finger. Part of that is automatically handled by optimizing typing speed. Having many common characters on the same finger results in many words that use the same finger twice in a row, which is slow. However, I don't want to leave the proportion of key-strokes for each finger to chance. It should still be roughly balanced, with heavier weight on stronger fingers. Proposed ideal weights per finger:

* Pinky: 1
* Ring finger: 2
* Middle finger: 3
* Index finger: 3

The ring finger is relatively weak. But the pinky tends to get used more for special keys within its reach. Therefore it should get less typing work. Middle and index finger are about equally strong. But the index finger handles twice as many keys. Therefore it would likely handle less frequent characters.

Deviating from the home row should incur a penalty. Again, optimizing typing speed may favour the home row automatically, but a lot can be compensated with additional effort and discomfort. Therefore the algorithm should explicitly favour the home row. Proposed ideal weights per row:

* Top: 1
* Home: 3
* Bottom: 1

There may also be an argument for favouring one hand over the other. A right-handed person may want to favour the right hand. On the other hand, the right hand may have other jobs (e.g. operating a mouse or function keys), so one may want to reduce use of the strong hand for pure typing. Finally, an ambidextrous layout may be more widely acceptable by more users. I am leaning towards assuming an ambidextrous layout due to uncertainty about what's actually better, and to generate a layout that's more generally applicable.

Given a probability distribution of characters in a text, each character probability can be multiplied with its row and column weight using a given keyboard layout. An keyboard layout optimized for comfort would maximize the weighted sum.

## Determining parameters of the quality function

The quality function has many parameters. This section goes over those parameters and how they can be determined.

### Speed of typing short sequences

The possible speed of typing a short sequence of keys can be measured from a real typist on a real keyboard. Each short sequence of keys can be practised for a short time (less than a minute) and then measured repeatedly. The average of several measurements can be used, discarding statistical outliers. This could potentially be done by multiple individual typists on different keyboards. Measurements from each typist should be normalized before combining them with measurements from other typists.

The shortest possible sequence would consist of two keys. On the reduced keyboard layout there are 32\*32 = 1024 such sequences (pairs). That number can be reduced for practical purposes. Sequences that switch from one hand to the other probably don't vary much between each other assuming that the two hands act independently. The speed largely depends on how quickly a key can be reached, but doesn't depend on the key that was pressed by the other hand. Considering only a single hand, there are only 16\*16 = 256 sequences per hand. Assuming no injuries, both hands should be about equal with enough training, although slight variations are still likely. Thus the results from both hands could be mirrored, normalized and averaged to better represent an average user.

Sequences using alternate hands should still be measured, but a smaller sample could be measured and then generalized.

When measuring the speed of typing a pair, the keys typed before and after may affect the speed as the entire hand can move slightly over the keyboard as it types the longer sequence and the fingers are not bio-mechanically independent. Therefore ideally each pair should be measured in the middle of longer sequences of at least four keys. The number of sequences to measure quickly gets intractable without some simplifications. Multiple data-points could be obtained from three-key sequences (triplets):

1. First+second key at the start of a word
2. Second+third key at the end of a word
3. Variation of first+second key depending on the third
4. Variation of second+third key depending on the first

As a result of combining many measurements of different triplets, each pair would have an average speed and a number of variations depending on a leading or trailing key. An exhaustive set of triplets would consist of 4096 measurements per hand and even more, when including sequences that alternate between hands.

To reduce this number, leading and trailing keys are categorized, so that measurements are only needed for each category but not individual leading and trailing keys. The categories are the same for leading and trailing keys. For leading keys they are relative to the first key in the pair, for trailing keys relative to the second key in the pair:

* Different hand (use middle finger home row as representative)
* Same key
* Same finger, adjacent key (including diagonal, measure only one)
* Same finger, distant key (only applicable for top and bottom row keys, measure only one)
* Adjacent fingers, all keys (p: 3, r: 7, m: 9, i: 3)
* Non-adjacent finger, all rows (measure most distant finger and key)

Putting it all together, following algorithm is proposed for generating a reduced set of triplets to measure:

1. Generate all pairs for the left hand and right hand separately (total: 512 pairs)
2. Generate pairs for alternating hands, but not an exhaustive list:

    1. Each key on left hand + middle finger home row on right hand
    2. Middle finger home row on left hand + each key on right hand

    Middle finger home row on both hands would be generated twice, eliminate the duplicate. This results in 31 pairs using both hands.

3. Combine pairs by matching the second key of the first pair with the first key of the second pair.  Generate triplets according to the categories listed above. For each pair generate two triplets per category, one for the leading key and one for the trailing one. Eliminate any duplicates.

