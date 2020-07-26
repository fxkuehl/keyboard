Searching for the optimal keyboard layout
=========================================

***Empirically quantifying and optimizing keyboard layouts***

**Author:** *Felix Kuehling*

# Introduction

Most keyboard layouts in use today are based on historical keyboard designs for mechanical typewriters. The typical staggered-row design is a result of lever arms having to pass each other between rows of a mechanical keyboard. The origin of the common QWERTY layout is a somewhat murky. It may be to avoid jamming of the typewriter mechanism or be a legacy from transcription of Morse code. [1] Either, way, those design constraints do not apply to modern computer keyboards, yet they have been carried over almost without being questioned.

A few attempts have been made to redesign computer keyboards for ergonomic considerations, both in terms of physical layout and the mapping of symbols to keys. On the physical side, ergonomic keyboards are often split designs with the two halves at an angle to put the wrists into a more neutral position. However, most of the more affordable or main-stream designs still carry over the row stagger. More radical designs either choose a regular matrix (ortholinear) layout or a column stagger that attempts to match the different lengths of the fingers. There are many designs that reduce the number of physical keys to the ones within easy reach without having to move the hands. On such keyboards, more functions and symbols are activated by switching layers. [2]

In terms of ergonomic keymaps, the oldest example I'm aware of is the Dvorak [3] layout, which was patented in 1936. More modern layouts for the English language include Colemak [4] and variations, Workman [5], Neo [6].

I have personally used QWERTZ (German version of QWERTY), QWERTY, Dvorak and Colemak. Learning a new layout is a time-consuming process. Whether using one keyboard layout over another leads to more speed or comfort is hard to judge objectively for any individual.

This project attempts to approach the problem of the optimal keyboard layout algorithmically as an optimization problem. The quality of the existing layouts can be quantified objectively using different criteria. There are several online keyboard layout analyzers available [7,8] that can be used to analyze small numbers of keyboard layouts. A potentially more optimal layout could be found by automatically searching the entire space of all possible keyboard layouts for a global optimum.

The remainder of this document is divided into several sections.

**Assumptions and Limitations** defines the scope of this project, what parts of the keyboard layout are part of the attempted optimization, and a brief discussion of the size of the search space.

**Quality function** describes the design of the quality function, which quantifies for the search algorithm what makes a good keyboard layout.

**Optimization algorithm** describes the basic elements of the simulated annealing algorithm that was implemented, concluding with its performance and convergence to good solutions.

**Results** presents a selection of keyboard layouts found by the algorithm.

---

# Assumptions and limitations

Typical computer keyboards have between roughly 60 to 100 keys. Many of those keys are assigned to special functions or rarely used symbols. Many of those special keys are used very differently by different users, depending on whether they are writing text, computer programs, performing data entry, using CAD applications, gaming, etc. Therefore this project is going to focus on the central area of the keyboard containing the alphabetical keys and the most common punctuation characters. This should make it applicable to a wide range of keyboards, including minimalist ergonomic ones with 40 or fewer keys.

Any user willing to adopt a radically different keyboard layout for purposes of efficiency or comfort is also likely to be willing to switch to a programmable, ergonomic or ortholinear keyboard. So some assumptions of typical QWERTY keyboards with staggered rows may not be applicable. Specifically the position of Space, Shift, Caps-Lock, TAB, Enter and Backspace keys may be unusual. Furthermore, ergonomic keyboards have more keys available to the thumbs to take over some of those functions usually performed by the pinky fingers or require moving the hands away from the home position. Therefore all of those special keys are excluded from the analysis.

## Reduced keyboard layout

I am going to assume three rows of keys with 1O keys per row available for typing. A QWERTY layout can be represented in this reduced keyboard as follows:

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

This distance measure has the property that the element with the biggest deviation will have the biggest effect on the overall distance value. However, a deviation from O.1 to 1 and a deviation from 10.1 to 11 will be measured equally far. For key usage frequencies this is not a good measure because in the first case, a key is over-used or under-used by a factor 10. In the second case it is over-used or under-used by about 1.089. A measure that would express that "factor of deviation", which scales with the magnitude of the values would be better. I am proposing the following distance metric:

> d = sqrt((log A<sub>1</sub>/B<sub>1</sub>)<sup>2</sup> + ...+ (log A<sub>n</sub>/B<sub>n</sub>)<sup>2</sup>)

As long as neither A nor B are 0, this metric provides a useful distance measure between key weights and a heatmap.

Similarly to individual keys, the finger weights can be evaluated. The weight of the finger is calculated by adding all the weights of the individual keys operated by that finger. The actual usage of the finger is calculated by adding the character frequencies of all characters typed by the finger.

The character probabilities in the input text can be calculated ahead of time. Then the distance metric has O(1) effort with respect to the size of the input text.

The distance should be normalized to the common value range 0 to 1. The lowest possible value should map to 0, the highest to 1. The lowest possible distance is obviously 0. However, given the character frequencies of an input text, a perfect 0 distance is likely impossible to achieve. The closest one can get is by assigning the most frequent characters to the highest weighted keys in order and calculating the resulting distance. Conversely the biggest possible distance can be calculated by assigning the most frequent characters to the lowest weighted keys. The actual score can be scaled linearly within this range such that a 0 distance maps to 1.0 and a maximal distance maps to 0.0.

For finger weights and heatmaps this calculation is a bit more difficult. The finger heatmap can get much closer to 0 distance by combining key frequencies differently. To simplify the calculation we can assume that it will get close enough to 0 that it's not worth calculating the actual best possible value for the actual character frequencies of a given input text. The biggest possible distance can be approximated with prior knowledge of the finger weights (see the weight parameters in the next section): Placing the most frequent keys on the pinky fingers, the next most frequent keys on the ring fingers, the next most frequent keys on the index fingers (which take 6 keys each) and the least frequent ones on the middle fingers.

The arithmetic mean of the normalized distance metric of key and finger usage and weights forms the heatmap metric. The finger and key metrics can also be weight differently or scaled non-linearly, e.g. using a square root function. Using a square root changes the slope of the metric, with a smaller slope at higher values. That means, the sensitivity to heatmap changes is reduced for higher heatmap scores. This can allow more flexibility in trade-offs of heatmap against other quality metrics.

After some experimentation I chose to weigh the finger and key heatmap distances equally but apply a square root function to the key metric.

The choice of key weights is a tuneable quality function parameter (or rather a vector of 30 parameters). To get ambidextrous keyboard layouts, those weights should be symmetric between the left and right hand, which effectively reduces the number of parameters to 15.

### Fast, slow and bad bigrams

The set of all potential bigrams (2-symbol sequences) can be determined from the input text, and the probability or frequency of each bigram can be stored in a lookup table.

From the keyboard layout a set of fast, slow, and bad bigrams can be generated. Fast bigrams are those, which are particularly comfortable or fast to type. Rolling motions from finger to finger without having to stretch uncomfortably should be favoured by the optimal keyboard layout. For example the sequence "AD" on the QWERTY layout would be a good bigram.

Bad bigrams are those, which use the same finger to type different letters. For example the sequence very common bigram "ED" is a bad bigram in the QWERTY layout.

Any bigram that uses the same hand but is neither fast nor bad increases the number of consecutive keys one hand would have to type on average before alternating hands without much benefit. This can lead to fatigue and to slowing down the flow of typing. Therefore I call these "slow bigrams". For example the Dvorak layout is heavily optimized for alternating hands between keystrokes. So Dvorak has very few slow bigrams but also very few fast bigrams.

