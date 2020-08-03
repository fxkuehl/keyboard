Searching for the optimal keyboard layout
=========================================

***Empirically quantifying and optimizing keyboard layouts***

**Author:** *Felix Kuehling*

# Introduction

Most keyboard layouts in use today are based on historical keyboard designs for mechanical typewriters. The typical staggered-row design is a result of lever arms having to pass each other between rows of a mechanical keyboard. The origin of the common QWERTY layout is a somewhat murky. It may be to avoid jamming of the typewriter mechanism or be a legacy from transcription of Morse code. [1] Either, way, those design constraints do not apply to modern computer keyboards, yet they have been carried over almost without being questioned.

A few attempts have been made to redesign computer keyboards for ergonomic considerations, both in terms of physical layout and the mapping of symbols to keys. On the physical side, ergonomic keyboards are often split designs with the two halves at an angle to put the wrists into a more neutral position. However, most of the more affordable or main-stream designs still carry over the row stagger. More radical designs either choose a regular matrix (ortholinear) layout or a column stagger that attempts to match the different lengths of the fingers. There are many designs that reduce the number of physical keys to the ones within easy reach without having to move the hands. On such keyboards, more functions and symbols are activated by switching layers. [2]

In terms of ergonomic keymaps, the oldest example I'm aware of is the Dvorak [3] layout, which was patented in 1936. More modern layouts for the English language include Colemak [4] and variations, Workman [5]. The Neo [6] layout is optimized for the German language.

I have personally used QWERTZ (German version of QWERTY), QWERTY, Dvorak and Colemak. Learning a new layout is a time-consuming process. Whether using one keyboard layout over another leads to more speed or comfort is hard to judge objectively for any individual.

This project attempts to approach the problem of the optimal keyboard layout algorithmically as an optimization problem. The quality of the existing layouts can be quantified objectively using different criteria. There are several online keyboard layout analyzers available [7,8] that can be used to analyze small numbers of keyboard layouts. A potentially more optimal layout could be found by automatically searching the entire space of all possible keyboard layouts for a global optimum.

The remainder of this document is divided into several sections.

**Assumptions and Limitations** defines the scope of this project, what parts of the keyboard layout are part of the attempted optimization, and a brief discussion of the size of the search space.

**Quality function** describes the design of the quality function, which quantifies for the search algorithm what makes a good keyboard layout. Then it reviews existing keyboard layouts with respect to the quality function and its metrics to provide context and a reference for the optimization.

**Optimization algorithm** describes the basic elements of the simulated annealing algorithm that was implemented, concluding with its performance and convergence to good solutions.

**Results** presents and discusses a selection of keyboard layouts found by the algorithm.

---

# Assumptions and limitations

Typical computer keyboards have between roughly 60 to 100 keys. Many of those keys are assigned to special functions or rarely used symbols. Many of those special keys are used very differently by different users, depending on whether they are writing text, computer programs, performing data entry, using CAD applications, gaming, etc. Therefore this project is going to focus on the central area of the keyboard containing the alphabetical keys and the most common punctuation characters. This should make it applicable to a wide range of keyboards, including minimalist ergonomic ones with 40 or fewer keys.

Any user willing to adopt a radically different keyboard layout for purposes of efficiency or comfort is also likely to be willing to switch to a programmable, ergonomic or ortholinear keyboard. So some assumptions of typical QWERTY keyboards with staggered rows may not be applicable. Specifically the position of Space, Shift, Caps-Lock, TAB, Enter and Backspace keys may be unusual. Furthermore, ergonomic keyboards have more keys available to the thumbs to take over some of those functions usually performed by the pinky fingers or require moving the hands away from the home position. Therefore all of those special keys are excluded from the analysis.

## Reduced keyboard layout

I am going to assume three rows of keys with 10 keys per row available for typing. A QWERTY layout can be represented in this reduced keyboard as follows:

        Q | W | E | R   T || Y   U | I | O | P
        A | S | D | F   G || H   J | K | L | ;:
        Z | X | C | V   B || N   M | ,<| .>| /?
          |   |   |       ||       |   |   |
     Pinky|Rng|Mid| Index || Index |Mid|Rng|Pinky
                          ||
          Left hand       ||      Right hand

Similarly, Dvorak would look as follows:

        '"| ,<| .>| P   Y || F   G | C | R | L
        A | O | E | U   I || D   H | T | N | S
        ;:| Q | J | K   X || B   M | W | V | Z
          |   |   |       ||       |   |   |
     Pinky|Rng|Mid| Index || Index |Mid|Rng|Pinky
                          ||
          Left hand       ||      Right hand

The set of symbols in the reduced layout is almost the same between the two layouts. The only difference is that QWERTY has the `/?` key, while Dvorak has the more frequently used `'"` key in the reduced key set. Therefore Dvorak is a better starting point for an English language keyboard. For other languages, the punctuation characters could be replaced with other symbols such as Umlauts or letters with accents.

