import sys
import os
import time
import csv
from classifiers.utils import UnicodeWriter

from twitter_api_wrapper.twitter import Twitter
from twitter_api_wrapper.twitter_exceptions import *

if len(sys.argv) != 3:
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
        reader = csv.reader(input_file, delimiter=',')
        writer = UnicodeWriter(output_file, delimiter=',')
        twitter_client = Twitter()

        count = 0
        for row in reader:
            id = row[0]
            sentiment = row[1]

            try:
                tweet = twitter_client.get_tweet(id)
                count += 1
            except Twitter_Rate_Limit_Exception:
                time.sleep(60)
                continue
            except Twitter_Forbidden_Exception:
                time.sleep(5)
                continue
            except Twitter_Not_Found_Exception:
                time.sleep(5)
                continue

            if count % 100 == 0:
                print count

            try:
                writer.writerow([id, tweet['text'], sentiment])
            except Exception:
                print [id, tweet['text'], sentiment]

            time.sleep(5)