A good keyboard layout would balance good and slow bigrams, trying to maximize good bigrams while minimizing slow bigrams as much as possible.

From the fast, bad and slow bigrams of the keyboard layout and the bigram frequencies of the input text, a count of fast, bad, and slow bigrams can be calculated. These counts can be scaled by the total number of keystrokes to give a range from 0 to 1. We want the number of bad bigrams to be very small. So the quality function should be more sensitive in the small value range. This can be achieved with square root or 3rd root functions. For very small values this function has a very steep slope. That means the quality function will be very sensitive to small changes when the number of bigrams is small. For larger values the slope becomes more shallow, thus the sensitivity decreases.

Calculating the frequency of bigrams using this method is O(1) with respect to the size of the input text. The number of bigrams in the lookup table depends on the input text. However, a good hash table implementation for the lookup should also be O(1).

The set of good and bad bigrams is a choice of parameters of the quality function.

### Fast 3-grams

Taking this one step further, one can also consider 3-grams and 4-grams that can be typed fast, with one rolling motion of the fingers on one hand. Useful 4-grams would be very rare and are not considered, here. However, fast 3-grams are worth optimizing for. For example "oin" as in "ointment" and "ast" as in "last" would be considered fast 3-grams in the Colemak layout.

Algorithmically, fast 3-grams can be derived from two fast bigrams that travel in the same direction where the first one's second key is the same as the second one's first key. For example "oin" in Colemak is composed of the two fast bigrams "oi" and "in".

The frequencies of trigrams in the input text can be calculated ahead of time and stored in a lookup table. Then the frequncy of fast bigrams in a given keyboard layout can be calculated in the same way as the bigram frequencies in O(1) with respect to the length of the input text.

Again, they can be scaled to a value range from 0 to 1 by dividing by the total number of keystrokes. However, the biggest possible number of 3-grams in a degenerate input text is only half the total number of key strokes, because with four fingers in each hand only two overlapping 3-grams can be typed before having to start a new one. E.g. in Colemak, the text "arstarst..." repeating would be counted as overlapping "ars" and "rst" 3-grams, with the total number being two 3-grams for every four key-strokes. Thus the scaling factor should be only half the number of keystrokes.

If the fast 3-grams are automatically generated from fast bigrams, this metric has no tuneable parameters.

### Other metrics

Other metrics have been considered and even implemented. However, they are less computationally efficient and are therefore not used in the optimization. Most notably, the finger travel distance can only be calculated by actually simulating every key stroke, which is O(n) with respect to the length of the input text.

In practice, it is observed that the finger travel distance achieved with the heatmap and bigram-based metrics is reasonable and within the same range as existing ergonomic layouts. Furthermore, the travel distances don't differ by a huge amount between good and bad layouts. By contract, the bigram metrics can differ by more than one order of magnitude.

## Determining parameters of the quality function

### Weights

The following weights were used:

         1 |  6 |  7 |  2    1  ||  1    2 |  7 |  6 |  1
        10 | 12 | 15 | 10    4  ||  4   10 | 15 | 12 | 10
         4 |  2 |  3 |  5    3  ||  3    5 |  3 |  2 |  4
    =======|====|====|==========||=========|====|====|=======
        15 | 20 | 25 | 25       ||      25 | 25 | 20 | 15
    =======|====|====|==========||=========|====|====|=======
     Pinky |Ring| Mid| Index    ||   Index |Mid |Ring| Pinky

The strong fingers are weighted more heavily. Since the index finger reaches more keys, its individual key weights tend to be smaller. Keys that require more of a stretch are weighted lower. For example the middle and ring fingers can stretch up relatively easily, whereas the index and pinky fingers are typically shorter and prefer to curl to reach the bottom row rather than stretching up to the top row.

Aggressive column stagger on some ergonomic keyboards can compensate for some of the differences in finger length and their different ability to stretch up or down. Thus the weights may have to be adjusted for such keyboards.

### Fast bigrams

Which bigrams are easy to type may be somewhat subjective. This is the set chosen in my implementation expressed in terms of the left hand of the QWERTY layout. They are separate into two sets, left-to-right and right-to-left in order to facilitate automatic generation of fast 3-grams:

#### Left-to-right
>WE, WF,<br>
>EF,<br>
>AE, AS, AD, AF, AV,<br>
>SD, SF, SV,<br>
>DF, DV,<br>
>ZS, ZD, ZF, ZV,

#### Right-to-left
>FW, FE, FA, FS, FD, FZ,<br>
>VA, VS, VD, VZ,<br>
>EW, EA,<br>
>DS, DA, DZ,<br>
>SA, SZ

These are 34 fast bigrams for the left hand. When mirrored for the right hand this results in a total of 68 fast bigrams.

### Auto-generated bigrams and 3-grams

Bad bigrams, slow bigrams, and fast 3-grams are automatically generated by the program:

>bad bigrams: 96<br>
>slow bigrams: 256<br>
>fast 3-grams: 56

Only bad bigrams and slow bigrams are calculated in the quality function. Since the set of slow bigrams excludes fast bigrams, it is an indirect measure of fast bigrams. The same could be said for bad bigrams, which are also excluded from the set of slow bigrams. However, bad bigrams use a different non-linear scaling to optimize for very small values.

Thus the total number of bigrams and 3-grams that need to be looked to evaluate the quality function of one keyboard layout is 96 + 256 + 56 = 408.

### Input text

The input text used to evaluate the quality function can also be understood as a parameter. It determines the language that the keyboard layout gets optimized for.

From early experience it appears that the size and diversity of the input text is important for making a keyboard layout that generalizes to most texts. For example initial experiments using a chapter from the Junglebook as input gave a skewed perception of common bigrams that did not generalize to other texts. For example the bigram "ow" is quite common in this text from the name "Mowgli", but it is not common in the English language in general.

Another reverse example, running experiments with two texts found very good solutions for those texts, but they didn't generalize well for other texts. It was found that the initial two texts didn't represent the "je" bigram well. A resulting keyboard layout applied to another text that included the word "project" many times performed poorly because it had "j" and "e" on the same finger.

These problems with input texts can be addressed in two different ways:

* Concatenating many diverse texts
* Preprocessing texts to remove unusual names or typos

Both approaches are being applied in the experiments below. Preprocessing uses a word list to filter all words in the text. Rejected words are output into a new "missing words" list that can be manually vetted. Any real words can be added to the canonical word list. Typos and unusual names can be left out.

The texts used in these experiments were copied from [8] and then preprocessed against a growing canonical word list.

---

# Optimization algorithm

## Metaheuristic

I chose to implement a metaheuristic based on Simulated Annealing to find an optimal keyboard layout. Simulated annealing works by accepting worse solutions based on a temperature parameter that is gradually reduced as the optimization progresses.

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

The current implementation can evaluate about 16000 keyboard layouts per second on a Ryzen 5 2400G running 3.6GHz when using Pypy3. When running four concurrent instances (using 4 independent cores on the Ryzen 5 processor), the performance drops to about 10000 keyboard layouts per second. I suspect this is the result of exceeding the size of shared caches.

Each evaluation of a layout involves 408 lookups in the bigram and 3-gram dictionaries. Thus, when running a single instance, the program is performing about 7.5 million lookups per second or about 550 CPU clocks per lookup, including all other overheads.

Starting from the first naive implementation, a speedup of about 30 was achieved by making the entire quality function O(1) with respect to the input text. A further factor of 3 speed-up comes from using Pypy instead of the Python reference implementation.