Less common punctuation keys are not considered here, e.g.: `-_`, `[{`, `]}`, \`~, `=+`, `\|`. The numbers row is missing altogether. On a keyboard with a numbers row, it can be added back. On a smaller keyboard it would be reached on a separate layer. Either way, it is not considered for layout optimization in this project.

## Search space

With the keyboard layout assumed above, there are 30 key positions to be assigned to 30 keys. That means the total number of possible layouts is 30! = 2.652528598×10<sup>32</sup>. That search space is too large for a brute-force search. A computer that could hypothetically evaluate one million layouts per second would take about 8.4×10<sup>18</sup> years, or 8.4 quintillion years. Even a supercomputer with a million processors working at the same time would still take 8.4 trillion years.

The optimization will need to use a heuristic approach, such as a genetic algorithm or simulated annealing.

---

# Quality function

In order to quantify how good or bad a keyboard layout is, a quality function is needed. That function assigns a numerical value to the potential speed and comfort of typing a specific benchmark text. Computing the function for different keyboard layouts will give different results. Computing the function for different texts will also give different results. Texts written in the same language and using similar vocabulary should give similar results.

## Criteria

### Speed

Typing text can be broken down into short sequences of key strokes. A sequence of two keys is called a bigram. Longer sequences of n key strokes are called n-grams. Some of those sequences are faster to type than others. Factors that affect the speed are:

* Same or different hand
* Same or different finger
* Same or different row
* Keys in adjacent columns or further separated

The influence of these factors can be guessed or measured. Once these parameters are known, the potential typing speed of a given text can be estimated.

When measuring typing speed, there is a trade-off between speed and comfort. Key sequences that are hard to type can still be typed fast with additional effort. For anecdotal evidence, see typing speed records on websites such as [10 Fast Fingers](https://10fastfingers.com/) [9].

### Bio-mechanics

Some keyboard layout analyzers look at the distance that fingers travel during typing. However, one should also take into account, that fingers are not bio-mechanically independent. In particular motion of the ring finger is linked to movement of adjacent fingers.

In practice, the finger travel distance can be optimized indirectly by:

* Avoiding frequent bigrams on the same finger
* Mapping less frequent keys to the index fingers, which reach 6 keys each
* Mapping the most frequent keys on the home row

### Comfort

The goal for comfortable typing is to maximize use of the home row and the use of strong fingers. On the other hand, different fingers have different numbers of keys assigned to them in the reduced layout:

* Pinky: 3
* Ring finger: 3
* Middle finger: 3
* Index finger: 6

A comfortable layout should not over-stress one finger while under-utilizing another. This goal is partially correlated with typing speed and finger travel distance. Having many common characters on the same finger results in many bigrams using the same finger, which is slow.

Weighing the fingers equally can help reduce average finger travel distances. By contrast, very uneven weighing can result in the heavily weighted fingers travelling a lot because they need to handle multiple frequent keys and alternate between them. If the most frequent keys are more evenly spread out across the home row on all fingers, the most frequent keys will incur zero finger travel cost and only less frequent keys require fingers to move away from their home position.

There may also be an argument for favouring one hand over the other. A right-handed person may want to favour the right hand. On the other hand, the right hand may have other jobs (e.g. operating a mouse or a number-pad), so one may want to reduce the use of the strong hand for pure typing. An ambidextrous layout may be more widely acceptable by more users.

## Defining the quality function

The quality functions should express the quality of a keyboard layout using quantifiable metrics on a given input text. It should also be efficient to calculate. Ideally the cost of calculating the function should be O(1) with respect to the size of the input text.

The metrics chosen should account for the quality criteria outlined in the previous section. Some of the metrics may use parameters that can be changed or tuned in order to match real world usage, or measurements, or personal preferences.

Multiple independent metrics can be combined with different linear or non-linear weighting to express the relative importance of different metrics. In order to make the combination of different metrics more meaningful, all metrics should be scaled to the same numeric range before applying weighting functions. The choice made in my implementation uses floating point numbers in the range from 0 to 1, with 0 being the lowest possible quality, and 1 being the highest.

### Heatmap

The use of different keys for typing an input text can be visualized as a heatmap. A target or ideal heatmap can be defined, and the actual usage of the layout with the input text can be compared with that ideal. The result is a numerical score that expresses how closely the actual heatmap matches the ideal.

Weights can be used to express how common the use of a particular key should be. This can be expressed as a 30-element vector A. The actual frequency of key usage is another 30-element vector B. The distance d between these vectors can be calculated.

> d = sqrt((A<sub>1</sub> - B<sub>1</sub>)<sup>2</sup> + ...+ (A<sub>n</sub> - B<sub>n</sub>)<sup>2</sup>)

This distance measure has the property that the element with the biggest deviation will have the biggest effect on the overall distance value. However, a deviation from 0.1 to 1 and a deviation from 10.1 to 11 will be measured equally far. For key usage frequencies this is not a good measure because in the first case, a key is over-used or under-used by a factor 10. In the second case it is over-used or under-used by about 1.089. A measure that would express that "factor of deviation", which scales with the magnitude of the values would be better. I am proposing the following distance metric:

> d = sqrt((log A<sub>1</sub>/B<sub>1</sub>)<sup>2</sup> + ...+ (log A<sub>n</sub>/B<sub>n</sub>)<sup>2</sup>)

The logarithm measures the magnitude of the ration of A and B. Furthermore *log A/B = -log B/A*, i.e. the magnitude of both ratios is the same, only the sign differs. If either A or B are 0, this metric goes to infinity. As long as neither A nor B are 0, this metric provides a useful distance measure between key weights and a heatmap.

Similarly to individual keys, the finger weights can be evaluated. The weight of the finger is calculated by adding all the weights of the individual keys operated by that finger. The actual usage of the finger is calculated by adding the character frequencies of all characters typed by the finger.

The character probabilities in the input text can be calculated ahead of time. Then the distance metric has O(1) effort with respect to the size of the input text.

The distance should be normalized to the common value range 0 to 1. The lowest possible value should map to 0, the highest to 1. The lowest possible distance is obviously 0. However, given the character frequencies of an input text, a perfect 0 distance is likely impossible to achieve. The closest one can get is by assigning the most frequent characters to the highest weighted keys in order and calculating the resulting distance. Conversely the biggest possible distance can be calculated by assigning the most frequent characters to the lowest weighted keys. The actual score can be scaled linearly within this range such that a 0 distance maps to 1.0 and a maximal distance maps to 0.0.

For finger weights and heatmaps this calculation is a bit more difficult. The finger heatmap can get much closer to 0 distance by combining key frequencies differently. To simplify the calculation we can assume that it will get close enough to 0 that it's not worth calculating the actual best possible value for the actual character frequencies of a given input text. The biggest possible distance can be approximated with prior knowledge of the finger weights (see the weight parameters in the next section): Placing the most frequent keys on the pinky fingers, the next most frequent keys on the ring fingers, the next most frequent keys on the index fingers (which take 6 keys each) and the least frequent ones on the middle fingers.

The arithmetic mean of the normalized distance metric of key and finger usage and weights forms the heatmap metric. The finger and key metrics can also be weighed differently or scaled non-linearly, e.g. using a square root function. Using a square root changes the slope of the metric, with a smaller slope at higher values. That means, the sensitivity to heatmap changes is reduced for higher heatmap scores. This can allow more flexibility in trade-offs of "good enough" heatmap scores against other quality metrics.

After some experimentation I chose to weigh the finger and key heatmap distances equally but apply a square root function to the key metric.

The choice of key weights is a tuneable quality function parameter (or rather a vector of 30 parameters). To get ambidextrous keyboard layouts, those weights should be symmetric between the left and right hand, which effectively reduces the number of parameters from 30 to 15.

### Fast, slow and bad bigrams

The set of all potential bigrams (2-symbol sequences) can be determined from the input text, and the probability or frequency of each bigram can be stored in a lookup table.

From the keyboard layout a set of fast, slow, and bad bigrams can be generated. Fast bigrams are those, which are particularly comfortable or fast to type. Rolling motions from finger to finger without having to stretch uncomfortably should be favoured by the optimal keyboard layout. For example the sequence "AD" on the QWERTY layout would be a good bigram.

Bad bigrams are those, which use the same finger to type different letters. For example the very common bigram "ED" is a bad bigram in the QWERTY layout.

Any bigram that uses the same hand, but is neither fast nor bad, increases the number of consecutive keys one hand would have to type on average before alternating hands, without much benefit. This can lead to fatigue and to slowing down the flow of typing. Therefore I call these "slow bigrams". For example the Dvorak layout is heavily optimized for alternating hands between keystrokes. So Dvorak has very few slow bigrams but also very few fast bigrams.

A good keyboard layout would balance fast and slow bigrams, trying to maximize fast bigrams while minimizing slow bigrams as much as possible.

From the set of fast, bad and slow bigrams of the keyboard layout and the bigram frequencies of the input text, a count of fast, bad, and slow bigrams can be calculated. These counts can be scaled by the total number of keystrokes to give a range from 0 to 1. We want the number of bad bigrams to be very small. So the quality function should be more sensitive in the small value range. This can be achieved with square root or 3rd root functions. For very small values this function has a very steep slope. That means the quality function will be very sensitive to small changes when the number of bigrams is small. For larger values the slope becomes more shallow, thus the sensitivity decreases.

Calculating the frequency of bigrams using this method is O(1) with respect to the size of the input text. The number of bigrams in the lookup table does depend on the input text; however, a good hash table implementation for the lookup should also be O(1).

The set of fast bigrams is a choice of parameters of the quality function. The set of bad bigrams is objectively defined as all bigrams using the same finger to type different symbols. The set of slow bigrams is objectively defined as the set of all bigrams using the same hand minus the bad and fast bigram sets. Thus the set of fast bigrams is the only tuneable parameter of this metric.

### Fast 3-grams

Taking this one step further, one can also consider 3-grams and 4-grams that can be typed fast, with one rolling motion of the fingers on the same hand. Useful 4-grams would be very rare and are not considered, here. However, fast 3-grams are worth optimizing for. For example "oin" as in "ointment" and "ast" as in "last" would be considered fast 3-grams in the Colemak layout.

Algorithmically, fast 3-grams can be derived from two fast bigrams travelling in the same direction, where the first one's second key is the same as the second one's first key. For example "oin" in Colemak is composed of the two fast bigrams "oi" and "in".

The frequencies of 3-grams in the input text can be calculated ahead of time and stored in a lookup table. Then the frequncy of fast 3-grams in a given keyboard layout can be calculated in the same way as the bigram frequencies in O(1) with respect to the length of the input text by adding up frequencies of fast 3-grams of the keyboard layout found in the lookup table.

Again, they can be scaled to a value range from 0 to 1 by dividing by the total number of keystrokes. However, the biggest possible number of 3-grams in a degenerate input text is only half the total number of key strokes, because with four fingers in each hand only two overlapping 3-grams can be typed before having to start a new one. E.g. in Colemak, the text "arstarst..." repeating would be counted as overlapping "ars" and "rst" 3-grams, with the total number being two 3-grams for every four key-strokes. Thus the scaling factor should be only half the number of keystrokes.

If fast 3-grams are automatically generated from fast bigrams, this metric has no tuneable parameters.

### Other metrics

Other metrics have been considered and even implemented. However, they are less computationally efficient and are therefore not used in the optimization. Most notably, the finger travel distance can only be calculated by actually simulating every key stroke, which is O(n) with respect to the length of the input text.

In practice, it is observed that the finger travel distance achieved with the heatmap and bigram-based metrics is reasonable and within the same range as existing ergonomic layouts. Furthermore, the travel distances don't differ by a huge amount between good and bad layouts. By contract, the bigram metrics can differ by more than one order of magnitude.

## Determining parameters of the quality function

### Weights

The following weights were used:

         1 |  8 |  9 |  4    1  ||  1    4 |  9 |  8 |  1
        10 | 15 | 18 | 12    3  ||  3   12 | 18 | 15 | 10
         4 |  2 |  3 |  8    2  ||  2    8 |  3 |  2 |  4
    =======|====|====|==========||=========|====|====|=======
        15 | 25 | 30 | 30       ||      30 | 30 | 25 | 15
    =======|====|====|==========||=========|====|====|=======
     Pinky |Ring| Mid| Index    ||   Index |Mid |Ring| Pinky

The strong fingers are weighted more heavily. Since the index finger reaches more keys, its individual key weights tend to be smaller. The inner column that requires the index fingers to move horizontally is least heavily weighted since that is considered to be a factor in repetitive strain injuries by some. [5]

Keys that require more of a stretch are weighted lower. The longer middle and ring fingers can stretch up relatively easily, whereas the index and pinky fingers are typically shorter and prefer to curl to reach the bottom row rather than stretching up to the top row.

Aggressive column stagger on some ergonomic keyboards can compensate for some of the differences in finger length and their different ability to stretch up or down. Thus the weights may have to be adjusted for such keyboards.

### Fast bigrams

Which bigrams are easy to type may be somewhat subjective. This is the set chosen in my implementation expressed in terms of the left hand of the QWERTY layout. They are separated into two sets, left-to-right and right-to-left in order to facilitate automatic generation of fast 3-grams:

#### Left-to-right
>WE, WF,<br>
>EF,<br>
>AE, AW, AS, AD, AF, AV,<br>
>SD, SF, SV,<br>
>DF, DV,<br>
>ZS, ZD, ZF, ZV,

#### Right-to-left
>FW, FE, FA, FS, FD, FZ,<br>
>VA, VS, VD, VZ,<br>
>EW, EA,<br>
>DS, DA, DZ,<br>
>WA,<br>
>SA, SZ

These are 36 fast bigrams for the left hand. When mirrored for the right hand this results in a total of 72 fast bigrams.

### Auto-generated bigrams and 3-grams

Bad bigrams, slow bigrams, and fast 3-grams are automatically generated by the program:

>bad bigrams: 96<br>
>slow bigrams: 252<br>
>fast 3-grams: 64

Only bad bigrams and slow bigrams are calculated in the quality function. Since the set of slow bigrams excludes fast bigrams, it is an indirect measure of fast bigrams. The same could be said for bad bigrams, which are also excluded from the set of slow bigrams. However, bad bigrams use a different non-linear scaling to optimize for very small values.

Thus the total number of bigrams and 3-grams that need to be looked up to evaluate the quality function of one keyboard layout is 96 + 252 + 64 = 412.

### Input text

The input text used to evaluate the quality function can also be understood as a parameter. It determines the language and vocabulary that the keyboard layout gets optimized for.

From early experience it appears that the size and diversity of the input text is important for making a keyboard layout that generalizes to most texts. For example initial experiments using a chapter from the Junglebook as input gave a skewed perception of common bigrams that did not generalize to other texts. For example the bigram "ow" is quite common in this text from the name "Mowgli", but it is not common in the English language in general.

Another reverse example, running experiments with two texts found very good solutions for those texts, but they didn't generalize well for other texts. It was found that the initial two texts didn't represent the "je" bigram well. A resulting keyboard layout applied to another text that included the word "project" many times performed poorly because it had "j" and "e" on the same finger.

These problems with input texts can be addressed in two different ways:

* Concatenating many diverse texts
* Preprocessing texts to remove unusual names or typos

Both approaches are being applied in the experiments below. Preprocessing uses a word list to filter all words in the text. Rejected words are output into a new "missing words" list that can be manually vetted. Any real words can be added to the canonical word list before rerunning the preprocessing step. Typos and unusual names can be left out.

The texts used in these experiments were copied from [8] and then preprocessed against a growing canonical word list. The following four texts were used from that source:

1. Alice in Wonderland, Chapter 1
2. Jungle Book
3. Academic - Contractor's Performance in Construction
4. Academic - Binary Logistic Analysis

## Review of existing keyboard layouts

This section applies the quality function and its metrics to existing keyboard layouts. The scores and discussion of the results provide context and a reference for the solutions found by the optimization algorithm discussed in the next section.

Each keyboard layout is shown with key and finger weights normalized, to match the weights used in the heatmap metric of the quality function.

The metrics are presented as follows. All bigram and 3-gram counts as well as finger travel distances are given per 1000 keystrokes or 1 kilo-keystroke (kKS):

| Metric        | Value       | Details |
| ------------- | ----------- | :------ |
| Overall score | Score of the quality function | |
| Heatmap       | 0 to 1 key metric | 0 to 1 finger metric |
| Bad bigrams   | Total/kKS   | Count/kKS for each bigram |
| Slow bigrams  | Total/kKS   |         |
| Fast 3-grams  | Total/kKS   | Count/kKS for each 3-gram |
| Fast bigrams  | Total/kKS   | Count/kKS for each bigram |
| Finger travel | Total/kKS in units of the key size | Per-finger travel/kKS |
| Run length    | Avg # consecutive keystrokes: Left hand | Right hand |

Fast bigrams, finger travel and run length are not explicitly included in the quality function. They are shown here for reference and comparison with other layouts. Finger travel is indirectly affected by the heatmap. Run length and fast bigrams are implicitly optimized by the definition of slow bigrams, which penalize non-fast bigrams in the same hand.

### QWERTY

    [ Q ]  [ W ]  [ E ]  [ R ]  [ T ]  |  [ Y ]  [ U ]  [ I ]  [ O ]  [ P ]
     0.4    3.2   23.5   12.1   18.3   |   3.0    5.4   13.8   15.4    4.5
    [ A ]  [ S ]  [ D ]  [ F ]  [ G ]  |  [ H ]  [ J ]  [ K ]  [ L ]  [; :]
    14.8   12.0    7.0    5.0    3.8   |   9.2    0.7    1.2    8.0    0.4
    [ Z ]  [ X ]  [ C ]  [ V ]  [ B ]  |  [ N ]  [ M ]  [, <]  [. >]  [/ ?]
     0.1    0.2    8.0    2.1    2.6   |  14.3    4.6    3.0    3.4    0.2
    15.3 + 15.4 + 38.5 + 43.8 = 113.0  |  87.0 = 37.1 + 18.0 + 26.8 +  5.1

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.5011 |         |
| Heatmap       | 0.4986 |  0.7159 |
| Bad bigrams   |  59.14 | ed:8.77 ec:6.55 de:6.23 ce:4.80 tr:4.71 ol:4.50 lo:4.00 un:2.88 rt:1.82 rf:1.45 hn:1.41 ft:1.34 fr:1.19 gr:1.06 ki:0.86 um:0.84 hu:0.76 mu:0.69 br:0.59 ju:0.57 rg:0.52 my:0.51 ny:0.46 ik:0.34 rv:0.32 ws:0.31 nm:0.29 za:0.25 nu:0.23 hy:0.19 aq:0.16 sw:0.11 gt:0.09 bt:0.08 az:0.06 rb:0.04 nh:0.04 ym:0.03 uy:0.03 hm:0.02 vg:0.01 yn:0.01 uj:0.01 |
| Slow bigrams  | 241.42 |         |
| Fast 3-grams  |   0.27 | adv:0.11 fea:0.09 few:0.03 awf:0.01 fwa:0.01 ewa:0.01 |
| Fast bigrams  |  40.32 | io:5.95 as:5.13 ea:4.11 we:2.92 fa:2.51 oj:2.34 wa:2.33 fe:2.05 af:1.96 sa:1.90 ad:1.79 va:1.41 av:1.32 ef:1.10 ds:0.67 ew:0.55 aw:0.54 da:0.49 jo:0.31 oi:0.29 sf:0.22 lk:0.14 dv:0.11 kl:0.08 lm:0.06 wf:0.01 df:0.01 fw:0.01 fs:0.01 km:0.01 |
| Finger travel | 770.05 | 4.96 25.96 162.00 223.23 : 204.99 55.41 86.61 6.89 |
| Run length    |   1.68 | 1.48    |

The heatmap score for QWERTY is quite bad. It uses the left hand more heavily than the right hand, and some of the most frequently used keys are away from the home row. There are more bad (same-finger) bigrams than fast bigrams in this layout. The index fingers have to travel a lot and so does the left middle finger.

### Dvorak

    [' "]  [, <]  [. >]  [ P ]  [ Y ]  |  [ F ]  [ G ]  [ C ]  [ R ]  [ L ]
     1.0    3.0    3.4    4.5    3.0   |   5.0    3.7    7.9   12.0    8.0
    [ A ]  [ O ]  [ E ]  [ U ]  [ I ]  |  [ D ]  [ H ]  [ T ]  [ N ]  [ S ]
    14.7   15.3   23.5    5.3   13.7   |   7.0    9.1   18.3   14.2   11.9
    [; :]  [ Q ]  [ J ]  [ K ]  [ X ]  |  [ B ]  [ M ]  [ W ]  [ V ]  [ Z ]
     0.4    0.4    0.7    1.2    0.2   |   2.6    4.5    3.2    2.1    0.1
    16.1 + 18.7 + 27.5 + 28.0 =  90.3  | 109.7 = 32.0 + 29.4 + 28.3 + 20.0

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.6160 |         |
| Heatmap       | 0.7805 | 0.8732  |
| Bad bigrams   |  24.63 | ct:9.39 je:2.38 gh:1.72 rn:1.20 up:1.01 pi:0.91 ki:0.86 ip:0.81 ui:0.80 ls:0.72 tw:0.63 pu:0.46 mb:0.44 ik:0.34 yi:0.33 xp:0.32 rv:0.32 nv:0.32 dg:0.29 yp:0.28 sl:0.21 tc:0.16 xi:0.15 iu:0.11 py:0.07 ix:0.07 uk:0.04 hd:0.04 uy:0.03 gm:0.03 dm:0.03 hm:0.02 'a:0.01 a':0.01 oq:0.01 ej:0.01 kp:0.01 ky:0.01 ku:0.01 gd:0.01 df:0.01 db:0.01 hf:0.01 hb:0.01 mf:0.01 wt:0.01 nr:0.01 |
| Slow bigrams  |  95.81 |         |
| Fast 3-grams  |   0.66 | rch:0.35 sch:0.18 nth:0.08 uea:0.02 stm:0.01 ntm:0.01 hts:0.01 |
| Fast bigrams  |  85.82 | th:24.22 nt:9.10 st:8.08 ou:5.25 rs:4.56 ea:4.09 ch:3.78 ts:3.20 sh:3.17 ns:3.16 cr:2.16 ke:1.96 ue:1.41 hn:1.41 ua:1.31 ak:1.06 ht:0.99 sc:0.97 au:0.89 sm:0.81 rc:0.71 ok:0.63 eo:0.49 hr:0.39 ms:0.37 cs:0.33 oa:0.31 nm:0.29 oe:0.22 ka:0.10 sn:0.09 tm:0.08 eu:0.07 nh:0.04 rh:0.03 tn:0.03 uo:0.02 ek:0.01 ko:0.01 sr:0.01 hs:0.01 |
| Finger travel | 584.98 | 11.45 27.76 30.11 115.99 : 168.99 90.34 93.50 46.83 |
| Run length    |   1.23 | 1.39    |

The heatmap and bigram scores are much better than QWERTY. Also finger travel is much reduced. Only the right index finger still travels much more than other fingers.

Dvorak is optimized for alternating hands between keystrokes. This is reflected by the short average run length and the much lower score of slow bigrams.

Dvorak more than doubles the number of fast 3-grams, though that number is still very small in absolute terms.

### Colemak

    [ Q ]  [ W ]  [ F ]  [ P ]  [ G ]  |  [ J ]  [ L ]  [ U ]  [ Y ]  [; :]
     0.4    3.2    5.0    4.5    3.8   |   0.7    8.0    5.4    3.0    0.4
    [ A ]  [ R ]  [ S ]  [ T ]  [ D ]  |  [ H ]  [ N ]  [ E ]  [ I ]  [ O ]
    14.8   12.1   12.0   18.3    7.0   |   9.2   14.3   23.5   13.8   15.4
    [ Z ]  [ X ]  [ C ]  [ V ]  [ B ]  |  [ K ]  [ M ]  [, <]  [. >]  [/ ?]
     0.1    0.2    8.0    2.1    2.6   |   1.2    4.6    3.0    3.4    0.2
    15.3 + 15.5 + 24.9 + 38.2 =  93.9  | 106.1 = 38.0 + 31.9 + 20.3 + 16.0

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.6668 |         |
| Heatmap       | 0.9163 | 0.8363  |
| Bad bigrams   |   8.48 | hn:1.41 ue:1.41 sc:0.97 kn:0.48 pt:0.47 nk:0.46 cs:0.33 nl:0.33 yi:0.33 dg:0.29 nm:0.29 za:0.25 sf:0.22 aq:0.16 lk:0.14 dv:0.11 rw:0.10 gt:0.09 bt:0.08 kl:0.08 eu:0.07 az:0.06 lm:0.06 nh:0.04 wr:0.03 tp:0.03 pb:0.02 td:0.02 ln:0.02 hm:0.02 fs:0.01 pg:0.01 pd:0.01 gd:0.01 dp:0.01 db:0.01 vg:0.01 kh:0.01 km:0.01 |
| Slow bigrams  | 131.10 |         |
| Fast 3-grams  |   6.24 | tra:1.76 aft:1.07 ien:0.88 oun:0.81 art:0.60 ars:0.33 ast:0.31 rst:0.17 oin:0.13 nio:0.06 nyo:0.03 arv:0.02 nei:0.02 awf:0.01 fwa:0.01 neo:0.01 meo:0.01 |
| Fast bigrams  | 161.52 | in:16.98 on:14.56 en:11.58 at:11.34 st:8.11 me:6.85 io:5.95 ar:5.73 ou:5.27 as:5.13 ra:5.12 tr:4.71 rs:4.58 no:4.54 ne:4.29 ta:3.77 ts:3.22 om:3.21 im:2.91 un:2.88 ie:2.80 em:2.58 fa:2.51 ni:2.47 wa:2.33 mo:2.14 af:1.96 sa:1.90 rt:1.82 va:1.41 mi:1.39 ft:1.34 av:1.32 ei:0.75 tw:0.64 yo:0.64 aw:0.54 eo:0.49 ny:0.46 rv:0.32 oi:0.29 oe:0.23 nu:0.23 oy:0.16 uy:0.03 uo:0.02 wf:0.01 wt:0.01 fw:0.01 sr:0.01 yn:0.01 |
| Finger travel | 590.53 | 4.96 26.31 96.10 168.65 : 167.12 71.69 49.86 5.86 |
| Run length    |   1.38 | 1.62    |

Colemak brings a further improvement in the heatmap score, although the per-finger heatmap is slightly worse. The index and middle fingers are weighted most heavily. On top of the improvements in Dvorak, Colemak brings another big improvement of bad bigrams by factor 3 and fast bigrams by factor 2.

Colemak has more slow bigrams than Dvorak, along with a longer average run length. Total finger travel is about the same as in Dvorak, but more evenly distributed to both hands. Both index fingers still travel a lot.

Colemak has nearly 10 times as many fast 3-grams as Dvorak and more than 20 times as many as QWERTY.

### Colemak-DHm

    [ Q ]  [ W ]  [ F ]  [ P ]  [ B ]  |  [ J ]  [ L ]  [ U ]  [ Y ]  [; :]
     0.4    3.2    5.0    4.5    2.6   |   0.7    8.0    5.4    3.0    0.4
    [ A ]  [ R ]  [ S ]  [ T ]  [ G ]  |  [ M ]  [ N ]  [ E ]  [ I ]  [ O ]
    14.8   12.1   12.0   18.3    3.8   |   4.6   14.3   23.5   13.8   15.4
    [ Z ]  [ X ]  [ C ]  [ D ]  [ V ]  |  [ K ]  [ H ]  [, <]  [. >]  [/ ?]
     0.1    0.2    8.0    7.0    2.1   |   1.2    9.2    3.0    3.4    0.2
    15.3 + 15.5 + 24.9 + 38.2 =  93.9  | 106.1 = 38.0 + 31.9 + 20.3 + 16.0

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.6736 |         |
| Heatmap       | 0.9552 | 0.8363  |
| Bad bigrams   |   8.48 | hn:1.41 ue:1.41 sc:0.97 kn:0.48 pt:0.47 nk:0.46 cs:0.33 nl:0.33 yi:0.33 dg:0.29 nm:0.29 za:0.25 sf:0.22 aq:0.16 lk:0.14 dv:0.11 rw:0.10 gt:0.09 bt:0.08 kl:0.08 eu:0.07 az:0.06 lm:0.06 nh:0.04 wr:0.03 tp:0.03 pb:0.02 td:0.02 ln:0.02 hm:0.02 fs:0.01 pg:0.01 pd:0.01 gd:0.01 dp:0.01 db:0.01 vg:0.01 kh:0.01 km:0.01 |
| Slow bigrams  | 116.51 |         |
| Fast 3-grams  |   7.05 | tra:1.76 aft:1.07 ien:0.88 oun:0.81 art:0.60 hei:0.44 ard:0.35 ars:0.33 ast:0.31 rst:0.17 oin:0.13 nio:0.06 dra:0.03 nyo:0.03 nei:0.02 heo:0.02 awf:0.01 fwa:0.01 neo:0.01 |
| Fast bigrams  | 176.11 | he:22.25 in:16.98 on:14.56 en:11.58 at:11.34 st:8.11 io:5.95 ar:5.73 hi:5.71 ou:5.27 as:5.13 ra:5.12 tr:4.71 rs:4.58 no:4.54 ne:4.29 ho:3.82 ta:3.77 ts:3.22 un:2.88 ie:2.80 fa:2.51 ni:2.47 wa:2.33 af:1.96 sa:1.90 rt:1.82 ad:1.79 ft:1.34 rd:0.81 ei:0.75 ds:0.67 eh:0.66 tw:0.64 yo:0.64 aw:0.54 da:0.49 eo:0.49 ny:0.46 dr:0.39 oi:0.29 oe:0.23 nu:0.23 oy:0.16 oh:0.08 ih:0.06 uy:0.03 uo:0.02 wf:0.01 wt:0.01 fw:0.01 sr:0.01 yn:0.01 |
| Finger travel | 600.01 | 4.96 26.31 96.10 170.85 : 174.40 71.69 49.86 5.86 |
| Run length    |   1.38 | 1.62    |

This is a minor modification of Colemak that affects only the placement of keys for the index fingers, making the common keys "D" and "H" more comfortable to reach [12] without lateral motion. This results in a small improvement of the key heatmap score and enables a few more fast bigrams and 3-grams than plain Colemak.

Out of all existing layouts considered here, this is the one with the highest overall score, followed closely by plain Colemak.

### Workman

    [ Q ]  [ D ]  [ R ]  [ W ]  [ B ]  |  [ J ]  [ F ]  [ U ]  [ P ]  [; :]
     0.4    7.0   12.1    3.2    2.6   |   0.7    5.0    5.4    4.5    0.4
    [ A ]  [ S ]  [ H ]  [ T ]  [ G ]  |  [ Y ]  [ N ]  [ E ]  [ O ]  [ I ]
    14.8   12.0    9.2   18.3    3.8   |   3.0   14.3   23.5   15.4   13.8
    [ Z ]  [ X ]  [ M ]  [ C ]  [ V ]  |  [ K ]  [ L ]  [, <]  [. >]  [/ ?]
     0.1    0.2    4.6    8.0    2.1   |   1.2    8.0    3.0    3.4    0.2
    15.3 + 19.2 + 25.8 + 37.9 =  98.1  | 101.9 = 32.3 + 31.9 + 23.2 + 14.4

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.6470 |         |
| Heatmap       | 0.9742 | 0.8913  |
| Bad bigrams   |  27.61 | ct:9.42 ly:2.78 po:2.78 rm:2.62 op:1.58 ue:1.41 lf:1.06 ds:0.67 tw:0.64 nf:0.62 fl:0.55 kn:0.48 ny:0.46 nk:0.46 hr:0.39 nl:0.33 za:0.25 aq:0.16 tc:0.16 lk:0.14 fy:0.10 gt:0.09 bt:0.08 kl:0.08 eu:0.07 az:0.06 rh:0.03 bc:0.03 hm:0.02 ln:0.02 wb:0.01 wt:0.01 vg:0.01 yn:0.01 ky:0.01 |
| Slow bigrams  |  83.96 |         |
| Fast 3-grams  |  12.73 | ion:5.63 tha:2.83 tra:1.76 ien:0.88 art:0.60 cha:0.40 ast:0.31 ash:0.10 upi:0.06 noi:0.03 rda:0.02 iol:0.02 iel:0.02 nei:0.02 adr:0.01 ths:0.01 pun:0.01 neo:0.01 |
| Fast bigrams  | 204.62 | th:24.31 in:16.98 on:14.56 en:11.58 at:11.34 st:8.11 ha:6.56 le:6.54 io:5.95 ar:5.73 ac:5.34 li:5.17 as:5.13 ra:5.12 tr:4.71 el:4.57 no:4.54 ol:4.50 ca:4.38 ne:4.29 lo:4.00 ch:3.79 ta:3.77 il:3.42 ts:3.22 sh:3.19 un:2.88 ie:2.80 ni:2.47 sa:1.90 rt:1.82 ad:1.79 up:1.01 ht:0.99 sc:0.97 pi:0.91 rd:0.81 ip:0.81 ui:0.80 ei:0.75 da:0.49 eo:0.49 pu:0.46 dr:0.39 cs:0.33 oi:0.29 oe:0.23 nu:0.23 iu:0.11 np:0.07 td:0.02 ah:0.01 hs:0.01 |
| Finger travel | 600.21 | 4.96 47.93 100.50 169.20 : 138.16 71.69 61.82 5.96 |
| Run length    |   1.49 | 1.58    |

The Workman layout was designed to minimize lateral movement in order to minimize the risk of repetitive strain injury. It is a more significant departure from Colemak than Colemak-DHm. It succeeds in achieving better heatmap scores and also has more fast bigrams and 3-grams as well as fewer slow bigrams than Colemak variants. However, its overall score is lower due to a 3x increase in same-finger bigrams. The frequency of the 'ct' bigram alone is higher than the entire same-finger bigram number on Colemak.

Notwithstanding the same-finger bigram score, out of all existing layouts considered here, Workman comes closest to the layouts found by the optimization algorithm discussed in the "Results" section.

### PLUM

    [ P ]  [ L ]  [ U ]  [ M ]  [; :]  |  [' "]  [ C ]  [ F ]  [ G ]  [ Q ]
     4.5    8.0    5.3    4.5    0.4   |   1.0    7.9    5.0    3.7    0.4
    [ R ]  [ E ]  [ A ]  [ D ]  [ O ]  |  [ N ]  [ T ]  [ H ]  [ I ]  [ S ]
    12.0   23.5   14.7    7.0   15.3   |  14.2   18.3    9.1   13.7   11.9
    [ K ]  [ J ]  [ V ]  [ B ]  [, <]  |  [. >]  [ W ]  [ X ]  [ Y ]  [ Z ]
     1.2    0.7    2.1    2.6    3.0   |   3.4    3.2    0.2    3.0    0.1
    17.7 + 32.1 + 22.1 + 32.8 = 104.7  |  95.3 = 48.0 + 14.4 + 20.5 + 12.4

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.5526 |         |
| Heatmap       | 0.8488 | 0.7434  |
| Bad bigrams   |  65.44 | ct:9.39 nt:9.10 le:6.51 pr:5.55 el:4.55 nc:4.04 om:3.19 je:2.38 ig:2.36 mo:2.13 do:1.85 od:1.84 va:1.41 av:1.32 ua:1.31 gy:1.15 gi:1.07 wn:1.01 bo:0.92 au:0.89 tw:0.63 rk:0.57 ob:0.47 mb:0.44 yi:0.33 n':0.31 tc:0.16 rp:0.15 t':0.15 sq:0.07 't:0.05 dm:0.03 tn:0.03 nw:0.02 kp:0.01 ej:0.01 db:0.01 'c:0.01 wt:0.01 hf:0.01 |
| Slow bigrams  | 160.37 |         |
| Fast 3-grams  |  10.70 | his:2.12 thi:1.99 der:1.48 red:0.84 rea:0.74 whi:0.63 ked:0.53 ead:0.46 tis:0.29 ber:0.27 sit:0.24 rad:0.17 dul:0.14 lud:0.13 dar:0.13 wis:0.13 rab:0.11 rld:0.09 bar:0.07 dur:0.06 rud:0.01 reb:0.01 eab:0.01 kab:0.01 tiz:0.01 ths:0.01 |
| Fast bigrams  | 169.72 | th:24.22 er:15.98 re:12.64 ti:10.74 ed:8.74 st:8.08 it:7.86 is:7.79 de:6.20 ar:5.70 hi:5.68 ra:5.10 si:4.11 ea:4.09 be:3.22 ts:3.20 sh:3.17 ur:2.78 wi:2.48 wh:2.47 ld:2.23 ru:2.11 ul:2.11 du:2.02 ab:1.98 ke:1.96 ad:1.79 ft:1.34 ba:1.24 ak:1.06 ht:0.99 ud:0.93 lu:0.89 rd:0.81 br:0.59 iz:0.51 da:0.49 dr:0.39 gs:0.33 ws:0.31 rl:0.26 sf:0.21 dl:0.17 zi:0.15 eb:0.11 sw:0.11 ka:0.10 gt:0.09 ih:0.06 rb:0.04 lr:0.01 ek:0.01 sg:0.01 hw:0.01 fs:0.01 hs:0.01 |
| Finger travel | 629.01 | 46.15 66.68 60.17 144.20 : 214.97 32.37 59.75 4.74 |
| Run length    |   1.87 | 1.62    |

The PLUM keyboard[13] was an attempt to market a matrix keyboard with an easy to learn layout, aimed at users who are not already touch-typing with QWERTY. It places the most common letters of the Engish language on the home row, arranged to form the words "read on this".

The layout shown here is a slight variation on the original PLUM layout, which placed the TAB and Backspace keys in the middle of the keyboard. I replaced those key positions with `;:` and `'"` to match other layouts compared here more closely.

