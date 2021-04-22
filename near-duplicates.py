import os
import time
import csv
import json
import pandas as pd
from utils import checkNotice
from sklearn.metrics import precision_score, recall_score, f1_score
import dvc.api

with open("data/database/database.json", "r", encoding="utf8") as f : 
    data = json.load(f)

df = pd.DataFrame(data.values())

def get_notice_from_sourceUid(sourceUid, df = df): 
    if not isinstance(sourceUid, str) : 
        sourceUid = str(sourceUid)
    n_serie = df[df.sourceUid == sourceUid]
    t = n_serie.T.to_json()
    t_json = list(json.loads(t).values())[0]
    return t_json

def nearDuplicates(l1, l2) :
    for x, y in zip(l1, l2) : 
        n1 = get_notice_from_sourceUid(x)
        n2 = get_notice_from_sourceUid(y)
        i = checkNotice(n1,n2)
        if i : 
            yield i
        else : 
            yield 0


# TODO : A remplacer par l'api DVC sur gitub actions


path = "data/test-data/"
files = os.listdir(path)
print(files)
with open("resultats.tsv", encoding="utf8", mode = "w", newline="") as f : 
    csvwriter = csv.writer(f,delimiter = "\t")
    csvwriter.writerow(("file", "precision", "recall", "F score")) 

    for file in files : 

        test_file = pd.read_csv(path + file, sep = "\t", encoding="utf8")

        a = time.time()

        results = test_file.apply(lambda x : checkNotice(get_notice_from_sourceUid(x["sourceUid1"]), get_notice_from_sourceUid(x["sourceUid2"])), axis = 1)
        print(f"{file} statistics")
        print(f"Time elapsed are {time.time() - a}")
        prec = precision_score(results, list(test_file['validation manuelle']))
        recall = recall_score(results, list(test_file['validation manuelle']))
        f1 = f1_score(results, list(test_file['validation manuelle']))
        csvwriter.writerow((file, prec, recall, f1))
            






