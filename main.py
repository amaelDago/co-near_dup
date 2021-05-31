#!/usr/bin/env python
import sys
import json
from tqdm import tqdm
from utils import NoticeComparison, getNoticeFromSourceUid
#from flask import Flask

#app = Flask(__name__)
#app.config["DEBUG"] = True

# Get file
#with open(args.filepath, mode = "r", encoding = "utf8")

data = json.load(sys.stdin)

# Build avoir les index
# 

# Get index
index = {}
nearDupliTuples = []
for notice in data : 
    sourceUid = notice["sourceUid"]
    index[sourceUid] = notice
    nearDuplicate = notice["nearDuplicates"]
    try : 
        l = list(map(lambda y : y["sourceUid"], nearDuplicate))
        for x in l : 
            nearDupliTuples.append((sourceUid, x))
    except  : 
        pass

for x,y in tqdm(nearDupliTuples) : 
    try : 
        temp1 = getNoticeFromSourceUid(x, index)
        temp2 = getNoticeFromSourceUid(y, index)
        comp = NoticeComparison(temp1, temp2, threshold = .2)
        comp.run()
        dico = {"sourceUid1" : x, "sourceUid2" : y, "validation": comp.result, "comment" : comp.comment}
    except : 
        dico = {"sourceUid1" : x, "sourceUid2" : y, "validation" : 99, "comment" : "data not available"}
    
    sys.stdout.write(json.dumps(dico))
    sys.stdout.write('\n')