With the common words on the home row, the layout achieves good scores for fast bigrams and 3-grams, only slightly lower than Workman. However, the main disadvantage is a very high number of same-finger bigrams, even worse than QWERTY. The heatmap scores and finger travel are also not as good as other ergonomic-optimized keyboard layouts.

---

# Optimization algorithm

## Metaheuristic

I chose to implement a metaheuristic based on Simulated Annealing [14] to find an optimal keyboard layout. Simulated annealing works by accepting worse solutions based on a temperature parameter that is gradually reduced as the optimization progresses.

I made some modifications to the basic algorithm in order to improve convergence to good solutions, or in other words, reduce the chances of getting stuck in a local optimum:

* Compare the score of new solutions with the best known solution rather than the current one
* If the current solution wanders too far away from the best known solution, reset to the best known solution
* Finding a new best solution is exothermic and raises the temperature proportionally to the increase in the score, to encourage more exploration starting from the new best solution

## Walking the solution space

Simulated annealing requires "small steps" through the solution space to find potentially better solutions from a known good solution. The solution in this case is a keyboard layout with discrete symbols assigned to discrete key positions. The smallest possible change one can make to a layout is to exchange two keys with one another. However, this can result in big changes in multiple metrics of the quality function.

In order to take smaller or more directed steps through the search space, it is desirable to apply transformations that change one or mostly one metric of the quality function. The following transformations were implemented and are chosen randomly in each step:

