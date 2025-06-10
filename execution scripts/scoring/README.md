# RTEC-scoring
Info: evaluate.py computes Precision, Recall, F1-score, and their macro/micro averages for all FVPs of an event description. 

Usage: evaluate.py [-h] --gt GT --test TEST --out OUT 
	GT: path to RTEC recognitions file to be considered as GT
	TEST: path to RTEC recognitions file to be considered as TEST
	OUT: path to the comparison report

Note that the expected format of both GT and TEST file is the same as the output format of RTEC. No need for amalgamating
the input files, result amalgmation is taken care of by evaluate.py.

Example:
	python3 evaluate.py --gt example/caviar_gt.txt --test example/caviar_gt.txt --out example/report.csv
