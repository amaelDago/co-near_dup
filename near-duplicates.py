import pandas as pd
import json
from tqdm import tqdm
import argparse
from utils import NoticeComparison, RecordFileComparison


# Argument Parser
parser = argparse.ArgumentParser(description="near Duplicates validation" )
parser.add_argument("--filepath", help = "File to get near duplicates validation. Must be a csv files")
parser.add_argument('--separator', help = "separator", default = ",")
parser.add_argument('--record-database', help = "Records database. May be jsonfile coming from Conditor API ")
args = parser.parse_args()

df = pd.read_csv(args.filepath, sep= args.separator)

sl1 = df.sourceUid1
sl2 = df.sourceUid2
y = list(df["validation manuelle"])


with open(args.record_database, "r") as f : 
    db = json.load(f)

print("Data importation...")
indexor = {}
d = []
for notice in db : 
    sourceUid = notice["sourceUid"]
    indexor[sourceUid] = notice
    nearDuplicate = notice["nearDuplicates"]
    try : 
        l = list(map(lambda y : y["sourceUid"], nearDuplicate))
        for x in l : 
            d.append((sourceUid, x))
    except  : 
        pass
print("Compute near duplicate validation")
comp = RecordFileComparison(sl1, sl2, indexor, threshold=0.2) 
comp.run()
print(comp.get_stats(y)['report'], sep = '\n')
print(comp.dataframe.head())
print(comp.dataframe[["validation","comment"]].groupby("validation").count())


comp.dataframe.to_csv('resultat.tsv', sep = "\t")