* Swapping entire fingers. This will not affect the same-finger bigram score
* Swapping keys within one finger. This will not affect the same-finger bigram score
* Swapping keys with similar weight. This is implemented by ranking keys by weight and exchanging keys within a small window based on that ranking. This will make only small changes to the heatmap score
* Basic random exchange of two arbitrary keys

## Performance

The algorithm was implemented in Python [10]. This language makes it easy to work with lists and dictionaries with efficient lookup implemented by the Python interpreter. It also lends itself to fast prototyping. It may not be the most efficient in terms of raw speed. However, there exists an alternative Python implementation called Pypy [11], which uses a JIT compiler and resulted in a factor three speedup compared to the Python reference implementation. An optimized implementation in C++ may achieve even better performance.

The current implementation can evaluate about 15000 keyboard layouts per second on a Ryzen 5 2400G running 3.6GHz when using Pypy3. When running four concurrent instances (using 4 independent cores on the Ryzen 5 processor), the performance drops to about 10000 keyboard layouts per second. I suspect this is the result of exceeding the size of shared caches.

Each evaluation of a layout involves 412 lookups in the bigram and 3-gram dictionaries. Thus, when running a single instance, the program is performing about 6 million lookups per second or about 580 CPU clocks per lookup, including all other overheads.

Starting from the first naive implementation, a speedup of about 30 was achieved by making the entire quality function O(1) with respect to the input text. A further factor of 3 speed-up comes from using Pypy instead of the Python reference implementation.

