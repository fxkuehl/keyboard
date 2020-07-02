Searching for the optimal keyboard layout
=========================================

***Empirically quantifying and optimizing keyboard layouts***

**Author:** *Felix Kuehling*

# Introduction

Most keyboard layouts in use today are based on historical keyboard designs for mechanical typewriters. The typical staggered-row design is a result of lever arms having to pass each other between rows of a mechanical keyboard. The common QWERTY layout is designed to slow down typists to avoid lever arms from jamming. Those design constraints do not apply to modern computer keyboards, yet they have been carries over almost without being questioned.

A few attempts have been make to redesign computer keyboards for ergonomic considerations, both in terms of physical layout and the mapping of symbols to keys. On the physical side, ergonomic keyboards are often split designs with the two halves at an angle to put the wrists into a more neutral position. However, most of the more affordable or main-stream designs still carry over the row stagger. More raddical designs either choose a regular matrix layout or a colunm stagger that attempts to match the different lengths of the fingers. There are many designs that reduce the number of physical keys to the ones within easy reach without having to move the hands. On such keyboards, more functions and symbols are activated by switching layers.

In terms of ergonomic keymaps, the oldest example I'm aware of is the Dvorak layout, which was patented in 1936. More modern layouts for the English language include Colemak and variations, Workman, Neo.

I have personally used QWERTZ (German version of QWERTY), QWERTY, Dvorak and Colemak. Learning a new layout is a time-consuming process. Whether using one keyboard layout over another leads to more speed or comfort is hard to judge objectively for any individual.

This study attempts to approach the problem of the optimal keyboard layout algorithmically as an optimization problem. The quality of the existing layouts can be quantified objectively using different criteria. There are several online keyboard layout analyzers available that can be used to analyze small numbers of keyboard layouts. A potentially more optimal layout could be found by searching the entire space of all possible keyboard layouts for a global optimum.

---

# Assumptions and limitations

Typical computer keyboards have between roughly 60 to 100 keys. Many of those keys are assigned to special functions or rarely used symbols. Many of those special keys are used very differently by different users, depending on whether they are writing text, computer programs, performing data entry, using CAD applications, gaming, etc. Therefore this study is going to focus on the central area of the keyboard containing the alphabetical keys and the most common punctuation characters. This should make it applicable to a wide range of keyboards, including minimalist ergonomic ones with 40 or fewer keys.

Any user willing to adopt a radically different keyboard layout for purposes of efficiency or comfort is also likely to be willing to switch to a programmable, ergonomic or ortholinear keyboard. So some assumptions of typical QWERTY keyboards with staggered rows may not be applicable. Specifically the position of Space, Shift, Caps-Lock, TAB, Enter and Backspacethe keys may be unusual. Furthermore, ergonomic keyboards have more keys available to the thumbs to take over some of those functions usually performed by the pinky fingers or require moving the hand away from the home position. Therefore all of those special keys are excluded from the analysis.

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

The set of symbols in the reduced layout is almost the same between the two layouts. The only difference is that QWERTY has the `/?` key, while Dvorak has the more frequently used `'"` key. Therefore Dvorak is a better starting point for an English language keyboard. For other languages, the punctuation characters could be replaced with other symbols such as Umlauts or letters with accents.

