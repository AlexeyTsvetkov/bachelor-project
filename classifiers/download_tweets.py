import sys
import os
import time
import csv

from twitter_api_wrapper.twitter import Twitter
from twitter_api_wrapper.twitter_exceptions import *

if sys.argc != 3:
    print "Usage: python download_tweets.py path_to_input path_to_output"
    sys.exit()

input_path = sys.argv[1]
output_path = sys.argv[2]

if not os.path.exists(input_path):
    print "Input path does not exist"
    sys.exit()

if os.path.exists(output_path):
    print "Output path already exists"
    sys.exit()

with open(input_path, 'r') as input_file:
    with open(output_path, 'w') as output_file:
        reader = csv.reader(delimiter=',')
        writer = csv.writer(delimiter=',')
        twitter = Twitter()

        for row in reader:
            id = row[0]
            sentiment = row[1]

            try:
                tweet = twitter.get_tweet(id)
            except Twitter_Rate_Limit_Exception:
                time.sleep(60)
                continue
            except Twitter_Not_Found_Exception:
                time.sleep(6)
                continue

            writer.writerow([id, tweet['text'], sentiment])
            time.sleep(6)