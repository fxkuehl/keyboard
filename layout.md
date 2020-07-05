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

In order to quantify how good or bad a keyboard layout is, a quality function is needed. That function assigns a numerical value to the potential speed and comfort of typing a specific benchmark text. Computing the function for different keyboard layouts will give different results. Computing the function for different texts will also give different results. Texts written in the same language should give similar results.

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

Weights can be used to express how common the use of a particular key should be. Given a probability distribution of characters in a text, each character probability can be multiplied with its corresponding key weight using a given keyboard layout. A keyboard layout optimized for comfort would maximize the weighted sum. This can also be expressed as a dot-product.

The character probabilities in the input text can be calculated ahead of time. The dot-product has O(1) effort with respect to the size of the input text.

The result of the dot-product should be scaled to the common value range 0 to 1. The lowest possible dot-product should map to 0, the highest to 1. The lowest possible value can be calculated by assigning the most frequent characters to the lowest weighted keys in order and calculating the resulting dot-product. Conversely the highest possible value can be calculated by assigning the most frequent characters to the highest weighted keys. The actual score can be scaled linearly within this range.

The choice of key weights is a tuneable quality function parameter (or rather a vector of 30 parameters). To get ambidextrous keyboard layouts, those weights should be symmetric between the left and right hand, which effectively reduces the number of parameters to 15.

### Good and bad bigrams

The set of all potential bigrams (2-symbol sequences) can be determined from the input text, and the probability or frequency of each bigram can be stored in a lookup table.

From the keyboard layout a set of good and bad bigrams can be generated. Good bigrams are those, which are particularly comfortable or fast to type. Rolling motions from finger to finger without having to stretch uncomfortably should be favoured by the optimal keyboard layout. For example the sequence "EF" on the QWERTY layout would be a good bigram.

Bad bigrams are those, which use the same finger to type different letters. For example the sequence "RT" on the QWERTY layout would be bad. Furthermore, sequences that use different fingers but skip between the top and the bottom row, would be uncomfortable to type, though not as bad as same-finger bigrams.

From the good and bad bigrams of the keyboard layout and the bigram frequencies of the input text, a count of good and bad bigrams can be calculated. These counts can be scaled by the total number of keystrokes to give a range from 0 to 1. We want the number of bad bigrams to be very small. So the quality function should be more sensitive in the small value range. This can be achieved with square root or 3rd root functions. For very small values this function has a very steep slope. That means the quality function will be very sensitive to small changes when the number of bigrams is small. For larger values the slope becomes more shallow, thus the sensitivity decreases.

Calculating the frequency of bigrams using this method is O(1) with respect to the size of the input text. The number of bigrams in the lookup table depends on the input text. However, a good hash table implementation for the lookup should also be O(1).

The set of good and bad bigrams is a set of tuneable parameters of the quality function. Similarly, the non-linear scaling using root functions has tuneable parameter.

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

The strong fingers are weighted more heavily. Since the index finger reaches more keys, its individual key weights tend to be smaller. Keys that require more of a stretch are weighted lower. For example the middle and ring fingers can stretch up relatively easily, whereas the index and pinky fingers prefer to curl to reach the bottom row rather than stretching up to the top row.

Aggressive column stagger on some ergonomic keyboards can compensate for some of the stretching. Thus the weights may have to be adjusted for such keyboards.

### Good bigrams

Which bigrams are easy to type may be somewhat subjective. This is the set chosen in my implementation expressed in terms of the left hand of the QWERTY layout:

WE, WF,
EF,
AE, AD, AF, AV,
SE, SD, SF, SV,
DF, DV,
FW, FE, FA, FS, FD, FZ,
ZD, ZF, ZC, ZV,
XD, XF, XC, XV,
CV,
VA, VS, VD, VZ, VX, VC

When mirrored for the right hand this results in a total of 68 favourable bigrams.

### Input text

The input text used to evaluate the quality function can also be understood as a parameter. It determines the language that the keyboard layout gets optimized for.