Less common punctuation keys are not considered here, e.g.: `-_`, `[{`, `]}`, \`~, `=+`, `\|`. The numbers row is missing altogether. On a keyboard with a numbers row, it can be added back. On a smaller keyboard it would be reached on a separate layer. Either way, it is not considered for layout optimization in this study.

## Search space

With the keyboard layout assumed above, there are 30 key positions to be assigned to 30 keys. That means the total number of possible layouts is 30! = 2.652528598×10<sup>32</sup>. That search space is too large for a brute-force search. A computer that could hypothetically evaluate one million layouts per second would take about 8.4×10<sup>18</sup> years, or 8.4 quintillion years. Even a supercomputer with a million nodes working at the same time would still take 8.4 trillion years.

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

When measuring typing speed, there is a trade-off between speed and comfort. Key sequences that are hard to type can still be typed fast with additional effort. For anecdotal evidence, see typing speed records on websites such as [10 Fast Fingers](https://10fastfingers.com/).

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

There may also be an argument for favouring one hand over the other. A right-handed person may want to favour the right hand. On the other hand, the right hand may have other jobs (e.g. operating a mouse or a number-pad), so one may want to reduce use of the strong hand for pure typing. An ambidextrous layout may be more widely acceptable by more users.

## Defining the quality function

The quality functions should express the quality of a keyboard layout using quantifiable metrics on a given input text. It should also be efficient to calculate. Ideally the cost of calculating the function should be O(1) with respect to the size of the input text.

The metrics chosen should account for the quality criteria outlined in the previous section. Some of the metrics may use parameters that can be changed or tuned in order to match real world usage or measurements, or personal preferences.

Multiple independent metrics can be combined with different linear or non-linear weighting to express the relative importance of different metrics. In order to make the combination of different metrics more meaningful, all metrics should be scaled to the same numeric range before applying weighting functions. The choice made in my implementation uses floating point numbers in the range from 0 to 1, with 0 being the lowest possible quality, and 1 being the highest.

### Heatmap

The use of different keys for typing an input text can be visualized as a heatmap. A target or ideal heatmap can be defined, and the actual usage of the layout with the input text can be compared with that ideal. The result is a numerical score that expresses how closely the actual heatmap matches the ideal.

Weights can be used to express how common the use of a particular key should be. Given a probability distribution of characters in a text, each character probability can be multiplied with its corresponding key weight using a given keyboard layout. A keyboard layout optimized for comfort would maximize the weighted sum. This can also be expressed as a dot-product.

The character probabilities can be calculated ahead of time. The dot-product has O(1) effort with respect to the size of the input text.

The result of the dot-product should be scaled to the common value range 0 to 1. The lowest possible dot-product should map to 0, the highest to 1. The lowest possible value can be calculated by assigning the most frequent characters to the lowest weighted keys in order and calculating the resulting dot-product. Conversely the highest possible value can be calculated by assigning the most frequent characters to the highest weighted keys. The actual score can be scaled linearly within this range.

The choice of key weights is a tuneable quality function parameter (or rather a set of 30 parameters). To get ambidextrous keyboard layouts, those weights should be symmetric between the left and right hand.

### Good and bad bigrams

The set of all potential bigrams (2-symbol sequences) can be determined from the input text, and the probability or frequency of each bigram can be stored in a lookup table.

From the keyboard layout a set of good and bad bigrams can be generated. Good bigrams are those, which are particularly comfortable or fast to type. Rolling motions from finger to finger without to having stretch uncomfortably should be favoured by the optimal keyboard layout. For example the sequence "EF" on the QWERTY layout would be a good bigram.

Bad bigrams are those, which use the same finger to type different letters. For example the sequence "RT" on the QWERTY layout would be bad. Furthermore, sequences that use different fingers but skip between the top and the bottom row, would be uncomfortable to type, though not as bad as same-finger bigrams.

From the good and bad bigrams of the keyboard layout and the bigram frequencies of the input text, a count of good and bad bigrams can be calculated. These counts can be scaled by the total number of key-strokes to give a range from 0 to 1. We want the number of bad bigrams to be very small. So the quality function should be more sensitive in the small value range. This can be achieved with square root or 3rd root functions. For very small values this function has a very steep slope. That means the quality function will be very sensitive to small changes when the number of bigrams is small. For larger values the slope becomes more shallow, thus the sensitivity decreases.

Calculating the frequency of bigrams using this method is O(1) with respect to the size of the input text. The number of bigrams in the lookup table depends on the input text. However, a good hash table implementation for the lookup should also be O(1).

The set of good and bad bigrams is a set of tuneable parameters of the quality function. Similar, the non-linear scaling using root functions is a tuneable parameter.

### Other metrics

Other metrics have been considered and even implemented. However, they are less computationally efficient and are therefore not used in the optimization. Most notably, the finger travel distance can only be calculated by actually simulating every key stroke, which is O(n) with respect to the length of the input text.

In practice, it is observed that the finger travel distance achieved with the heatmap and bigram-based metrics is reasonable and within the same range as existing ergonomic layouts. Furthermore, the travel distances don't differ by a huge amount between good and bad layouts. By contract, the bigram metrics can differ by several orders of magnitude.

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

Which bigrams are easy to type may be somewhat subjective. The set chosen in my implentation expressed in terms of the left hand of the QWERTY layout:

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

The algorithm was implemented in Python. This language makes it easy to work with lists and dictionaries with efficient lookup implemented in the language. It also lends itself to fast prototyping. It may not be the most efficient in terms of raw speed. An optimized implementation in C++ may achieve better performance.

The final implementation can evaluate about 8000 keyboard layouts per second on a Ryzen 5 2400G running 3.6GHz. This is about a factor 30 improvement from an initial naive implementation, after switching to an efficient O(1) implementation of the bigram metrics, and calculating the number of keystrokes for normalization from the heatmap rather than the input text. Each evaluation of a layout involves 164 lookups in the bigram dictionary. Thus, the program is performing about 1.3 million lookups per second or about 2700 clocks per lookup, including all other overheads. Even with an optimized C++ implementation, this can probably not be improved by more than a factor of 10.

## Convergence of solutions

The performance optimizations allow the use of a fairly slow annealing schedule that lowers the temperature very gradually, in a reasonable time bugdet. One run of the program completes in about 15 minutes with the parameters chosen. The solutions seem to converge quite well with a relatively small set of solutions being discovered quite consistently within a narrow range of quality function scores (roughly 0.78 to 0.79).

A run on 4 CPU cores for 8 hours performed 2O7 runs of the annealing schedule and found 65 unique solutions (counting mirrored versions as the same solution). The most popular solution was found 16 times in those runs.

# References

[Colemak Keyboard Layout](https://colemak.com/)<br>
[Workman Keyboard Layout](https://workmanlayout.org/)<br>
Patrick Gillespie’s [Keyboard Layout Analyzer](http://patorjk.com/keyboard-layout-analyzer/#/main)<br>
SteveP's fork of the [Keyboard Layout Analyzer](https://stevep99.github.io/keyboard-layout-analyzer/#/main)<br>
[10 Fast Fingers typing test](https://10fastfingers.com/typing-test/english)
