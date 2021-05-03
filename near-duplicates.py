import os
import json
import pandas as pd
from config import ratio
from utils import NoticeComparison

with open("data/database/database.json", "r") as f : 
    db = json.load(f)

df = pd.DataFrame(db.values())
stats = []


path = "data/test-data/"
files = os.listdir(path)
#for ratio in range(0, 11): 
    #ratio = ratio/10
for file in files : 
    print(f"Compute {file}")
    test = pd.read_csv(path + file, encoding = "utf8", sep = "\t")

    comp = NoticeComparison(test.sourceUid1, test.sourceUid2, df, ratio)
    comp.compare_notice()
    y_test = test['validation manuelle']
    stats.append(comp.get_stats(y_test))
    #print(stats)

dd = pd.DataFrame(stats)
print(dd.head())
dd.to_csv('resultats.tsv', sep = "\t")
