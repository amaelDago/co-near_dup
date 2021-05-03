import os
import json
import pandas as pd
from utils import get_notice_from_sourceUid

print("Load conditor database")
filepath = "../../data/conditor.json"
with open(filepath, encoding="utf8", mode ="r") as f : 
    conditor = json.load(f)

df = pd.DataFrame(conditor)

filenames = "./data/test-data/"
files = os.listdir(filenames)
database = {}

for file in files : 
    print(file)
    data = pd.read_csv(filenames + file, encoding = "utf8", sep = "\t")

    sourceUids = (list(data.sourceUid1) + list(data.sourceUid2))

    for sourceUid in sourceUids : 
        if not sourceUid in conditor : 
            try :
                database[sourceUid] = get_notice_from_sourceUid(sourceUid, df)
            except : 
                print(sourceUid)
        else : 
           pass


with open("./data/database/database.json", "w", encoding="utf8") as f : 
    json.dump(database, f)