## Convergence of solutions

The performance optimizations allow the use of a fairly slow annealing schedule that lowers the temperature very gradually, while still completing in a reasonable amount of time. When running 4 concurrent instances, one run of the program completes in about 13 minutes with the annealing parameters chosen. The solutions seem to converge quite well with a relatively small set of solutions being discovered quite consistently within a narrow range of quality function scores (roughly 0.72 to 0.74).

A run on 4 CPU cores for about 13 hours performed 247 runs of the annealing schedule and found 119 unique solutions (counting mirrored versions as the same solution). The most popular solution was found independently by 18 program runs. This was also the highest-scoring solution.

---

# Results

Out of 119 unique solutions found by 247 runs of the algorithm I picked 9 solutions to discuss the results. Each layout gets its own subsection showing the layout with the basic metrics and a short discussion. The last subsection shows graphs of the distribution of all solutions with respect to various metrics.

Each keyboard layout is shown with key and finger weights normalized to match the weights used in the heatmap metric of the quality function.

The metrics are presented as follows:

| Metric        | Value       | Details |
| ------------- | ----------- | :------ |
| Overall score | Score of the quality function | |
| Heatmap       | 0 to 1 key metric | 0 to 1 finger metric |
| Bad bigrams   | Total count | Count for each bigram |
| Slow bigrams  | Total count |         |
| Fast 3-grams  | Total count | Count for each 3-gram |
| Fast bigrams  | Total count | Count for each bigram |
| Finger travel | Total in units of the key size | Per-finger travel, normalized per 1000 keystrokes |
| Run length    | Avg # consecutive keystrokes: Left hand | Right hand |
| Times found   | # of times solution was found in 247 runs | |

Fast bigrams, finger travel and run length are not directly optimized for, but they are shown here for reference and comparison with other layouts. Finger travel is indirectly affected by the heatmap. Run length and fast bigrams are implicitly optimized by the definition of slow bigrams, which penalize non-fast bigrams in the same hand.

First the three most popular English keyboard layouts as a reference to provide context for the values of the metrics in the optimized layouts.

## QWERTY

    [ Q ] [ W ] [ E ] [ R ] [ T ] | [ Y ] [ U ] [ I ] [ O ] [ P ]
     0.3   2.7  20.0  10.2  15.6  |  2.6   4.6  11.7  13.1   3.8
    [ A ] [ S ] [ D ] [ F ] [ G ] | [ H ] [ J ] [ K ] [ L ] [; :]
    12.5  10.2   6.0   4.3   3.2  |  7.8   0.6   1.1   6.8   0.3
    [ Z ] [ X ] [ C ] [ V ] [ B ] | [ N ] [ M ] [, <] [. >] [/ ?]
     0.1   0.2   6.8   1.8   2.2  | 12.1   3.9   2.5   2.9   0.2
    13.0  13.1  32.7  37.3        |       31.5  15.3  22.8   4.3

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.5064 |         |
| Heatmap       | 0.4204 |  0.7115 |
| Bad bigrams   |   5773 | ed:856 ec:639 de:608 ce:469 tr:460 ol:439 lo:390 un:281 rt:178 rf:142 hn:138 ft:131 fr:116 gr:103 ki:84 um:82 hu:74 mu:67 br:58 ju:56 rg:51 my:50 ny:45 ik:33 rv:31 ws:30 nm:28 za:24 nu:22 hy:19 aq:16 sw:11 gt:9 bt:8 az:6 rb:4 nh:4 ym:3 uy:3 hm:2 vg:1 yn:1 uj:1 |
| Slow bigrams  |  23848 |         |
| Fast 3-grams  |     23 | adv:11 fea:9 few:3 |
| Fast bigrams  |   3656 | io:581 as:501 ea:401 we:285 fa:245 oj:228 fe:200 af:191 sa:185 ad:175 va:138 av:129 ef:107 ds:65 ew:54 da:48 jo:30 oi:28 sf:21 lk:14 dv:11 kl:8 lm:6 wf:1 df:1 fw:1 fs:1 km:1 |
| Finger travel |  75173 | 4, 25, 162, 223, 204, 55, 86, 6 |
| Run length    |   1.68 | 1.48    |

The heatmap score for QWERTY is quite bad. It uses the left hand more heavily than the right hand, and some of the most frequently used keys are away from the home row. There are more bad (same-finger) bigrams than fast bigrams in this layout. The index fingers have to travel a lot and so does the left middle finger.