From early experience it appears that the size and diversity of the input text is important for making a keyboard layout that generalizes to most texts. For example initial experiments using a chapter from the Junglebook as input gave a skewed perception of common bigrams that did not generalize to other texts. For example the bigram "ow" is quite common in this text from the name "Mowgli", but it is not common in the English language in general.

Another reverse example, running experiments with two texts found very good solutions for those texts, but they didn't generalize well for other texts. It was found that the initial two texts didn't represent the "je" bigram well. A resulting keyboard layout applied to another text that included the word "project" many times performed poorly because it had "j" and "e" on the same finger.

These problems with input texts can be addressed in two different ways:

* Concatenating many diverse texts
* Preprocessing texts to remove unusual names or typos

Both approaches are being applied in the experiments below. Preprocessing uses a word list to filter all words in the text. Rejected words are output into a new "missing words" list that can be manually vetted. Any real words can be added to the canonical word list. Typos and unusual names can be left out.

The texts used in these experiments were copied from [8] and then preprocessed against a growing canonical word list. Presumably these source texts are all texts free of copyright or with expired copyright.

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

The algorithm was implemented in Python. This language makes it easy to work with lists and dictionaries with efficient lookup implemented by the Python interpreter. It also lends itself to fast prototyping. It may not be the most efficient in terms of raw speed. An optimized implementation in C++ may achieve better performance.

The current implementation can evaluate about 8000 keyboard layouts per second on a Ryzen 5 2400G running 3.6GHz. This is about a factor 30 improvement from an initial naive implementation, after switching to an efficient O(1) implementation of the bigram metrics, and calculating the number of keystrokes for normalization from the heatmap rather than the input text. Each evaluation of a layout involves 164 lookups in the bigram dictionary. Thus, the program is performing about 1.3 million lookups per second or about 2700 clocks per lookup, including all other overheads. Even with an optimized C++ implementation, this can probably not be improved by more than a factor of 10.

Update: Using pypy, an alternative Python implementation using a JIT compiler, gave an additional speed up of about factor three, evaluating about 2700 layouts per second.

## Convergence of solutions

The performance optimizations allow the use of a fairly slow annealing schedule that lowers the temperature very gradually, in a reasonable time budget. One run of the program completes in about 5 minutes with the parameters chosen. The solutions seem to converge quite well with a relatively small set of solutions being discovered quite consistently within a narrow range of quality function scores (roughly 0.78 to 0.79).

A run on 4 CPU cores for 8 hours performed 142 runs of the annealing schedule and found 65 unique solutions (counting mirrored versions as the same solution). The most popular solution was found independently by 16 program runs.

Update: Using pypy the run time improved from about 15 minutes to less than 5 minutes.

---

# Experiment

Out of 65 unique solutions found by 142 runs of the algorithm I picked 9 solutions to discuss the result. Each layout gets its own subsection showing the layout with the basic metrics and a short discussion.

Each keyboard layout is shown with key and finger weights normalized to match the weights used in the heatmap metric of the quality function.

The metrics are presented as follows:

| Metric        | Value       | Details |
| ------------- | ----------- | :------ |
| Heatmap       | 0 to 1      | None    |
| Bad bigrams   | Total count | Count for each bigram |
| Fast bigrams  | Total count | Count for each bigram |
| Finger travel | Total in units of the key size | Per-finger travel, normalized to a total of 1000 |
| Overall score | Score of the quality function | None |
| Times found   | Number of times the solution was found by the algorithm |