## Convergence of solutions

The performance optimizations allow the use of a fairly slow annealing schedule that lowers the temperature very gradually, while still completing in a reasonable amount of time. When running 4 concurrent instances, one run of the program completes in about 10 minutes with the annealing parameters chosen. The solutions seem to converge quite well with a relatively small set of solutions being discovered quite consistently within a narrow range of quality function scores (roughly 0.72 to 0.74).

A run on 4 CPU cores for about 24 hours performed 576 runs of the annealing schedule and found 223 unique solutions (counting mirrored versions as the same solution). The most popular solution was found independently by 43 program runs. The top scoring 10% of solutions accounted for 38% of all program runs.

---

# Results

## Examples of optimized Layouts

Out of 223 unique solutions found by 576 runs of the algorithm I picked 5 solutions to discuss the results. Each layout gets its own subsection showing the layout with the basic metrics and a short discussion.

### SEAR

    [ X ]  [ U ]  [ O ]  [. >]  [ Q ]  |  [ B ]  [ F ]  [ L ]  [ D ]  [ J ]
     0.2    5.3   15.3    3.4    0.4   |   2.6    5.0    8.0    7.0    0.7
    [ S ]  [ E ]  [ A ]  [ R ]  [, <]  |  [ P ]  [ C ]  [ N ]  [ T ]  [ I ]
    11.9   23.5   14.7   12.0    3.0   |   4.5    7.9   14.2   18.3   13.7
    [ V ]  [; :]  [' "]  [ H ]  [ Z ]  |  [ W ]  [ G ]  [ M ]  [ K ]  [ Y ]
     2.1    0.4    1.0    9.1    0.1   |   3.2    3.7    4.5    1.2    3.0
    14.2 + 29.2 + 31.0 + 28.0 = 102.4  |  97.6 = 26.9 + 26.8 + 26.5 + 17.5

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.7395 |         |
| Heatmap       | 0.9697 | 0.9186  |
| Bad bigrams   |   3.45 | ue:1.41 hr:0.39 nl:0.33 yi:0.33 oa:0.31 nm:0.29 eu:0.07 lm:0.06 rh:0.03 bc:0.03 pf:0.03 tk:0.03 pb:0.02 wp:0.02 ln:0.02 td:0.02 o':0.01 a':0.01 'a:0.01 fw:0.01 pg:0.01 wb:0.01 wf:0.01 |
| Slow bigrams  |  64.46 |         |
| Fast 3-grams  |  21.73 | ing:5.79 cti:2.59 ver:2.57 res:2.10 ear:1.04 hav:0.89 var:0.74 rou:0.66 ous:0.64 nti:0.64 has:0.55 cli:0.53 inc:0.52 sur:0.37 hes:0.31 seh:0.30 gni:0.24 sea:0.20 rev:0.18 ser:0.13 ldi:0.12 rus:0.11 ros:0.11 sor:0.08 nty:0.08 rav:0.05 vea:0.04 sar:0.03 ras:0.03 idl:0.02 itc:0.02 itn:0.01 |
| Fast bigrams  | 251.08 | he:22.17 in:16.92 er:15.98 re:12.64 or:11.28 ti:10.74 ct:9.39 nt:9.10 es:8.79 it:7.86 ng:7.64 ro:7.30 ve:6.91 ha:6.53 ar:5.70 ou:5.25 li:5.15 as:5.11 ra:5.10 se:4.96 rs:4.56 us:4.40 ic:4.13 ea:4.09 nc:4.04 il:3.41 sh:3.17 ur:2.78 su:2.52 ni:2.46 di:2.43 so:2.39 ig:2.36 ld:2.23 ru:2.11 ty:1.98 ev:1.97 sa:1.89 id:1.83 ci:1.54 va:1.41 os:1.35 av:1.32 gy:1.15 gi:1.07 cl:1.03 eh:0.65 gn:0.48 ny:0.46 cy:0.40 rv:0.32 dl:0.17 tc:0.16 yt:0.11 gt:0.09 tn:0.03 uo:0.02 sr:0.01 ah:0.01 hs:0.01 yn:0.01 yc:0.01 |
| Finger travel | 591.39 | 19.35 48.68 86.76 106.08 : 142.39 90.86 65.16 32.10 |
| Run length    |   1.59 | 1.49    |
| Times found   |      8 |         |

This was the best-scoring solution found by the annealing algorithm on this text sample.

The overall score is a further improvement on Colemak-DHm. Looking at some of the individual metrics, the improvements are quite dramatic. The bad bigrams score is more than factor 2 better than Colemak-DHm and factor 8 better than Workman. Fast bigrams are improved 43% over Colemak-DHm and 23% over Workman. In the fast 3-gram metric it scores 70% higher than Workman, factor 3 higher than Colemak-DHm.

The total number of same-hand bigrams in this layout is 276 per kKS. Out of those, 79% are fast bigrams. The next closest existing layout in this regard is Workman with 65% of all same-hand bigrams being fast bigrams.

The slow bigram number is 33% smaller than Dvorak. However that does not translate directly to a shorter average run length. This has to be expected, given that this layout has much more fast bigrams and 3-grams contributing to the average run length. For comparison, the total number of same-hand bigrams in Dvorak is 206 per kKS. However, in only 41% of them are fast bigrams in Dvorak.

Overall finger travel distance is similar to Colemak and Dvorak. However, it is more evenly distributed with significantly less travel for the index fingers. This layout still has relatively high finger travel for the right index finger and the right pinky do better in this metric.

The remaining layouts in this section have slightly lower overall scores than this one. However, analyzing them allows some insight into the trade-offs made by the algorithm and highlights different strategies found by the simulated annealing algorithm to optimize for the multi-objective quality function.

### REAT

    [ Z ]  [, <]  [ O ]  [. >]  [ Q ]  |  [ J ]  [ F ]  [ L ]  [ U ]  [ X ]
     0.1    3.0   15.3    3.4    0.4   |   0.7    5.0    8.0    5.3    0.2
    [ R ]  [ E ]  [ A ]  [ T ]  [ B ]  |  [ P ]  [ C ]  [ N ]  [ I ]  [ S ]
    12.0   23.5   14.7   18.3    2.6   |   4.5    7.9   14.2   13.7   11.9
    [ H ]  [; :]  [' "]  [ D ]  [ K ]  |  [ W ]  [ G ]  [ M ]  [ Y ]  [ V ]
     9.1    0.4    1.0    7.0    1.2   |   3.2    3.7    4.5    3.0    2.1
    21.3 + 26.8 + 31.0 + 32.8 = 111.9  |  88.1 = 25.0 + 26.8 + 22.1 + 14.2

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.7377 |         |
| Heatmap       | 0.9708 | 0.8645  |
| Bad bigrams   |   2.94 | ui:0.80 hr:0.39 nl:0.33 yi:0.33 oa:0.31 nm:0.29 iu:0.11 bt:0.08 lm:0.06 rh:0.03 tk:0.03 pf:0.03 uy:0.03 td:0.02 wp:0.02 ln:0.02 o':0.01 a':0.01 'a:0.01 db:0.01 fw:0.01 pg:0.01 wf:0.01 |
| Slow bigrams  |  73.10 |         |
| Fast 3-grams  |  25.57 | ing:5.79 hat:3.01 tor:3.01 ter:2.07 der:1.48 sin:1.16 red:0.84 rea:0.74 suc:0.63 eat:0.62 had:0.56 rat:0.52 inc:0.52 sig:0.50 ead:0.46 hea:0.44 sul:0.42 gis:0.39 hed:0.29 vin:0.29 gni:0.24 clu:0.19 rot:0.17 rad:0.17 giv:0.14 dar:0.13 niv:0.12 ret:0.10 tar:0.10 sic:0.07 vic:0.07 nis:0.07 cus:0.06 lus:0.06 cis:0.05 het:0.04 civ:0.02 |
| Fast bigrams  | 258.03 | th:24.22 he:22.17 in:16.92 er:15.98 re:12.64 at:11.30 or:11.28 to:8.99 ed:8.74 te:8.65 is:7.79 ng:7.64 ro:7.30 ha:6.53 de:6.20 ar:5.70 ra:5.10 tr:4.69 us:4.40 ic:4.13 si:4.11 ea:4.09 nc:4.04 ta:3.76 uc:3.16 ns:3.16 et:2.85 ot:2.78 su:2.52 iv:2.47 ni:2.46 ig:2.36 ul:2.11 rt:1.82 ad:1.79 ci:1.54 vi:1.53 cu:1.28 gi:1.07 cl:1.03 ht:0.99 sc:0.97 lu:0.89 rd:0.81 ls:0.72 eh:0.65 da:0.49 gn:0.48 dr:0.39 cs:0.33 gs:0.33 nv:0.32 sl:0.21 sn:0.09 hd:0.04 ah:0.01 sg:0.01 vg:0.01 |
| Finger travel | 584.70 | 49.96 29.25 86.76 115.00 : 124.35 90.86 69.17 19.35 |
| Run length    |   1.67 | 1.48    |
| Times found   |     15 |         |

This layout achieves better bad and fast bigram as well as fast 3-gram scores. Of all 334 same-hand bigrams per kKS, 77% are fast bigrams.

It compromises slightly on the per-finger heatmap and hand balance. I chose this over a very similar layout with slightly better finger heatmap score becuase it has less finger-travel, especially for the right index finger. Only the left pinky has a relatively high amount of travel, similar to the right pinky in Dvorak.

### EROT

    [; :]  [ H ]  [ A ]  [ Z ]  [ Q ]  |  [ J ]  [ F ]  [ L ]  [ U ]  [ X ]
     0.4    9.1   14.7    0.1    0.4   |   0.7    5.0    8.0    5.3    0.2
    [ E ]  [ R ]  [ O ]  [ T ]  [ B ]  |  [ P ]  [ C ]  [ N ]  [ I ]  [ S ]
    23.5   12.0   15.3   18.3    2.6   |   4.5    7.9   14.2   13.7   11.9
    [' "]  [. >]  [, <]  [ D ]  [ K ]  |  [ W ]  [ G ]  [ M ]  [ Y ]  [ V ]
     1.0    3.4    3.0    7.0    1.2   |   3.2    3.7    4.5    3.0    2.1
    24.8 + 24.5 + 33.0 + 29.6 = 111.9  |  88.1 = 25.0 + 26.8 + 22.1 + 14.2

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.7359 |         |
| Heatmap       | 0.9716 | 0.8078  |
| Bad bigrams   |   2.96 | ui:0.80 hr:0.39 nl:0.33 yi:0.33 oa:0.31 nm:0.29 iu:0.11 bt:0.08 lm:0.06 e':0.05 rh:0.03 tk:0.03 pf:0.03 uy:0.03 td:0.02 wp:0.02 ln:0.02 db:0.01 fw:0.01 pg:0.01 wf:0.01 |
| Slow bigrams  |  81.48 |         |
| Fast 3-grams  |  36.26 | the:16.11 ing:5.79 hat:3.01 tor:3.01 sin:1.16 ore:0.94 rod:0.67 suc:0.63 eat:0.62 inc:0.52 sig:0.50 sul:0.42 gis:0.39 vin:0.29 tre:0.26 gni:0.24 ert:0.20 clu:0.19 rot:0.17 doe:0.15 giv:0.14 dre:0.13 niv:0.12 or':0.08 sic:0.07 vic:0.07 nis:0.07 cus:0.06 lus:0.06 cis:0.05 ero:0.04 eha:0.02 erd:0.02 civ:0.02 |
| Fast bigrams  | 249.63 | th:24.22 he:22.17 in:16.92 er:15.98 re:12.64 at:11.30 or:11.28 to:8.99 ed:8.74 te:8.65 is:7.79 ng:7.64 ro:7.30 ha:6.53 de:6.20 tr:4.69 us:4.40 ic:4.13 si:4.11 ea:4.09 nc:4.04 ta:3.76 uc:3.16 ns:3.16 et:2.85 ot:2.78 su:2.52 iv:2.47 ni:2.46 ig:2.36 ul:2.11 do:1.85 od:1.84 rt:1.82 ci:1.54 vi:1.53 cu:1.28 gi:1.07 cl:1.03 ht:0.99 sc:0.97 lu:0.89 rd:0.81 ls:0.72 eh:0.65 eo:0.49 gn:0.48 dr:0.39 cs:0.33 gs:0.33 nv:0.32 oe:0.22 sl:0.21 t':0.15 r':0.10 sn:0.09 't:0.05 'r:0.01 ah:0.01 o':0.01 sg:0.01 vg:0.01 |
| Finger travel | 595.80 | 11.53 76.40 112.47 91.67 : 124.35 90.86 69.17 19.35 |
| Run length    |   1.67 | 1.48    |
| Times found   |     10 |         |

The right hand of this layout is identical to REAT. The changes in the right hand achieve much more fast 3-grams, mainly by making "the" a fast 3-gram. It compromises further on the per-finger heatmap, mainly by placing the most frequent letter "e" on the left pinky. However, since the left pinky doesn't have much else to do with two relatively infrequent punctuation keys, this is not a bad compromise. The travel distance for pinky fingers looks much better than REAT and SEAR.

As a consequence of the right hand being the same as REAT, both layouts have the same 334 same-hand bigrams per kKS. In this layout 75% of them are fast bigrams, compared to 77% in REAT.

The arrangement of the punctuation keys is like a reverse version of Dvorak with the top and bottom row swapped.

Some of the keys on the left index finger are arranged in a non-intuitive way, with the least frequent letter "z" on a higher-weighted key than "b". This is a quirk in the way the heatmap is scored, penalizing underuse less than overuse of keys. Manually rearranging them changes only the key heatmap score leaves the overall score nearly unchanged at 0.7358:

    [; :]  [ H ]  [ A ]  [ B ]  [ Z ]  |  [ J ]  [ F ]  [ L ]  [ U ]  [ X ]
     0.4    9.1   14.7    2.6    0.1   |   0.7    5.0    8.0    5.3    0.2
    [ E ]  [ R ]  [ O ]  [ T ]  [ K ]  |  [ P ]  [ C ]  [ N ]  [ I ]  [ S ]
    23.5   12.0   15.3   18.3    1.2   |   4.5    7.9   14.2   13.7   11.9
    [' "]  [. >]  [, <]  [ D ]  [ Q ]  |  [ W ]  [ G ]  [ M ]  [ Y ]  [ V ]
     1.0    3.4    3.0    7.0    0.4   |   3.2    3.7    4.5    3.0    2.1
    24.8 + 24.5 + 33.0 + 29.6 = 111.9  |  88.1 = 25.0 + 26.8 + 22.1 + 14.2

### NEAI

    [ Z ]  [' "]  [ O ]  [. >]  [ X ]  |  [ W ]  [ D ]  [ H ]  [ T ]  [ J ]
     0.1    1.0   15.3    3.4    0.2   |   3.2    7.0    9.1   18.3    0.7
    [ N ]  [ E ]  [ A ]  [ I ]  [ Y ]  |  [ F ]  [ C ]  [ R ]  [ M ]  [ S ]
    14.2   23.5   14.7   13.7    3.0   |   5.0    7.9   12.0    4.5   11.9
    [ B ]  [; :]  [ Q ]  [ U ]  [, <]  |  [ G ]  [ P ]  [ L ]  [ K ]  [ V ]
     2.6    0.4    0.4    5.3    3.0   |   3.7    4.5    8.0    1.2    2.1
    16.9 + 24.8 + 30.4 + 28.7 = 100.8  |  99.2 = 31.3 + 29.1 + 24.0 + 14.7

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.7346 |         |
| Heatmap       | 0.9336 | 0.9580  |
| Bad bigrams   |   3.26 | ui:0.80 hr:0.39 yi:0.33 oa:0.31 dg:0.29 rl:0.26 aq:0.16 xi:0.15 iu:0.11 tm:0.08 ix:0.07 e':0.05 uy:0.03 pf:0.03 rh:0.03 tk:0.03 bn:0.02 wp:0.02 oq:0.01 wf:0.01 df:0.01 dp:0.01 fw:0.01 gd:0.01 pd:0.01 pg:0.01 lr:0.01 km:0.01 |
| Slow bigrams  |  52.96 |         |
| Fast 3-grams  |   8.80 | ion:5.61 ien:0.88 cts:0.62 iab:0.47 uen:0.28 ian:0.19 uan:0.15 bea:0.13 nai:0.08 bei:0.08 neu:0.07 nea:0.05 rms:0.05 noi:0.03 eau:0.03 nei:0.02 stc:0.02 bai:0.01 hts:0.01 |
| Fast bigrams  | 186.14 | th:24.22 in:16.92 an:15.93 on:14.50 en:11.53 ct:9.39 st:8.08 io:5.93 pr:5.55 rs:4.56 no:4.52 ne:4.28 ea:4.09 ch:3.78 be:3.22 ts:3.20 sh:3.17 na:3.13 un:2.87 ie:2.79 mp:2.66 rm:2.61 ia:2.59 ni:2.46 ai:2.20 cr:2.16 bu:2.15 ab:1.98 ue:1.41 sp:1.36 ua:1.31 ba:1.24 bi:1.03 ht:0.99 sc:0.97 au:0.89 ub:0.85 sm:0.81 ei:0.74 rc:0.71 ib:0.38 ms:0.37 ps:0.34 cs:0.33 rv:0.32 n':0.31 oi:0.29 nu:0.22 pm:0.20 tc:0.16 rp:0.15 eb:0.11 eu:0.07 i':0.06 o':0.01 sr:0.01 hs:0.01 |
| Finger travel | 602.07 | 22.98 11.53 80.35 119.36 : 171.41 116.94 55.47 24.02 |
| Run length    |   1.41 | 1.34    |
| Times found   |      3 |         |

This solution is heavily optimized for fewer slow bigrams. The necessary compromise is a much lower number of fast 3-grams, comparable to Colemak-DHm. Similar to Dvorak, this layout places all vowels in the same hand, which tends to favour alternating hands between keystrokes. The total number of same-hand bigrams per kKS is 242, getting close to Dvorak. However, out of those, 77% are fast bigrams, much better than Dvorak's 41%.

Finger travel for the right index finger is quite high in this and similar layouts.

### NEAT

    [ Z ]  [, <]  [ O ]  [ G ]  [ Q ]  |  [ J ]  [ F ]  [ R ]  [ U ]  [ X ]
     0.1    3.0   15.3    3.7    0.4   |   0.7    5.0   12.0    5.3    0.2
    [ N ]  [ E ]  [ A ]  [ T ]  [. >]  |  [ P ]  [ C ]  [ H ]  [ I ]  [ S ]
    14.2   23.5   14.7   18.3    3.4   |   4.5    7.9    9.1   13.7   11.9
    [ B ]  [; :]  [' "]  [ M ]  [ K ]  |  [ W ]  [ D ]  [ L ]  [ Y ]  [ V ]
     2.6    0.4    1.0    4.5    1.2   |   3.2    7.0    8.0    3.0    2.1
    16.9 + 26.8 + 31.0 + 31.5 = 106.3  |  93.7 = 28.3 + 29.1 + 22.1 + 14.2

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.7332 |         |
| Heatmap       | 0.9646 | 0.9413  |
| Bad bigrams   |   2.68 | ui:0.80 hr:0.39 yi:0.33 oa:0.31 rl:0.26 iu:0.11 gt:0.09 tm:0.08 gm:0.03 tk:0.03 kg:0.03 pf:0.03 rh:0.03 uy:0.03 bn:0.02 wp:0.02 o':0.01 a':0.01 'a:0.01 km:0.01 fw:0.01 pd:0.01 wf:0.01 df:0.01 dp:0.01 lr:0.01 |
| Slow bigrams  |  96.41 |         |
| Fast 3-grams  |  15.73 | man:3.00 men:2.94 his:2.12 not:1.28 ten:0.69 suc:0.63 eat:0.62 tab:0.57 tan:0.50 sur:0.37 nat:0.36 bet:0.36 chi:0.36 sid:0.27 dis:0.19 vid:0.15 eam:0.13 bea:0.13 rus:0.11 urc:0.10 bat:0.09 ton:0.09 div:0.09 sic:0.07 vic:0.07 net:0.06 nam:0.06 bam:0.06 cus:0.06 nea:0.05 cis:0.05 nem:0.02 cru:0.02 civ:0.02 meb:0.01 |
| Fast bigrams  | 192.74 | an:15.93 on:14.50 en:11.53 at:11.30 nt:9.10 to:8.99 te:8.65 is:7.79 me:6.83 hi:5.68 ma:4.81 rs:4.56 no:4.52 us:4.40 ne:4.28 ic:4.13 si:4.11 ea:4.09 ch:3.78 ta:3.76 be:3.22 sh:3.17 uc:3.16 na:3.13 et:2.85 ot:2.78 ur:2.78 em:2.57 su:2.52 iv:2.47 di:2.43 cr:2.16 ru:2.11 ab:1.98 id:1.83 ci:1.54 vi:1.53 am:1.39 cu:1.28 ba:1.24 sc:0.97 rc:0.71 ds:0.66 mb:0.44 cs:0.33 nm:0.29 eb:0.11 dv:0.11 bt:0.08 ih:0.06 hd:0.04 tn:0.03 sr:0.01 hs:0.01 |
| Finger travel | 601.24 | 22.98 29.25 86.76 109.30 : 143.10 121.33 69.17 19.35 |
| Run length    |   1.51 | 1.44    |
| Times found   |     43 |         |

This is the most frequently found unique layout. It has very good heat map and bad bigrams scores. Its fast bigrams and 3-grams scores aren't bad but not great. The total number of same-hand bigrams per kKS is 292, of which 66% are fast bigrams, similar to workman.

One interesting and counter-intuitive optimization is the placement of "h" and "r". The heatmap would prefer "r" in the home row and "h" above. However, that would result in fewer fast bigrams ("ru" and "ur") and 3-grams, which outweighed the small difference in the heatmap score.

## Statistics

The plots in this section are bar charts where each bar represents the number of solutions in a small range of score values. This provides a visual representation of the distribution of scores. All distributions display strong peaks around popular solutions. Some of them are skewed in one direction.

### Overall score distribution

    116┤                                               ▂                
       │                                               █                
    100┤                                               █                
       │                                               █                
     84┤                                               █                
       │                                               █                
     68┤                                               █                
       │                                               █                
     52┤                                               █                
       │                                            █  █                
     36┤                                     ▁      █  █            ▂   
       │                                     █      █  █            █   
     20┤                                ▂    █ ▃    █  █      ▁     █   
       │                             ▁ ▅█ ▅▂▇█▅█▁▃▇██▆ █▁▄▅  ▄█    ▇█ █ 
      4┤▁     ▁  ▁ ▄▁ ▃  ▁▁▄▂▂▇▁▅  ▄▇████▆████████████▇████▄ ██    ██ ██
       └┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────
      0.714 0.716 0.719 0.721 0.724 0.726 0.728 0.731 0.733 0.736 0.738

Overall scores are distributed in a fairly narrow range, with values significantly higher than existing layouts. The strong peak at 0.7332 is around the most popular solution "NEAT".

### Heatmap score distribution

       │                                      ▆                  
     58┤                                      █                  
       │                                      █                  
     50┤                                 █    █                  
       │                                 █    █                  
     42┤                                 █    █                  
       │                                 █    █                  
     34┤                                 █▄   █                  
       │                                 ██   █ ▄                
     26┤                         ▆       ██   █ █ █              
       │                     ▂   █ ▂█    ██   █ █ █              
     18┤                     █▂  █ ██    ██ ▂ █ █ █              
       │                     ██ ▆█▂██    ██ █ █▂█▄█▆             
     10┤               ▆     ██ █████    ██ █▄██████▆▄ ▆         
       │              ▆█     ██▂███████  ███████████████▂▄▆ ▆▆ ▄ 
      2┤▂ ▂▂        ▂████▄▂█▄██████████▆▄███████████████████████▆
       └┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────
      0.916 0.924 0.931 0.939 0.946 0.954 0.961 0.969 0.976 0.984

All solutions achieved very good heatmap scores above 0.9. Colemak variants and Workman fall within the same range.

### Finger heatmap score distribution


    100┤                                            ▁            
       │                                            █            
     84┤                                            █            
       │                                            █            
     68┤                                            █            
       │                                            █            
     52┤                                            █            
       │                                        ▁   █            
     36┤                          ▄           ▂ █   █            
       │                          █         ▆ █▂█   █▃           
     20┤          ▂              ▂█      ▁ ▆█ ███   ██           
       │          █         ▅    ██▃   ▆ █▄██▇███▄▇▄██▁█▄        
      4┤▁     ▇▁▁▁█▂▁   ▃▅▂▂█▆▁▁▄███▆▂▇██████████████████▃   ▄  ▁
       └┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────
      0.764 0.788 0.812 0.836 0.860 0.884 0.908 0.932 0.956 0.980

The finger heatmap scores are more widely distributed, but skewed towards higher values. There is a strong peak around O.94, which includes "NEAT".

### Bad bigrams distribution

     66┤     ▄                                                         
       │     █                                                         
     58┤  █  █                                                         
       │  █  █                                                         
     50┤  █  █                                                         
       │  █  █                                                         
     42┤  █  █   ▆                                                     
       │  █  █   █                                                     
     34┤  █  █   █    █ ▄                                              
       │  █  █   █    █ █                                              
     26┤  █  █   █▄   █ █                                              
       │ ██  █ ▆ ██▄▂ █▄█                                              
     18┤ ██  █ █ ████ ███                                              
       │ ██  █ █ ████ ███▂            ▆                                
     10┤ ██  █▄█▂████▆████▂ ▆    █▆   █                                
       │███▂▆██████████████▄█▆▂ ▆██▂▆▆██▆                              
      2┤█████████████████████████████████▆▆▄▄▂ ▂▂  ▂                  ▂
       └┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────
       2.48  2.96  3.44  3.92  4.40  4.88  5.36  5.84  6.32  6.80  7.28

This distribution is strongly skewed towards smaller values. Many of the the highest-scoring solutions are located around the second and third peak. There is one outlier at over 7 bad bigrams per kKS, which was also the overall lowest scoring solution.

### Slow bigrams distribution

       │                               ▂                      
     66┤                               █                      
       │                               █                      
     58┤                   ▂           █                      
       │                   █           █                      
     50┤                   █           █                      
       │                   █           █                      
     42┤                   █           █                      
       │                   █           █                      
     34┤                   █           █                      
       │                   █   █       █             ▆        
     26┤                   █   █       █             █        
       │              ▆    █   █       █             █        
     18┤              █    █ █ █     ▄ █▄            █    ▄   
       │       █ ▂ ▂  █   ██ █ █ ██  █ ██            █  ▂ █   
     10┤       █ █ █▄ ██  ██ █ ████ ▂█ ██ ▆      ▄   █  █ █   
       │  ▂  ▆▂███▆██▄██ ▂██▂█ ████▆██▆██▆█▂     █▄  █  █ █   
      2┤▂▄█▂▆███████████▄████████████████████▄▄▄███▂▆█▂ █▆█▄▆▆
       └┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────
        34    46    58    70    82    94   106   118   130 

This distribution covers a very wide range of values with the highest peaks near the center. It doesn't appear to be skewed one way or the other.

### Fast 3-grams distribution

       │                  █                                         
     58┤                  █                                         
       │                  █                                         
     50┤                  █               █                         
       │                  █               █                         
     42┤                  █               █                         
       │                  █               █                         
     34┤                  █          ▂    █                         
       │                  █          █    █         ▄       ▆       
     26┤       ▆          █          █    █         █       █       
       │       █          █         ██    █   ▄     █       █       
     18┤       █          █       █▆██    █   █     █▄      █       
       │       █          █    ▄  ████ █  █▂  █     ██      █       
     10┤      ███     ▄   █▂   █▆▆████ █  ██▂ █    ▄██      █       
       │      ███     ██  ███  █████████ ▄███ █ ▂  ███      █ ▆     
      2┤▂    █████▄█▄▄███▆███▆▆█████████▂████▂███▆████▂▂▆▆█▆█▂█▂▄▂▂▂
       └┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────
       4.8   8.4  12.0  15.6  19.2  22.8  26.4  30.0  33.6  37.2 

Fast 3-gram scores are very widely distributed with one outlier at 4.8 (actually 5.26) from a another solution similar to "NEAI".

### Fast bigrams distribution

       │                          █                                          
     58┤                          █                                ▄         
       │                          █                         █      █         
     50┤                          █                         █      █         
       │                          █                         █      █         
     42┤                          █                         █      █         
       │                          █                         █      █         
     34┤                          █                         █  ▂   █         
       │                          █                       █ █ ▆█   █         
     26┤                          █                       █ █ ██   █         
       │                          █                       █ █▆██   █         
     18┤                     ▄    █             ▂         █ ████   █         
       │                     █    █             █▂ ▆      █▂████   █    ▄    
     10┤                    ██    █     ▂       ██ █      ██████▄▂ █    █    
       │                    ██ █ ▂█ █   █▄ ▂ █ ▄██ █ ▂█▄▄█████████▂█▂▄  █ █  
      2┤▂                ▂▂▆██▄█▂█████▄ ██▄█▆█▆███▂████████████████████████ ▄
       └┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────
       140   152   164   176   188   200   212   224   236   248   260   272 

This distribution is generally skewed towards higher values, but with a strong peak at 193, representing "NEAT". There is an outlier at the lower end at 140 representing a solution similar to "NEAI".

### Finger travel distribution

       │                       █                                     
     58┤                       █                                     
       │           █           █                                     
     50┤           █           █ ▂                                   
       │           █           █ █                                   
     42┤           █           █ █                                   
       │           █           █ █                                   
     34┤           █           █▆█                                   
       │           █           ███                                   
     26┤           █        ▄  ███                                   
       │           █        █ ████  ▂                                
     18┤           █        █ ████  █▄▄    ▂                         
       │      ▆   ▂█ ▂  ▆█  █ ████  ███    █   █                     
     10┤    ▆ █   ██ █  ██ ▆█ ████▄▂███ █ ▆█   █                     
       │    █ █   ████  █████ █████████ █▄██   █   ▄ ▄       ▄       
      2┤█▄  █ █▄▂▆████▆███████████████████████▂█▂█ █▆█▆▄  ▄▄ █▂ ▂   ▂
       └┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────
       578   584   590   596   602   608   614   620   626   632   638 

Finger travel distance is distributed over a fairly narrow range with most solutions falling in the middle, around 600 per kKS.

---

# TODO

* Include finger travel or some estimate that's efficient to calculate from the heatmap in the quality function
* Build a more representative English text sample
* Investigate other languages (German, being my first language, is a good starting point)
* Investigate optimizing layouts for two languages (e.g. German and English)

# Conclusion

It was demonstrated that keyboard layouts can be algorithmically optimized. A quality function was defined, which can be computed efficiently. A simulated annealing algorithm was developed, which is able to converge on a set of good solutions, which significantly outperform existing keyboard layouts in common metrics.

It was shown in a few examples, that the choice of input text or texts affects the generality of the solution. More work is needed to build a representative sample of the English language. Other languages can be considered in the future. In particular it would be interesting to optimize keyboard layouts for multiple languages.

---

# References

[1] [Fact or Fiction? The Legend of the QWERTY Keyboard](https://www.smithsonianmag.com/arts-culture/fact-of-fiction-the-legend-of-the-qwerty-keyboard-49863249/)<br>
[2] [QMK Firmware - Layers](https://docs.qmk.fm/#/feature_layers)<br>
[3] [The Dvorak Keyboard — a Primer](https://www.dvorak-keyboard.com/)<br>
[4] [Colemak Keyboard Layout](https://colemak.com/)<br>
[5] [Workman Keyboard Layout](https://workmanlayout.org/)<br>
[6] [Neo – an Ergonomic Keyboard Layout, optimized for the German Language](https://neo-layout.org/index_en.html)<br>
[7] Patrick Gillespie’s [Keyboard Layout Analyzer](http://patorjk.com/keyboard-layout-analyzer/#/main)<br>
[8] SteveP's fork of the [Keyboard Layout Analyzer](https://stevep99.github.io/keyboard-layout-analyzer/#/main)<br>
[9] [10 Fast Fingers typing test](https://10fastfingers.com/typing-test/english)<br>
[10] [Python.org](https://www.python.org/)<br>
[11] [A fast, compliant alternative implementation of Python](https://www.pypy.org/)<br>
[12] [Colemak Mod-DH](https://colemakmods.github.io/mod-dh/)<br>
[13] [PLUM keyboard](https://en.wikipedia.org/wiki/PLUM_keyboard)<br>
[14] [Simulated Annealing](https://en.wikipedia.org/wiki/Simulated_annealing)<br>