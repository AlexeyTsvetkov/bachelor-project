#!/bin/sh

echo "Testing Sanders dataset"
python test_classifier.py --algorithm NaiveBayes --ngrams Unigrams --metric Count --input raw_data/scpn.csv
python test_classifier.py --algorithm NaiveBayes --ngrams Bigrams --metric Count --input raw_data/scpn.csv
python test_classifier.py --algorithm NaiveBayes --ngrams Both --metric Count --input raw_data/scpn.csv
python test_classifier.py --algorithm NaiveBayes --ngrams Both --selection DeltaIdf --top 1000 --metric Count --input raw_data/scpn.csv
python test_classifier.py --algorithm Dictionary --ngrams Unigrams --input raw_data/scpn.csv
python test_classifier.py --algorithm MaxEnt --ngrams Unigrams --metric Boolean --input raw_data/scpn.csv
python test_classifier.py --algorithm MaxEnt --ngrams Bigrams --metric Boolean --input raw_data/scpn.csv
python test_classifier.py --algorithm MaxEnt --ngrams Both --metric Boolean --input raw_data/scpn.csv
python test_classifier.py --algorithm MaxEnt --ngrams Both --metric Boolean --selection DeltaIdf --top 1000 --metric Count --input raw_data/scpn.csv
