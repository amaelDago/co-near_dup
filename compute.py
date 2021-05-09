import os
import json
import csv
import pandas as pd
from config import ratio
from utils import get_notice_from_sourceUid
from functions import NoticeComparison


with open("data/database/database.json", "r") as f : 
    db = json.load(f)

df = pd.DataFrame(db.values())
stats = []


path = "data/test-data/"
files = os.listdir(path)
# for ratio in range(0, 11): 
#     ratio = ratio/10
for file in files : 
    n_correct = 0
    n_ones = 0
    j = 0
    print(f"Compute {file}")
    test = pd.read_csv(path + file, encoding = "utf8", sep = "\t")
    for x,yy, z in zip(test.sourceUid1, test.sourceUid2, test["validation manuelle"]) : 
        
        n1 = get_notice_from_sourceUid(x, df)
        n2 = get_notice_from_sourceUid(yy, df)
        comp = NoticeComparison(n1, n2)
        comp.run()
        try : 
            res = comp.decision()
            if z == 1 : 
                n_ones +=1

                if z == res : 
                    n_correct+=1

        
        except : 
            j +=1
            print(comp.validation_dict)
        print(n_correct/n_ones)
        print(f"j{j}")
    #print(comp.validation)
    #comp
    # y_test = test['validation manuelle']
    # stats.append(comp.get_stats(y_test))
    # print(stats)


#dd = pd.DataFrame(stats)
#print(dd.head())
#dd.to_csv('score.csv')