## Dvorak

    [' "] [, <] [. >] [ P ] [ Y ] | [ F ] [ G ] [ C ] [ R ] [ L ]
     0.8   2.5   2.9   3.8   2.6  |  4.3   3.2   6.7  10.2   6.8
    [ A ] [ O ] [ E ] [ U ] [ I ] | [ D ] [ H ] [ T ] [ N ] [ S ]
    12.5  13.0  19.9   4.5  11.7  |  5.9   7.8  15.5  12.1  10.1
    [; :] [ Q ] [ J ] [ K ] [ X ] | [ B ] [ M ] [ W ] [ V ] [ Z ]
     0.3   0.3   0.6   1.0   0.2  |  2.2   3.9   2.7   1.8   0.1
    13.7  15.9  23.4  23.8        |       27.2  25.0  24.1  17.0

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.6169 |         |
| Heatmap       | 0.6117 | 0.9270  |
| Bad bigrams   |   2412 | ct:920 je:233 gh:169 rn:118 up:99 pi:89 ki:84 ip:79 ui:78 ls:71 tw:62 pu:45 mb:43 ik:33 yi:32 xp:31 rv:31 nv:31 dg:28 yp:27 sl:21 tc:16 xi:15 iu:11 py:7 ix:7 uk:4 hd:4 uy:3 gm:3 dm:3 hm:2 oq:1 ej:1 kp:1 ky:1 ku:1 gd:1 df:1 db:1 hf:1 hb:1 mf:1 wt:1 nr:1 |
| Slow bigrams  |   9837 |         |
| Fast 3-grams  |     65 | rch:34 sch:18 nth:8 uea:2 stm:1 ntm:1 hts:1 |
| Fast bigrams  |   7962 | th:2373 nt:892 st:792 ou:514 ea:401 ch:370 ts:314 sh:311 ns:310 cr:212 ke:192 ue:138 hn:138 ua:128 ak:104 ht:97 sc:95 au:87 sm:79 rc:70 ok:62 eo:48 hr:38 ms:36 cs:32 oa:30 nm:28 oe:22 ka:10 sn:9 tm:8 eu:7 nh:4 rh:3 tn:3 uo:2 ek:1 ko:1 hs:1 |
| Finger travel |  57323 | 11, 27, 30, 115, 168, 90, 93, 46 |
| Run length    |   1.23 | 1.39    |

The heatmap and bigram scores are much better than QWERTY. Especially the per-finger heatmap is very good. Also finger travel is much reduced. Only the right index finger still travels much more than other fingers.

Dvorak is optimized for alternating hands between keystokes. This is proven by the short average run length and the much lower score of slow bigrams.

Dvorak nearly tripples the number of fast 3-grams, though that number is still very small in absolute terms.

## Colemak

    [ Q ] [ W ] [ F ] [ P ] [ G ] | [ J ] [ L ] [ U ] [ Y ] [; :]
     0.3   2.7   4.3   3.8   3.2  |  0.6   6.8   4.6   2.6   0.3
    [ A ] [ R ] [ S ] [ T ] [ D ] | [ H ] [ N ] [ E ] [ I ] [ O ]
    12.5  10.2  10.2  15.6   6.0  |  7.8  12.1  20.0  11.7  13.1
    [ Z ] [ X ] [ C ] [ V ] [ B ] | [ K ] [ M ] [, <] [. >] [/ ?]
     0.1   0.2   6.8   1.8   2.2  |  1.1   3.9   2.5   2.9   0.2
    13.0  13.1  21.2  32.5        |       32.3  27.1  17.2  13.6

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.6668 |         |
| Heatmap       | 0.7342 | 0.8797  |
| Bad bigrams   |    828 | hn:138 ue:138 sc:95 kn:47 pt:46 nk:45 cs:32 nl:32 yi:32 dg:28 nm:28 za:24 sf:21 aq:16 lk:14 dv:11 rw:10 gt:9 bt:8 kl:8 eu:7 az:6 lm:6 nh:4 wr:3 tp:3 pb:2 td:2 ln:2 hm:2 fs:1 pg:1 pd:1 gd:1 dp:1 db:1 vg:1 kh:1 km:1 |
| Slow bigrams  |  13156 |         |
| Fast 3-grams  |    604 | tra:172 aft:104 ien:86 oun:79 art:59 ars:32 ast:30 rst:17 oin:13 nio:6 arv:2 nei:2 neo:1 meo:1 |
| Fast bigrams  |  15410 | in:1658 on:1421 en:1130 at:1107 st:792 me:669 io:581 ar:559 ou:514 as:501 ra:500 tr:460 rs:447 no:443 ne:419 ta:368 ts:314 om:313 im:284 un:281 ie:273 em:252 fa:245 ni:241 mo:209 af:191 sa:185 rt:178 va:138 mi:136 ft:131 av:129 ei:73 tw:62 eo:48 ny:45 rv:31 oi:28 oe:22 nu:22 uy:3 uo:2 wf:1 wt:1 fw:1 sr:1 yn:1 |
| Finger travel |  57648 | 4, 26, 96, 168, 167, 71, 49, 5 |
| Run length    |   1.38 | 1.62    |

Colemak brings a further improvement in the heatmap score although the per-finger heatmap is slightly worse. The index and middle fingers are weighted most heavily. On top of the improvements in Dvorak, Colemak brings another big improvement of bad bigrams by factor 3 and fast bigrams by factor 2.

Colemak has more slow bigrams than Dvorak, which goes along with a longer average run length. Total finger travel is about the same as in Dvorak, but more evenly distributed to both hands. Both index fingers still travel a lot.

Colemak has nearly 10 times as many fast 3-grams as Dvorak and over 25 times as many as QWERTY.

## REAT

    [ Z ] [. >] [ O ] [ K ] [ Q ] | [ J ] [ W ] [ L ] [ U ] [ X ]
     0.1   2.9  13.0   1.0   0.3  |  0.6   2.7   6.8   4.5   0.2
    [ R ] [ E ] [ A ] [ T ] [, <] | [ F ] [ C ] [ N ] [ I ] [ S ]
    10.2  19.9  12.5  15.5   2.5  |  4.3   6.7  12.1  11.7  10.1
    [ H ] [; :] [' "] [ D ] [ B ] | [ P ] [ G ] [ M ] [ Y ] [ V ]
     7.8   0.3   0.8   5.9   2.2  |  3.8   3.2   3.9   2.6   1.8
    18.1  23.2  26.4  27.5        |       21.3  22.7  18.8  12.1

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.7416 |         |
| Heatmap       | 0.9285 | 0.9191  |
| Bad bigrams   |    288 | ui:78 hr:38 nl:32 yi:32 oa:30 nm:28 iu:11 bt:8 lm:6 rh:3 tk:3 pf:3 uy:3 td:2 wp:2 ln:2 o':1 a':1 'a:1 db:1 wf:1 fw:1 pg:1 |
| Slow bigrams  |   7841 |         |
| Fast 3-grams  |   2391 | ing:567 hat:295 tor:295 ter:203 der:145 sin:114 red:82 rea:73 eat:61 had:55 rat:51 inc:51 sig:49 ead:45 hea:43 gis:38 hed:28 vin:28 gni:24 clu:19 rot:17 rad:17 giv:14 dar:13 niv:12 ret:10 tar:10 sic:7 vic:7 nis:7 cis:5 het:4 civ:2 |
| Fast bigrams  |  24607 | th:2373 he:2172 in:1658 er:1566 re:1239 at:1107 or:1105 to:881 ed:856 te:848 is:763 ng:749 ro:715 ha:640 de:608 ar:559 ra:500 tr:460 ic:405 si:403 ea:401 nc:396 ta:368 uc:310 ns:310 et:279 ot:272 iv:242 ni:241 ig:231 ul:207 rt:178 ad:175 ci:151 vi:150 cu:125 gi:105 cl:101 ht:97 sc:95 lu:87 rd:79 ls:71 eh:64 da:48 gn:47 dr:38 cs:32 gs:32 nv:31 sl:21 sn:9 hd:4 ah:1 sg:1 vg:1 |
| Finger travel |  57505 | 49, 27, 86, 117, 126, 90, 69, 19 |
| Run length    |   1.67 | 1.48    |
| Times found   |     18 |         |

This is the highest scoring solution found by the annealing algorithm on this text sample. It was also the most frequently found one with 18 times out of 247 program runs.

The overall score is a further improvement on Colemak. Looking at individual metrics, the improvements are quite dramatic. The heatmap score is nearly perfect, which only shows that this had a high weight in the overall score. Comparing this directly to existing layouts like Colemak is not really fair given that they may have been optimized for a different choice of key weights.

The bad bigrams score, on the other hand, is very objective. It is nearly factor 3 better than Colemak and more than factor 8 better than Dvorak. Fast bigrams are improved, but Colemak was already quite good at that. Where this layout really distinguishes itself from previous layouts is in the fast 3-gram metric, where it scores almost a factor 4 higher than Colemak and factor 36 higher than Dvorak.

The slow bigram number is smaller than Dvorak. However that does not translate directly to a shorter average run length. This has to be expected, given that this layout has much more fast bigrams and 3-grams in the same hand. The average run length is even slightly higher than in Colemak.

Overall finger travel distance is similar to Colemak and Dvorak. However, it is more evenly distributed with significantly less travel for the index fingers.

The remaining layouts in this section have slightly lower overall scores than this one. However, analyzing them allows some insight into the trade-offs made by the algorithm and highlights different strategies found by the simulated annealing algorithm to optimize for the multi-objective quality function.

## NEOI

    [ Z ] [' "] [ A ] [, <] [ X ] | [ J ] [ B ] [ R ] [ M ] [ V ]
     0.1   0.8  12.5   2.5   0.2  |  0.6   2.2  10.2   3.9   1.8
    [ N ] [ E ] [ O ] [ I ] [. >] | [ D ] [ C ] [ H ] [ T ] [ S ]
    12.1  19.9  13.0  11.7   2.9  |  5.9   6.7   7.8  15.5  10.1
    [ P ] [; :] [ Q ] [ U ] [ Y ] | [ W ] [ F ] [ L ] [ K ] [ G ]
     3.8   0.3   0.3   4.5   2.6  |  2.7   4.3   6.8   1.0   3.2
    16.0  21.1  25.8  24.4        |       22.4  24.8  20.4  15.1

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.7337 |         |
| Heatmap       | 0.8549 | 0.9703  |
| Bad bigrams   |    330 | ui:78 hr:38 yi:32 gs:32 oa:30 rl:25 aq:16 xi:15 iu:11 tm:8 np:7 ix:7 e':5 bj:4 uy:3 bc:3 rh:3 tk:3 oq:1 db:1 df:1 wb:1 wf:1 fw:1 lr:1 km:1 vg:1 sg:1 |
| Slow bigrams  |   5207 |         |
| Fast 3-grams  |    892 | ion:550 ien:86 cts:61 fts:59 peo:38 uen:27 ian:19 nou:9 gth:9 nai:8 neu:7 poi:7 noi:3 nei:2 eou:2 stc:2 neo:1 thf:1 hts:1 |
| Fast bigrams  |  17578 | th:2373 in:1658 an:1561 on:1421 en:1130 ct:920 st:792 io:581 ou:514 rs:447 no:443 pe:428 ne:419 ch:370 ts:314 sh:311 na:307 un:281 ie:273 po:271 rm:256 ia:254 ni:241 ai:216 cr:212 gh:169 op:154 ue:138 ft:131 ep:127 up:99 ht:97 sc:95 pi:89 ip:79 ei:73 rc:70 eo:48 pu:45 cs:32 oi:28 nu:22 oe:22 sf:21 tc:16 gt:9 eu:7 i':6 uo:2 'a:1 a':1 sr:1 hf:1 fs:1 hs:1 |
| Finger travel |  57979 | 34, 11, 81, 120, 125, 121, 47, 48 |
| Run length    |   1.42 | 1.31    |
| Times found   |      1 |         |

This layout shows a heavy emphasis on a small number of slow bigrams. In turn it sacrifices on most of the other metrics while still attaining a fairly good overall score.

It emulates the strategy of the Dvorak layout to move all vowels to the same (left) hand. Similar to Dvorak, all the punctuation symbols are also in the same hand. However, unlike Dvorak it does not place all vowels in the home row. There are many other differences. One interesting and counter-intuitive optimization is the placement of "H" and "R". The heatmap would prefer "R" in the home row and "H" above. However, that would break the "TH" fast bigram.

The slow bigram score is close to half that of Dvorak's. As a result this layout gets close to Dvorak's very low average run length while still achieving a significantly higher number fast bigrams (~2x) and 3-grams (~14x).

Compared to REAT, it has slightly more bad bigrams. More significantly, it achieves only a little more than 1/3 the number of fast 3-grams and 2/3 the number of fast bigrams. These scores are still significantly better than Dvorak and Colemak.

## SINC

    [ X ] [ U ] [ L ] [ W ] [ J ] | [ Z ] [ Q ] [ R ] [ O ] [; :]
     0.2   4.5   6.8   2.7   0.6  |  0.1   0.3  10.2  13.0   0.3
    [ S ] [ I ] [ N ] [ C ] [ F ] | [ B ] [ T ] [ H ] [ A ] [ E ]
    10.1  11.7  12.1   6.7   4.3  |  2.2  15.5   7.8  12.5  19.9
    [ V ] [ Y ] [ M ] [ G ] [ P ] | [ K ] [ D ] [. >] [' "] [, <]
     1.8   2.6   3.9   3.2   3.8  |  1.0   5.9   2.9   0.8   2.5
    12.1  18.8  22.7  21.3        |       25.1  20.9  26.4  22.8

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.7392 |         |
| Heatmap       | 0.9255 | 0.8751  |
| Bad bigrams   |    288 | ui:78 hr:38 yi:32 nl:32 oa:30 nm:28 iu:11 bt:8 lm:6 uy:3 pf:3 tk:3 rh:3 ln:2 wp:2 td:2 wf:1 fw:1 pg:1 db:1 o':1 a':1 'a:1 |
| Slow bigrams  |   9017 |         |
| Fast 3-grams  |   3055 | the:1579 ing:567 tha:276 sin:114 ort:81 eat:61 inc:51 sig:49 ead:45 gis:38 vin:28 tre:25 gni:24 tro:24 ert:20 clu:19 giv:14 niv:12 sic:7 vic:7 nis:7 cis:5 civ:2 |
| Fast bigrams  |  23431 | th:2373 he:2172 in:1658 er:1566 re:1239 at:1107 or:1105 to:881 ed:856 te:848 is:763 ng:749 ro:715 ha:640 de:608 tr:460 ic:405 si:403 ea:401 nc:396 ta:368 uc:310 ns:310 et:279 ot:272 iv:242 ni:241 ig:231 ul:207 rt:178 ad:175 ci:151 vi:150 cu:125 gi:105 cl:101 ht:97 sc:95 lu:87 ls:71 eh:64 da:48 gn:47 cs:32 gs:32 nv:31 sl:21 sn:9 hd:4 sg:1 vg:1 ah:1 |
| Finger travel |  57979 | 19, 69, 90, 126, 91, 79, 86, 29 |
| Run length    |   1.48 | 1.67    |
| Times found   |     13 |         |

This is the third-most popular solution found by the algorithm and the third-highest overall score. It puts the emphasis on the fast 3-gram score, which is about 28% higher than in the REAT layout and more than 3x that of NEOI. This is mostly thanks to making "the" a fast trigram. This requires some compromises, which negatively affect other scores.

In this solution, placing "E" on the right pinky finger negatively affects the heatmap score. This is most pronounced in the finger heatmap score. In fact, since the "the" 3-gram has such a big impact, it was important to weigh the heat map metrics strong enough in the quality function for this type of solution not to become overwhelmingly popular.

## EAHT

    [; :] [ O ] [ R ] [ Q ] [ Z ] | [ J ] [ W ] [ P ] [ U ] [ X ]
     0.3  13.0  10.2   0.3   0.1  |  0.6   2.7   3.8   4.5   0.2 
    [ E ] [ A ] [ H ] [ T ] [. >] | [ F ] [ C ] [ N ] [ I ] [ S ]
    19.9  12.5   7.8  15.5   2.9  |  4.3   6.7  12.1  11.7  10.1 
    [, <] [' "] [ L ] [ D ] [ K ] | [ M ] [ G ] [ B ] [ Y ] [ V ]
     2.5   0.8   6.8   5.9   1.0  |  3.9   3.2   2.2   2.6   1.8 
    22.8  26.4  24.8  25.8        |       21.3  18.1  18.8  12.1 

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.7380 |         |
| Heatmap       | 0.9137 | 0.8648  |
| Bad bigrams   |    246 | ui:78 hr:38 yi:32 oa:30 rl:25 iu:11 np:7 rh:3 tk:3 gm:3 uy:3 td:2 pb:2 bn:2 o':1 a':1 'a:1 lr:1 wf:1 fw:1 mf:1 |
| Slow bigrams  |  10263 |         |
| Fast 3-grams  |   3036 | the:1579 ing:567 tha:276 sin:114 ort:81 eat:61 inc:51 sig:49 ead:45 gis:38 vin:28 tre:25 tro:24 gni:24 ert:20 giv:14 niv:12 sic:7 vic:7 nis:7 cis:5 civ:2 |
| Fast bigrams  |  23254 | th:2373 he:2172 in:1658 er:1566 re:1239 at:1107 or:1105 to:881 ed:856 te:848 is:763 ng:749 ro:715 ha:640 de:608 tr:460 ic:405 si:403 ea:401 nc:396 ta:368 uc:310 ns:310 et:279 ot:272 iv:242 ni:241 ig:231 rt:178 ad:175 ci:151 vi:150 sp:133 cu:125 gi:105 up:99 ht:97 sc:95 eh:64 da:48 gn:47 pu:45 ps:33 cs:32 gs:32 nv:31 sn:9 hd:4 ah:1 sg:1 vg:1 |
| Finger travel |  58803 | 29, 86, 121, 91, 126, 56, 69, 19 |
| Run length    |   1.77 | 1.42    |
| Times found   |      8 |         |

This is a mirrored variant of SINC with a nearly identical home row. However, this solution emphasizes a small bad bigrams score. This is the smallest number of bad bigrams of any solution found.

The major compromise to achieve this seems to be the increase of slow bigrams. There is also an increase in finger travel for the left middle finger (compared to the right middle finger in SINC).

## SNIC

    [ X ] [ B ] [ U ] [ V ] [ J ] | [ Z ] [ Q ] [ H ] [ A ] [; :]
     0.2   2.2   4.5   1.8   0.6  |  0.1   0.3   7.8  12.5   0.3 
    [ S ] [ N ] [ I ] [ C ] [ F ] | [. >] [ T ] [ R ] [ O ] [ E ]
    10.1  12.1  11.7   6.7   4.3  |  2.9  15.5  10.2  13.0  19.9 
    [ G ] [ P ] [ Y ] [ D ] [ W ] | [ K ] [ M ] [ L ] [' "] [, <]
     3.2   3.8   2.6   5.9   2.7  |  1.0   3.9   6.8   0.8   2.5 
    13.5  18.1  18.8  22.0        |       23.7  24.8  26.4  22.8 

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.7377 |         |
| Heatmap       | 0.9183 | 0.8747  |
| Bad bigrams   |    294 | ui:78 hr:38 gs:32 yi:32 oa:30 rl:25 iu:11 dv:11 tm:8 np:7 uy:3 tk:3 rh:3 bn:2 pb:2 sg:1 fw:1 df:1 wf:1 km:1 lr:1 a':1 o':1 'a:1 |
| Slow bigrams  |   9511 |         |
| Fast 3-grams  |   3158 | the:1579 ing:567 tha:276 orm:173 ort:81 erm:66 suc:62 din:56 cub:55 ins:37 sid:26 tre:25 gni:24 tro:24 ert:20 dis:19 nic:17 cin:14 buc:9 sic:7 gic:6 cus:6 cis:5 dig:2 eor:2 |
| Fast bigrams  |  24746 | th:2373 he:2172 in:1658 er:1566 re:1239 at:1107 or:1105 nd:1091 to:881 te:848 is:763 ng:749 ro:715 me:669 ha:640 tr:460 us:431 ic:405 si:403 nc:396 ta:368 om:313 uc:310 ns:310 et:279 ot:272 rm:256 em:252 su:247 ni:241 di:238 ig:231 bu:211 mo:209 id:179 rt:178 ci:151 cu:125 gi:105 ht:97 sc:95 ub:83 ds:65 eh:64 eo:48 gn:47 cs:32 dg:28 oe:22 sn:9 dn:5 bc:3 gd:1 ah:1 |
| Finger travel |  57825 | 31, 56, 69, 123, 76, 116, 87, 29 |
| Run length    |   1.45 | 1.79    |
| Times found   |     14 |         |

This is the second-most popular solution, though somewhat lower on the overall score ranking. This is another one with "the" as a fast 3-gram. It's scores are quite similar to SINC.

## EORT

    [; :] [ A ] [ H ] [ K ] [ Q ] | [ Z ] [ W ] [ U ] [ L ] [ X ]
     0.3  12.5   7.8   1.0   0.3  |  0.1   2.7   4.5   6.8   0.2
    [ E ] [ O ] [ R ] [ T ] [ B ] | [ F ] [ C ] [ I ] [ N ] [ S ]
    19.9  13.0  10.2  15.5   2.2  |  4.3   6.7  11.7  12.1  10.1
    [, <] [' "] [. >] [ P ] [ V ] | [ M ] [ D ] [ Y ] [ J ] [ G ]
     2.5   0.8   2.9   3.8   1.8  |  3.9   5.9   2.6   0.6   3.2
    22.8  26.4  20.9  24.6        |       23.6  18.8  19.5  13.5

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.7379 |         |
| Heatmap       | 0.9612 | 0.8734  |
| Bad bigrams   |    335 | ui:78 pt:46 hr:38 yi:32 nl:32 gs:32 oa:30 iu:11 bt:8 rh:3 tk:3 tp:3 dm:3 uy:3 pb:2 ln:2 a':1 o':1 'a:1 kp:1 wf:1 fw:1 mf:1 df:1 sg:1 |
| Slow bigrams  |   9478 |         |
| Fast 3-grams  |   3397 | the:1579 ing:567 pro:426 tha:276 ort:81 suc:62 din:56 pre:53 eop:38 ins:37 sid:26 tre:25 tro:24 gni:24 ert:20 dis:19 nic:17 cin:14 cul:12 erp:10 sic:7 gic:6 cus:6 cis:5 eor:2 luc:2 dig:2 orp:1 |
| Fast bigrams  |  24684 | th:2373 he:2172 in:1658 er:1566 re:1239 at:1107 or:1105 nd:1091 to:881 te:848 is:763 ng:749 ro:715 ha:640 pr:544 tr:460 us:431 pe:428 ic:405 si:403 nc:396 ta:368 uc:310 ns:310 et:279 ot:272 po:271 su:247 ni:241 di:238 ig:231 ul:207 id:179 rt:178 op:154 ci:151 ep:127 cu:125 gi:105 cl:101 ht:97 sc:95 lu:87 ds:65 eh:64 eo:48 gn:47 cs:32 dg:28 oe:22 rp:15 sn:9 dn:5 ah:1 gd:1 |
| Finger travel |  57195 | 29, 87, 76, 95, 137, 69, 56, 31 |
| Run length    |   1.73 | 1.51    |
| Times found   |      5 |         |

This is a mirrored variant of SNIC with a nearly identical home row. It has a better key heatmap score and slightly more fast 3-grams, but also more bad bigrams (mostly due to "pt" and "nl"). The right index finger needs to travel more.

## CAIN

    [; :] [ F ] [ H ] [ J ] [ Q ] | [ Z ] [ W ] [ O ] [ U ] [ X ]
     0.3   4.3   7.8   0.6   0.3  |  0.1   2.7  13.0   4.5   0.2
    [ E ] [ S ] [ R ] [ T ] [ G ] | [ P ] [ C ] [ A ] [ I ] [ N ]
    19.9  10.1  10.2  15.5   3.2  |  3.8   6.7  12.5  11.7  12.1
    [' "] [ V ] [ L ] [ M ] [ K ] | [. >] [ D ] [, <] [ Y ] [ B ]
     0.8   1.8   6.8   3.9   1.0  |  2.9   5.9   2.5   2.6   2.2
    21.1  16.2  24.8  24.5        |       22.2  28.0  18.8  14.4

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.7359 |         |
| Heatmap       | 0.9253 | 0.9093  |
| Bad bigrams   |    283 | ui:78 hr:38 yi:32 oa:30 rl:25 sf:21 iu:11 gt:9 tm:8 e':5 rh:3 tk:3 gm:3 kg:3 uy:3 wp:2 nx:2 bn:2 fs:1 lr:1 km:1 pd:1 dp:1 |
| Slow bigrams  |   9926 |         |
| Fast 3-grams  |   2481 | the:1579 con:364 can:99 erm:66 ain:62 est:60 cou:59 din:56 tre:25 ert:20 rse:18 nic:17 bac:17 cin:14 mse:6 tse:4 ts':3 bia:2 dai:2 dan:2 thf:1 noc:1 nia:1 nad:1 bid:1 bad:1 |
| Fast bigrams  |  25674 | th:2373 he:2172 in:1658 er:1566 an:1561 on:1421 re:1239 nd:1091 es:861 te:848 st:792 co:717 me:669 ac:521 ou:514 se:486 tr:460 rs:447 no:443 ca:428 ic:405 nc:396 ts:314 uc:310 na:307 et:279 rm:256 ia:254 em:252 ni:241 di:238 ai:216 ab:194 id:179 rt:178 ad:175 ci:151 ft:131 cu:125 ba:122 oc:113 bi:101 ht:97 sm:79 eh:64 's:61 da:48 ib:37 ms:36 t':15 r':10 't:5 dn:5 s':3 bc:3 uo:2 sr:1 'r:1 'm:1 hf:1 db:1 |
| Finger travel |  58862 | 11, 54, 116, 90, 123, 109, 69, 23 |
| Run length    |   1.68 | 1.63    |
| Times found   |      7 |         |

Yet another approach to the "the" fast 3-gram. This one achieves surprisingly good finger heatmap and bad bigrams scores quite close to REAT. Even though it adds the "the" fast 3-gram, its fast 3-gram score is not much higher than REAT. However, the overall score is negatively affected by a significantly increased number of slow bigrams.

## NIAC

    [ Z ] [ U ] [ O ] [ V ] [ X ] | [ Q ] [ J ] [ H ] [ G ] [; :]
     0.1   4.5  13.0   1.8   0.2  |  0.3   0.6   7.8   3.2   0.3
    [ N ] [ I ] [ A ] [ C ] [. >] | [ B ] [ T ] [ R ] [ S ] [ E ]
    12.1  11.7  12.5   6.7   2.9  |  2.2  15.5  10.2  10.1  19.9
    [ P ] [ Y ] [, <] [ M ] [ W ] | [ K ] [ D ] [ L ] [ F ] [' "]
     3.8   2.6   2.5   3.9   2.7  |  1.0   5.9   6.8   4.3   0.8
    16.0  18.8  28.0  18.1        |       25.6  24.8  17.6  21.1

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.7356 |         |
| Heatmap       | 0.9138 | 0.8958  |
| Bad bigrams   |    318 | ui:78 hr:38 yi:32 gs:32 oa:30 rl:25 sf:21 xc:12 iu:11 bt:8 np:7 e':5 bj:4 uy:3 tk:3 rh:3 td:2 db:1 lr:1 sg:1 fs:1 |
| Slow bigrams  |   9590 |         |
| Fast 3-grams  |   2935 | the:1579 con:364 man:294 can:99 ght:94 ain:62 est:60 cou:59 min:57 pac:53 cap:47 tre:25 ert:20 rse:18 nic:17 cin:14 dre:13 mai:12 nim:10 cip:10 pic:9 nam:6 tse:4 ts':3 erd:2 noc:1 nia:1 iam:1 map:1 |
| Fast bigrams  |  25714 | th:2373 he:2172 in:1658 er:1566 an:1561 on:1421 re:1239 es:861 ed:856 te:848 st:792 co:717 de:608 ac:521 ou:514 se:486 ma:471 tr:460 rs:447 no:443 ca:428 ic:405 nc:396 ts:314 uc:310 na:307 im:284 et:279 mp:261 ia:254 ni:241 ai:216 rt:178 ap:173 gh:169 pa:158 ci:151 am:136 mi:136 cu:125 oc:113 ht:97 pi:89 ip:79 rd:79 ds:65 eh:64 's:61 dr:38 nm:28 pm:20 t':15 r':10 gt:9 't:5 s':3 uo:2 sr:1 'r:1 |
| Finger travel |  58610 | 34, 69, 109, 90, 96, 116, 68, 11 |
| Run length    |   1.63 | 1.66    |
| Times found   |      2 |         |

This is a mirrored variant of cain with a nearly identical home row. It achieves significantly more fast 3-grams and fewer slow bigrams, but compromises on the heatmap and bad bigrams.

## TEAR

    [ K ] [. >] [ O ] [ Q ] [ Z ] | [ J ] [ W ] [ U ] [ B ] [ X ]
     1.0   2.9  13.0   0.3   0.1  |  0.6   2.7   4.5   2.2   0.2
    [ T ] [ E ] [ A ] [ R ] [ L ] | [ F ] [ C ] [ I ] [ N ] [ S ]
    15.5  19.9  12.5  10.2   6.8  |  4.3   6.7  11.7  12.1  10.1
    [ V ] [; :] [' "] [ H ] [, <] | [ M ] [ D ] [ Y ] [ P ] [ G ]
     1.8   0.3   0.8   7.8   2.5  |  3.9   5.9   2.6   3.8   3.2
    18.3  23.2  26.4  27.7        |       24.1  18.8  18.1  13.5

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Overall score | 0.7384 |         |
| Heatmap       | 0.8908 | 0.9130  |
| Bad bigrams   |    278 | ui:78 hr:38 yi:32 gs:32 oa:30 rl:25 iu:11 np:7 tk:3 rh:3 dm:3 uy:3 bn:2 pb:2 o':1 a':1 'a:1 lr:1 wf:1 fw:1 mf:1 df:1 sg:1 |
| Slow bigrams  |   8377 |         |
| Fast 3-grams  |   2357 | ing:567 tor:295 hat:295 ver:252 ter:203 ear:102 hav:87 var:73 suc:62 din:56 cub:55 rat:51 ins:37 sid:26 gni:24 tea:19 dis:19 rev:18 rot:17 nic:17 cin:14 tar:10 ret:10 buc:9 sic:7 gic:6 cus:6 rav:5 cis:5 vea:4 het:4 dig:2 |
| Fast bigrams  |  25605 | th:2373 he:2172 in:1658 er:1566 re:1239 at:1107 or:1105 nd:1091 to:881 te:848 is:763 ng:749 ro:715 ve:677 ha:640 ar:559 ra:500 tr:460 us:431 ic:405 si:403 ea:401 nc:396 ta:368 uc:310 ns:310 et:279 ot:272 su:247 ni:241 di:238 ig:231 bu:211 ev:193 id:179 rt:178 ci:151 va:138 av:129 cu:125 gi:105 ht:97 sc:95 ub:83 ds:65 eh:64 gn:47 cs:32 rv:31 dg:28 sn:9 dn:5 bc:3 ah:1 gd:1 |
| Finger travel |  56227 | 30, 27, 86, 127, 144, 69, 56, 3 |
| Run length    |   1.76 | 1.46    |
| Times found   |      2 |         |

It all ends in tears. (Sorry, I had to.)

I included this one as another example of not having "the" as a fast 3-gram, which makes it similar to REAT. The right hand looks similar to SINC, EAHT and REAT.

The fast 3-gram score is slightly lower than REAT. The major compromise seems to be the lower key heatmap score and the bigger number of slow bigrams.

The total finger travel distance is one of the lowest seen among all solutions. However, it is unevenly distributed with more travel for the right index finger.

## Statistics

### Overall score distribution

       |                                            #                   
       |                                            #                   
       |                                            #                   
       |                                            #     #             
     25+                                            #     #             
       |                                            #     #             
       |                                            #     #             
       |                                            #     #             
       |                                            #     #             
     20+                                            #     #             
       |                                            #     #             
       |                                            #     #            #
       |                                            #     #            #
       |                                            #     #            #
     15+                                            #     #            #
       |                                            #     #            #
       |                                            #     #    #       #
       |                                            #     #    #       #
       |                               #            #     # #  #       #
     10+                               #            #     # ## #       #
       |                               #       #    #     #### #       #
       |                               #     # # #  #     #### #       #
       |                               #     ### #  #     #### #       #
       |                               ##    ### ## #     #### #       #
      5+                               ##    ### ## ##  # #### #       #
       |                       #  #### ##  # ### ###### # #### #       #
       |                       #  ######## ##### ###### # #### #       #
       |             #  #   ####  ######## ############ # #### #       #
       |#    #  #   ############ ######################## #### #      ##
        +---------+---------+---------+---------+---------+---------+---------
      0.723     0.726     0.729     0.732     0.735     0.738     0.741   

### Heatmap score distribution

     25+                                  #              
       |                                  #              
       |                                  #              
       |                                  #              
       |                                # ##             
     20+                                # ##             
       |                                # ##             
       |                                # ##             
       |                                # ##             
       |                          #     # ##             
     15+                          #   # # ##             
       |                          #   # # ##             
       |                          #   # #####     #      
       |                          #   # #####     #      
       |                          # # # #####     #      
     10+                         ## # # #####     #      
       |                         ## # # #####     #      
       |                    # #  ## # #######     #      
       |                    # #  ## # ####### ##  #      
       |                    # #  #### ####### ##  #      
      5+                    # #  #### ####### ##  #   #  
       |            # #     ###  #### ####### ## ##   #  
       |          # # #     ###  #### ########## ###  #  
       |     ##   # # #     #### ###################  #  
       |#    ###  # ###  #  #### ###################  # #
        +---------+---------+---------+---------+---------
      0.822     0.852     0.882     0.912     0.942   

### Bad bigrams distribution

       |       #                                                          
       |       #                                                          
     45+       #                                                          
       |       #                                                          
       |       #                                                          
       |       #                                                          
       |       #                                                          
     40+       #                                                          
       |       #                                                          
       |       #                                                          
       |       #                                                          
       |       #                                                          
     35+       #                                                          
       |       #                                                          
       |       #                                                          
       |       #                                                          
       |       #                                                          
     30+       #                                                          
       |       #                                                          
       |       #                                                          
       |       #                                                          
       |       #                                                          
     25+       #                                                          
       |       #                                                          
       |       #                                                          
       |       #                                                          
       |       #                                                          
     20+       #                                                          
       |       #                                                          
       |       ##       #                                                 
       |       ##       #                                                 
       |       ##       #                                                 
     15+       ##       #                                                 
       |#      ##       #   #                                             
       |#      ##       #   #                                             
       |#      ##       #   #                                             
       |#     ###     # #   #       #                                     
     10+#     ###     # #   #       #                                     
       |#     ###   # # #   #       #                                     
       |#     ###  ## # #   #       #                                     
       |#   # ###  ## # #   #       #                                     
       |#   # #### ## # #   #       #                                     
      5+#   ###### ## # #   # ##   ##                                     
       |#   #############  ## ###  ##    #                                
       |#   ############## ##########    #                                
       |#   ######################### # ##     #                          
       |##################################  # ##  #                      #
        +---------+---------+---------+---------+---------+---------+---------
        246       306       366       426       486       546       606   

### Fast bigrams distribution

       |                                             #            
       |                                             #            
       |                                             #            
       |                                             #            
     55+                                             #            
       |                                             #            
       |                                             #            
       |                                             #            
       |                                             #            
     50+                                             #            
       |                                             #            
       |                                             #            
       |                                             #            
       |                                             #            
     45+                                             #            
       |                                             #            
       |                                             #            
       |                                             #            
       |                                             #            
     40+                                             #            
       |                                             #            
       |                                             #            
       |                                             #            
       |                                             #            
     35+                                             #            
       |                                             #            
       |                                             #            
       |                                             #            
       |                                        #    #            
     30+                                        #    #            
       |                                        #    #            
       |                                        #    #            
       |                                        #    #            
       |                                        #    #            
     25+                                        #    #            
       |                                        #    #            
       |                                        #    ##           
       |                                        #    ##           
       |                                        #    ##           
     20+                                        #    ##           
       |                                        #    ##  #        
       |                                        #    ##  #        
       |                                        #    ##  #        
       |                                        #    ### #        
     15+                                        #    ### #        
       |                                        #    ### #        
       |                                        #    ### #  #     
       |                                        #    ### #  #     
       |                                        #   #### #  #     
     10+                                        #   #### #  #     
       |                                        # # #### #  #     
       |                                       ## # ######  #     
       |                                     # ## # ###### ##     
       |                                     # ## # ###### ##     
      5+                                   # #### ######## ##     
       |                                   # #### ######## ##     
       |                  #                # #### ######## ##     
       |#                 #       ##    ## # ############# ##     
       |#                ###      ##    ## ###################   #
        +---------+---------+---------+---------+---------+---------
      13250     15750     18250     20750     23250     25750   

### Slow bigrams distribution

       |                                  #                             
       |                                  #                             
       |                                  #                             
       |                                  #  #                          
     25+                                  #  #                          
       |                                  #  #                          
       |                          #       #  #                          
       |                          #       #  #                          
       |                          #       #  #                          
     20+                          #       #  #                          
       |                          #       #  #                          
       |                          #       #  #                          
       |                          #       #  #                          
       |                          #       #  #                          
     15+                          #       #  #                          
       |                          #       #  #                          
       |                          #       #  #  #                       
       |                         ##       #  #  ##                      
       |                         ##       #  #  ##                      
     10+                         ##       #  #  ###                     
       |                         ###      #  #  ###                     
       |                  #      ###     ### #  ####                    
       |                  #      ###     ### #  ####                    
       |                  #      ### # # ### #  ####                    
      5+                  #      ### # # ### #  ####                    
       |           #      #    ####### # ### #  ####                    
       |           #    # #### ####### ############# ##                 
       |      # ## #    ############## ################ #            #  
       |#    ## ## #   ##################################  #         # #
        +---------+---------+---------+---------+---------+---------+---------
       3900      5400      6900      8400      9900     11400     12900   

### Fast 3-grams distribution

       |                                             #                    
       |                                             #                    
       |                                #            #                    
     20+                                #            ##                   
       |                                #            ##  #                
       |                                #            ##  #                
       |                                #            ##  #                
       |                                #            ## ##                
     15+                                #            ## ##                
       |                                #            ## ##                
       |                                #            ## ##                
       |                                #            ## ##                
       |                                #            ## ##                
     10+                                #            ## ##       #        
       |                                #          # ## ## ##    #        
       |                                # #        # ## ## ##    #        
       |                                # #        # ## ## ##    #        
       |                                # #     # ## ## ## ##    #        
      5+                                # #     # ## ## ## ##    #    #   
       |  #                           #####     # ## ## #####   ##   ##   
       |  #                 # #   # ########### # ## ## #####   ##  ###   
       |# #         ##    ### #  ## ########### #### ######## # ##  ###  #
       |# ## # #    ###  #### # ### ########### #### ######## # ## ##### #
        +---------+---------+---------+---------+---------+---------+---------
        750      1250      1750      2250      2750      3250      3750   

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
[11] [A fast, compliant alternative implementation of Python](https://www.pypy.org/)