Finger travel is not used in the optimization, but it is shown here for reference and comparison with other layouts.

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
| Heatmap       | 0.4871 |         |
| Bad bigrams   |   5773 | ed:856 ec:639 de:608 ce:469 tr:460 ol:439 lo:390 un:281 rt:178 rf:142 hn:138 ft:131 fr:116 gr:103 ki:84 um:82 hu:74 mu:67 br:58 ju:56 rg:51 my:50 ny:45 ik:33 rv:31 ws:30 nm:28 za:24 nu:22 hy:19 aq:16 sw:11 gt:9 bt:8 az:6 rb:4 nh:4 ym:3 uy:3 hm:2 vg:1 yn:1 uj:1 |
| Fast bigrams  |   2816 | li:505 se:486 we:285 fa:245 oj:228 fe:200 af:191 ad:175 va:138 av:129 ef:107 jo:30 oi:28 sf:21 lk:14 xc:12 dv:11 lm:6 wf:1 df:1 fw:1 fs:1 km:1 |
| Finger travel |  75173 | 4, 25, 162, 223, 204, 55, 86, 6 |
| Overall score | 0.5563 |         |

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
| Heatmap       | 0.8932 |         |
| Bad bigrams   |   2412 | ct:920 je:233 gh:169 rn:118 up:99 pi:89 ki:84 ip:79 ui:78 ls:71 tw:62 pu:45 mb:43 ik:33 yi:32 xp:31 rv:31 nv:31 dg:28 yp:27 sl:21 tc:16 xi:15 iu:11 py:7 ix:7 uk:4 hd:4 uy:3 gm:3 dm:3 hm:2 oq:1 ej:1 kp:1 ky:1 ku:1 gd:1 df:1 db:1 hf:1 hb:1 mf:1 wt:1 nr:1 |
| Fast bigrams  |   7179 | th:2373 nt:892 st:792 ou:514 nc:396 ch:370 sh:311 ke:192 qu:180 ue:138 hn:138 ua:128 ak:104 ht:97 sc:95 au:87 sm:79 rc:70 ok:62 hr:38 ms:36 nm:28 oe:22 ka:10 tm:8 eu:7 nh:4 rh:3 uo:2 ek:1 ko:1 hs:1 |
| Finger travel |  57323 | 11, 27, 30, 115, 168, 90, 93, 46 |
| Overall score | 0.6631 |         |

The heatmap and bigram scores are much better than QWERTY. Also finger travel is much reduced. Only the right index finger still travels much more than other fingers.

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
| Heatmap       | 0.9112 |         |
| Bad bigrams   |    828 | hn:138 ue:138 sc:95 kn:47 pt:46 nk:45 cs:32 nl:32 yi:32 dg:28 nm:28 za:24 sf:21 aq:16 lk:14 dv:11 rw:10 gt:9 bt:8 kl:8 eu:7 az:6 lm:6 nh:4 wr:3 tp:3 pb:2 td:2 ln:2 hm:2 fs:1 pg:1 pd:1 gd:1 dp:1 db:1 vg:1 kh:1 km:1 |
| Fast bigrams  |  13358 | in:1658 on:1421 en:1130 at:1107 st:792 me:669 ou:514 as:501 tr:460 rs:447 no:443 ne:419 ta:368 ts:314 om:313 im:284 un:281 ie:273 em:252 ni:241 mo:209 af:191 rt:178 rf:142 va:138 mi:136 ft:131 av:129 tw:62 ny:45 rv:31 oe:22 nu:22 xc:12 iu:11 xt:9 wf:1 wt:1 yn:1 |
| Finger travel |  57648 | 4, 26, 96, 168, 167, 71, 49, 5 |
| Overall score | 0.7345 |         |

Colemak brings a small improvement in the heatmap score. The index and middle fingers are weighted most heavily. On top of the improvements in Dvorak, Colemak brings another big improvement of the bigram scores. Particularly the number of bad bigrams is only about 1/3 the number in Dvorak. Total finger travel is about the same as in Dvorak, but more evenly distributed to both hands. Both index fingers still travel a lot.

