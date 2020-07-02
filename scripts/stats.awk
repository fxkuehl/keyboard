#!/usr/bin/awk -f

BEGIN {
	FS = ":"
	trigger = 0
	total = 0
	heatmap_score = 0
	bad_bigrams_score = 0
	fast_bigrams_score = 0
}
/Heatmap score/ {
	heatmap_score = $2 + 0
}
/Bad bigrams/ {
	if (!bad_bigrams_score)
		bad_bigrams_score = $2 + 0
}
/Fast bigrams/ {
	if (!fast_bigrams_score)
		fast_bigrams_score = $2 + 0
}
/The number of # on the following line/ {
	trigger = 1
}
/^#+$/ {
	if (trigger) {
		print length($0), heatmap_score, bad_bigrams_score, fast_bigrams_score
		total += length($0)
		trigger = 0
		heatmap_score = 0
		bad_bigrams_score = 0
		fast_bigrams_score = 0
	}
}
END {
	print "Total:", total
}
