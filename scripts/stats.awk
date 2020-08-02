#!/usr/bin/awk -f

BEGIN {
	trigger = 0
	total = 0
	heatmap_score = 0
	finger_score = 0
	bad_bigrams_score = 0
	slow_bigrams_score = 0
	fast_trigrams_score = 0
	overall_score = 0
	fast_bigrams_score = 0
	travel_score = 0
}
/Heatmap \[key finger\]/ {
	if (!heatmap_score)
		heatmap_score = $4 + 0
	if (!finger_score)
		finger_score = $5 + 0
}
/Bigrams\/kKS \[bad slow\]/ {
	if (!bad_bigrams_score)
		bad_bigrams_score = $4 + 0
	if (!slow_bigrams_score)
		slow_bigrams_score = $5 + 0
}
/3-grams\/kKS \[fast\]/ {
	if (!fast_trigrams_score)
		fast_trigrams_score = $3 + 0
}
/Overall score/ {
	if (!overall_score)
		overall_score = $5 + 0
}
/Bigrams\/kKS \[fast\]/ {
	if (!fast_bigrams_score)
		fast_bigrams_score = $3 + 0
}
/Finger travel\/kKS/ {
	if (!travel_score)
		travel_score = $3 + 0
}
/^#+/ {
	if (trigger) {
		match($0, /^#+/)
		print RLENGTH, overall_score, heatmap_score, finger_score, bad_bigrams_score, slow_bigrams_score, fast_trigrams_score, fast_bigrams_score, travel_score
		total += RLENGTH
		trigger = 0
		heatmap_score = 0
		finger_score = 0
		bad_bigrams_score = 0
		slow_bigrams_score = 0
		fast_trigrams_score = 0
		overall_score = 0
		fast_bigrams_score = 0
		travel_score = 0
	}
}
/The number of # on the following line/ {
	trigger = 1
}
END {
	print "Total:", total
}