## AINT

    [; :] [ Y ] [ P ] [ J ] [ Z ] | [ X ] [ Q ] [ O ] [ F ] [ W ]
     0.3   2.6   3.8   0.6   0.1  |  0.2   0.3  13.0   4.3   2.7
    [ A ] [ I ] [ N ] [ T ] [ M ] | [ L ] [ R ] [ E ] [ S ] [ C ]
    12.5  11.7  12.1  15.5   3.9  |  6.8  10.2  19.9  10.1   6.7
    [. >] [ U ] [ B ] [ D ] [ K ] | [' "] [ H ] [, <] [ V ] [ G ]
     2.9   4.5   2.2   5.9   1.0  |  0.8   7.8   2.5   1.8   3.2
    15.7  18.8  18.1  27.1        |       26.1  35.5  16.2  12.6

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Heatmap       | 0.9373 |         |
| Bad bigrams   |    311 | ui:78 eo:48 hr:38 yi:32 rl:25 oe:22 sf:21 iu:11 tm:8 np:7 uy:3 tk:3 dm:3 rh:3 pb:2 bn:2 td:2 km:1 lr:1 fs:1  |
| Fast bigrams  |  22772 | he:2172 in:1658 er:1566 an:1561 re:1239 at:1107 or:1105 nd:1091 ti:1052 nt:892 it:770 co:717 ro:715 ve:677 se:486 ce:469 rs:447 fo:444 ch:370 ta:368 ge:320 sh:311 un:281 di:238 ut:237 so:234 cr:212 du:198 ty:194 id:179 ad:175 ap:173 gh:169 rf:142 fr:116 gr:103 ud:91 ub:83 ip:79 rc:70 eh:64 rg:51 da:48 pt:46 yp:27 yt:11 dn:5 tp:3 tn:3 db:1 sr:1 hs:1 |
| Finger travel |  59321 | 27, 69, 56, 106, 113, 127, 54, 49 |
| Overall score | 0.7925 |         |
| Times found   |      1 |         |

This is the first solution of the she optimization algorithm shown here. The heatmap score is on par with Colemak. Bigram scores are further improved. Same finger bigrams are reduced by almost another factor 1/3. Fast bigrams are improved by almost factor 2. This sets the standard for other solutions out of the optimization algorithm.

The total amount of finger travel is slightly bigger than Colemak and Dvorak, but it is quite balanced across the fingers, with only the right middle finger travelling a bit more from having two frequent vowels assigned to it.

One quirk in this layout is, that the left ring finger has more weight than the left middle finger. This would be easy to fix by just swapping those fingers. However, that would negatively affect the fast bigram score in exchange for only a minor improvement of the heatmap score.

Among the fast bigrams, "th" (being the most frequent bigram in the English language) is conspicuously absent. This may not be a bad thing. I found that typing the word "the" all in one hand felt awkward with some other solutions shown below.

For adoption of this layout, I would tweak to the  punctuation keys to move `'"` and `;:` to the same positions as in the Dvorak layout and arrange the `,<` and `.>` keys in a more sensible order in the right hand.

## Variation of AINT

    [ X ] [ Y ] [ P ] [ J ] [ Z ] | [; :] [' "] [ H ] [ V ] [ W ]
     0.2   2.6   3.8   0.6   0.1  |  0.3   0.8   7.8   1.8   2.7
    [ A ] [ I ] [ N ] [ T ] [ M ] | [. >] [ E ] [ R ] [ S ] [ C ]
    12.5  11.7  12.1  15.5   3.9  |  2.9  19.9  10.2  10.1   6.7
    [ Q ] [ U ] [ B ] [ G ] [ K ] | [, <] [ O ] [ L ] [ F ] [ D ]
     0.3   4.5   2.2   3.2   1.0  |  2.5  13.0   6.8   4.3   5.9
    13.0  18.8  18.1  24.3        |       39.5  24.8  16.2  15.4

| Metric        | Value  | Details  |
| ------------- | -----: | :------- |
| Heatmap       | 0.8687 |          |
| Bad bigrams   |    384 | ui:78 eo:48 hr:38 yi:32 rl:25 oe:22 sf:21 aq:16 iu:11 xa:10 gt:9 tm:8 np:7 uy:3 tk:3 gm:3 kg:3 rh:3 pb:2 bn:2 ax:1 km:1 lr:1 fs:1 |
| Fast bigrams  |  26582 | he:2172 in:1658 er:1566 an:1561 re:1239 at:1107 or:1105 ti:1052 nt:892 es:861 ed:856 it:770 ng:749 of:749 co:717 ro:715 ve:677 ec:639 de:608 se:486 ce:469 fo:444 ol:439 lo:390 ch:370 ta:368 sh:311 un:281 ut:237 so:234 ig:231 cr:212 fe:200 ty:194 ev:193 do:181 od:180 ap:173 ag:137 os:132 fr:116 oc:113 gi:105 ug:104 ub:83 ip:79 ga:69 eh:64 fl:54 gn:47 gu:47 pt:46 dr:38 yp:27 dl:17 yt:11 tp:3 tn:3 sr:1 |
| Finger travel |  60698 | 5, 69, 56, 87, 160, 116, 54, 68 |
| Overall score | 0.7949 |         |
| Times found   |      5 |         |

This variation of the AINT layout looks quite similar, but has a much worse heatmap score. It compensates for that with a much better fast bigram score. This demonstrates how the weighting of the component metrics of the quality function affects the compromises made in the search for a good layout.

Incidentally, this was the layout with the highest overall score.

Another interesting aspect of this layout is, how the punctuation keys are all on the right index finger. This matches the weighting of those keys and makes it easy to avoid bad bigrams on the index finger handling six keys.

## CION

    [ W ] [ U ] [ A ] [ B ] [ Z ] | [ Q ] [ J ] [. >] [ R ] [ X ]
     2.7   4.5  12.5   2.2   0.1  |  0.3   0.6   2.9  10.2   0.2
    [ C ] [ I ] [ O ] [ N ] [ P ] | [ M ] [ T ] [ E ] [ H ] [ S ]
     6.7  11.7  13.0  12.1   3.8  |  3.9  15.5  19.9   7.8  10.1
    [ G ] [ Y ] [; :] [ F ] [, <] | [ K ] [ D ] [' "] [ L ] [ V ]
     3.2   2.6   0.3   4.3   2.5  |  1.0   5.9   0.8   6.8   1.8
    12.6  18.8  25.9  25.0        |       27.2  23.7  24.8  12.1

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Heatmap       | 0.9274 |         |
| Bad bigrams   |    313 | ui:78 nf:61 hr:38 yi:32 oa:30 rl:25 iu:11 tm:8 np:7 uy:3 pf:3 tk:3 dm:3 rh:3 bn:2 pb:2 td:2 km:1 lr:1 |
| Fast bigrams  |  22097 | th:2373 he:2172 in:1658 an:1561 on:1421 ed:856 te:848 st:792 of:749 ng:749 co:717 ve:677 le:638 de:608 io:581 se:486 tr:460 fo:444 no:443 ca:428 nc:396 ts:314 na:307 un:281 et:279 ia:254 ni:241 ld:219 fi:180 rt:178 if:147 ua:128 go:97 ht:97 lt:79 ds:65 yo:62 gn:47 nu:22 dl:17 dv:11 fy:10 hd:4 yn:1 |
| Finger travel |  59133 | 49, 69, 81, 120, 109, 31, 121, 19 |
| Overall score | 0.7894 |         |
| Times found   |      7 |         |

Another layout with similar quality as the first AINT. Very good heatmap and bigram scores. Very balanced finger travel distance, except in this layout the right ring finger travels a lot.

This layout demonstrates an interesting aspect of optimizing for fast bigrams. Although both "th" and "he" are fast bigrams in this layout, putting the two together in the word "the" feels awkward.

This layout was found 7 times, which makes it one of the more "popular" or "easier to find" layouts.

## CION in a mirror, darkly

    [ K ] [ D ] [ H ] [; :] [ Z ] | [ Q ] [ B ] [ A ] [ Y ] [ W ]
     1.0   5.9   7.8   0.3   0.1  |  0.3   2.2  12.5   2.6   2.7
    [ S ] [ T ] [ R ] [ E ] [. >] | [ P ] [ N ] [ O ] [ I ] [ C ]
    10.1  15.5  10.2  19.9   2.9  |  3.8  12.1  13.0  11.7   6.7
    [ V ] [ M ] [ L ] [ U ] [' "] | [, <] [ F ] [ X ] [ J ] [ G ]
     1.8   3.9   6.8   4.5   0.8  |  2.5   4.3   0.2   0.6   3.2
    12.9  25.3  24.8  28.7        |       25.2  25.7  14.8  12.6

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Heatmap       | 0.9137 |         |
| Bad bigrams   |    456 | ue:138 nf:61 hr:38 sk:36 yi:32 oa:30 ze:26 rl:25 ks:16 xa:10 tm:8 eu:7 np:7 dm:3 rh:3 pf:3 ox:3 td:2 bn:2 pb:2 lr:1 nq:1 ax:1 xo:1 |
| Fast bigrams  |  26147 | th:2373 he:2172 in:1658 er:1566 an:1561 on:1421 re:1239 es:861 ed:856 te:848 of:749 ng:749 co:717 ve:677 me:669 de:608 io:581 se:486 tr:460 fo:444 no:443 us:431 ca:428 nc:396 sh:311 na:307 et:279 ur:272 ia:254 su:247 ni:241 ut:237 ru:207 ul:207 ev:193 fi:180 tu:148 if:147 go:97 lu:87 um:82 mu:67 eh:64 gn:47 ny:45 jo:30 ya:3 sr:1 yn:1 |
| Finger travel |  59002 | 28, 92, 116, 80, 122, 78, 32, 49 |
| Overall score | 0.7896 |         |
| Times found   |      1 |         |

This is a mirrored variant of CION, although with many changes. It has a relatively bad same-finger bigram score that it compensates for with much more fast bigrams. This is another example showing the trade-offs between different component metrics of the quality function.

## NTRO

    [ B ] [ G ] [ H ] [ Q ] [ X ] | [ J ] [ W ] [. >] [ Y ] [ Z ]
     2.2   3.2   7.8   0.3   0.2  |  0.6   2.7   2.9   2.6   0.1
    [ N ] [ T ] [ R ] [ O ] [, <] | [ F ] [ C ] [ E ] [ I ] [ S ]
    12.1  15.5  10.2  13.0   2.5  |  4.3   6.7  19.9  11.7  10.1
    [ P ] [ K ] [ L ] [ A ] [' "] | [ M ] [ D ] [; :] [ U ] [ V ]
     3.8   1.0   6.8  12.5   0.8  |  3.9   5.9   0.3   4.5   1.8
    18.1  19.7  24.8  29.4        |       24.1  23.2  18.8  12.0

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Heatmap       | 0.9212 |         |
| Bad bigrams   |    286 | ui:78 hr:38 yi:32 oa:30 rl:25 aq:16 iu:11 xa:10 gt:9 np:7 tk:3 kg:3 rh:3 ox:3 dm:3 uy:3 bn:2 pb:2 lr:1 xo:1 oq:1 ax:1 wf:1 fw:1 mf:1 df:1 |
| Fast bigrams  |  21592 | th:2373 an:1561 on:1421 at:1107 or:1105 to:881 ed:856 al:742 ro:715 ve:677 ec:639 de:608 ar:559 pr:544 ra:500 se:486 ce:469 tr:460 no:443 ic:405 ho:373 ta:368 uc:310 na:307 la:307 ie:273 ot:272 po:271 di:238 pl:232 og:203 du:198 id:179 ap:173 gh:169 pa:158 op:154 ci:151 ue:138 ak:104 go:97 sc:95 ud:91 ds:65 cy:39 cs:32 dv:11 ka:10 oh:8 kl:8 nh:4 nr:1 ko:1 yc:1
| Finger travel |  58383 | 56, 44, 116, 118, 144, 27, 69, 18 |
| Overall score | 0.7909 |         |
| Times found   |      1 |         |

This layout has an extremely good same-finger bigram score but slightly lower fast bigram score. Finger travel is slightly lower than in other layouts shown up to now, but the right index finger has to travel more.

The arrangement of the keys for T, H, R and O looks awkward. Spelling words such as "through" or "thorough" or "broth" will be awkward.

## WAUZRNET

    [ X ] [, <] [. >] [ J ] [ Q ] | [ B ] [ W ] [ A ] [ U ] [ Z ]
     0.2   2.5   2.9   0.6   0.3  |  2.2   2.7  12.5   4.5   0.1
    [ R ] [ N ] [ E ] [ T ] [ M ] | [ P ] [ C ] [ O ] [ I ] [ S ]
    10.2  12.1  19.9  15.5   3.9  |  3.8   6.7  13.0  11.7  10.1
    [ H ] [ L ] [; :] [ D ] [ K ] | [ G ] [ F ] [' "] [ Y ] [ V ]
     7.8   6.8   0.3   5.9   1.0  |  3.2   4.3   0.8   2.6   1.8
    18.1  21.4  23.2  27.2        |       22.9  26.4  18.8  12.0

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Heatmap       | 0.9341 |         |
| Bad bigrams   |    260 | ui:78 hr:38 nl:32 yi:32 oa:30 iu:11 tm:8 rh:3 tk:3 dm:3 bc:3 pf:3 uy:3 ln:2 td:2 wp:2 pb:2 km:1 wb:1 wf:1 pg:1 fw:1 |
| Fast bigrams  |  18542 | th:2373 he:2172 re:1239 nd:1091 nt:892 ed:856 te:848 of:749 co:717 le:638 de:608 io:581 ac:521 tr:460 fo:444 ca:428 ne:419 ic:405 uc:310 et:279 ia:254 so:234 ld:219 sa:185 fi:180 rt:178 ci:151 if:147 ua:128 cu:125 oc:113 ht:97 sc:95 rd:79 lt:79 yo:62 vo:54 dr:38 cs:32 sf:21 dl:17 fy:10 dn:5 hd:4 tn:3 yc:1 fs:1 |
| Finger travel |  57290 | 50, 78, 27, 109, 142, 87, 69, 18 |
| Overall score | 0.7853 |         |
| Times found   |      1 |         |

This layout has the best same-finger bigram score I have seen in any of the solutions. It also has a very good heatmap score. Finger travel distance is quite low, except for the right index finger.

The fast bigram score is lower than in other solutions showing another trade-off between metrics.

Typing "the" feels awkward even though both "th" and "he" are fast bigrams.

## RTEC

    [ X ] [ K ] [. >] [ W ] [ B ] | [ Z ] [ Q ] [ A ] [ U ] [ V ]
     0.2   1.0   2.9   2.7   2.2  |  0.1   0.3  12.5   4.5   1.8
    [ R ] [ T ] [ E ] [ C ] [ F ] | [, <] [ N ] [ O ] [ I ] [ S ]
    10.2  15.5  19.9   6.7   4.3  |  2.5  12.1  13.0  11.7  10.1
    [ H ] [ M ] [; :] [ D ] [ P ] | [ J ] [ L ] [' "] [ Y ] [ G ]
     7.8   3.9   0.3   5.9   3.8  |  0.6   6.8   0.8   2.6   3.2
    18.1  20.4  23.2  25.6        |       22.4  26.4  18.8  15.1

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Heatmap       | 0.9413 |         |
| Bad bigrams   |    293 | ui:78 hr:38 nl:32 yi:32 gs:32 oa:30 iu:11 tm:8 rh:3 tk:3 bc:3 pf:3 uy:3 wp:2 pb:2 ln:2 km:1 wb:1 wf:1 fw:1 db:1 df:1 dp:1 pd:1 nq:1 vg:1 sg:1 |
| Fast bigrams  |  20039 | he:2172 in:1658 an:1561 on:1421 re:1239 ct:920 ed:856 te:848 ng:749 me:669 ec:639 de:608 io:581 li:505 ce:469 no:443 ol:439 lo:390 ch:370 il:334 ns:310 na:307 un:281 ly:271 ia:254 ni:241 so:234 cr:212 sa:185 ck:141 ua:128 go:97 rd:79 ls:71 rc:70 yo:62 gl:61 gn:47 dr:38 nu:22 sl:21 tc:16 sn:9 hd:4 dm:3 td:2 kc:1 yn:1 |
| Finger travel |  56825 | 50, 47, 27, 163, 85, 87, 69, 48 |
| Overall score | 0.7873 |         |
| Times found   |      1 |         |

This layout has one of the best heatmap scores out of all solutions and also very good bigram scores. Furthermore it has one of the best total finger travel scores. The left index finger stands out negatively, however.

## STEReo

    [ X ] [ K ] [ O ] [ J ] [ Q ] | [ Z ] [ W ] [ P ] [ Y ] [; :]
     0.2   1.0  13.0   0.6   0.3  |  0.1   2.7   3.8   2.6   0.3
    [ S ] [ T ] [ E ] [ R ] [ L ] | [ F ] [ C ] [ N ] [ I ] [ A ]
    10.1  15.5  19.9  10.2   6.8  |  4.3   6.7  12.1  11.7  12.5
    [ V ] [ G ] [. >] [ H ] [, <] | [ M ] [ D ] [ B ] [ U ] [' "]
     1.8   3.2   2.9   7.8   2.5  |  3.9   5.9   2.2   4.5   0.8
    12.1  19.7  35.8  28.2        |       23.6  18.1  18.8  13.7

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Heatmap       | 0.9365 |         |
| Bad bigrams   |    294 | ui:78 eo:48 hr:38 yi:32 rl:25 oe:22 iu:11 gt:9 np:7 kg:3 tk:3 rh:3 dm:3 uy:3 pb:2 bn:2 lr:1 wf:1 fw:1 mf:1 df:1 |
| Fast bigrams  |  22674 | th:2373 he:2172 in:1658 er:1566 an:1561 re:1239 or:1105 nd:1091 to:881 te:848 ro:715 ve:677 ac:521 se:486 tr:460 rs:447 ca:428 ic:405 nc:396 ge:320 sh:311 uc:310 un:281 di:238 so:234 du:198 id:179 rt:178 ad:175 ap:173 gh:169 ci:151 gr:103 ht:97 ud:91 ub:83 ip:79 eh:64 rk:56 da:48 cy:39 rv:31 yp:27 dn:5 ko:1 sr:1 hs:1 yc:1 db:1 |
| Finger travel |  58321 | 19, 44, 123, 132, 137, 56, 69, 11 |
| Overall score | 0.7928 |         |
| Times found   |      6 |         |

This layout has very good scores all around and it was one of the more "popular" solutions, discovered 6 times independently. Finger travel is relatively low and reasonably well balanced.

## SHET

    [ X ] [ R ] [ O ] [ Q ] [ Z ] | [ B ] [ W ] [ L ] [ U ] [; :]
     0.2  10.2  13.0   0.3   0.1  |  2.2   2.7   6.8   4.5   0.3
    [ S ] [ H ] [ E ] [ T ] [ M ] | [ F ] [ C ] [ N ] [ I ] [ A ]
    10.1   7.8  19.9  15.5   3.9  |  4.3   6.7  12.1  11.7  12.5
    [ V ] [ J ] [, <] [ D ] [ K ] | [ P ] [ G ] [' "] [ Y ] [. >]
     1.8   0.6   2.5   5.9   1.0  |  3.8   3.2   0.8   2.6   2.9
    12.1  18.6  35.5  26.8        |       22.9  19.7  18.8  15.7

| Metric        | Value  | Details |
| ------------- | -----: | :------ |
| Heatmap       | 0.9399 |         |
| Bad bigrams   |    300 | ui:78 eo:48 hr:38 nl:32 yi:32 oe:22 iu:11 tm:8 rh:3 tk:3 dm:3 bc:3 pf:3 uy:3 td:2 wp:2 pb:2 ln:2 km:1 wb:1 wf:1 fw:1 pg:1 |
| Fast bigrams  |  21320 | th:2373 he:2172 in:1658 an:1561 to:881 ed:856 te:848 st:792 ng:749 al:742 ro:715 ve:677 de:608 ac:521 se:486 tr:460 ca:428 ic:405 nc:396 ho:373 il:334 ts:314 uc:310 et:279 ot:272 so:234 je:233 ig:231 ul:207 rt:178 ci:151 ag:137 cu:125 gy:113 gi:105 cl:101 ht:97 ga:69 ds:65 gn:47 dv:11 hd:4 yn:1 yc:1 |
| Finger travel |  58321 | 19, 59, 127, 103, 142, 58, 69, 27 |
| Overall score | 0.7902 |         |
| Times found   |     16 |         |

This was the most "popular" solution, discovered independently by 16 runs. It has very good scores with only the right index finger having to travel significantly more than other fingers. This is another layout where typing "the" feels awkward.

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
[9] [10 Fast Fingers typing test](https://10fastfingers.com/typing-test/english)
