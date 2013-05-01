import csv

with open('corpuses/sem_eval_corpus.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for i, row in enumerate(reader):
        if len(row) < 3:
            print i, row