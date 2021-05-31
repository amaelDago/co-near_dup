import json
import math
import string
import unidecode
import base64
import itertools as it
import pandas as pd
from unicodedata import normalize
import xml.etree.ElementTree as ET
from sklearn.metrics import classification_report
from config import decisionGrid, typeConditorCategory, titleStopwords

class Notice :
    
    def __init__(self, notice) : 
        # id
        self.doi = notice["doi"] if "doi" in notice else None
        self.pmId = notice["pmId"] if "pmId" in notice else None
        self.nnt = notice["nnt"] if "nnt" in notice else None
        
        # Content
        self.titleDefault = notice["title"]['default'] if "title" in notice else None
        self.en = notice["title"]["en"] if "title" in notice else None
        self.fr = notice["title"]["fr"] if "title" in notice else None
        self.titleDict = {"default" : self.titleDefault, "en" : self.en, "fr" : self.fr}
        
        # container
        self.meeting = notice["title"]["meeting"] if "title" in notice else None
        self.journal = notice["title"]["journal"] if "title" in notice else None
        self.issn = notice["issn"] if "issn" in notice else None
        self.eissn = notice["eissn"] if "eissn" in notice else None
        self.eisbn = notice["eisbn"] if "eisbn" in notice else None
        self.isbn = notice["isbn"] if "isbn" in notice else None
        self.monography = notice["title"]["monography"] if "title" in notice else None
        self.source = notice["source"] if "source" in notice else None
        self.docType = notice["documentType"][0] if "documentType" in notice else None
        self.publiSource = getSettlement(notice["teiBlob"]) if "teiBlob" in notice else None
        
        # Positionning
        self.publiDate = notice["publicationDate"] if "publicationDate" in notice else None
        self.pageRange = notice["pageRange"] if "pageRange" in notice else None
        self.issue = notice["issue"] if "issue" in notice else None
        self.volume = notice["volume"] if "volume" in notice else None
        
        # Others
        self.typeConditor = notice["typeConditor"] if "typeConditor" in notice else None
        self.sourceUid = notice['sourceUid'] if "sourceUid" in notice else None
        
def getSettlement(teiblob) : 
    decodeTeiblob = base64.b64decode(teiblob).decode('utf8')
    root = ET.fromstring(decodeTeiblob)
    dictionary = {}

    for child in root.iter("{http://www.tei-c.org/ns/1.0}meeting") : 
        dictionary.setdefault("title", None)
        dictionary.setdefault("begin", None)
        dictionary.setdefault("settlement", None)
        try :
            dictionary['title'] = next(child.iter("{http://www.tei-c.org/ns/1.0}title", )).text
        except : 
            pass

        try : 
            dictionary["begin"] = next(child.iter("{http://www.tei-c.org/ns/1.0}date")).text
        except :
            pass
    
        try : 
            dictionary["settlement"] = next(child.iter("{http://www.tei-c.org/ns/1.0}settlement")).text
        except : 
            pass

    return dictionary



def getSameBeginSequence(string1, string2) : 
    return ''.join(el[0] for el in it.takewhile(lambda t: t[0] == t[1], zip(string1, string2)))

def normalized(word) : 
    if not isinstance(word, str) : 
        word = str(word)

    word = word.strip().translate(str.maketrans('', '', string.punctuation)) # Remove punctation
    word = normalize("NFKD", word) # Replace some char like \xx
    word = unidecode.unidecode(word).lower() # lower case and remove accent
    return word



def damerauLevenshtein(seq1, seq2) : 

    """Calculate the Damerau-Levenshtein distance between sequences"""
    if not isinstance(seq1, str) and not isinstance(seq1, str) : 
        seq1 = str(seq1); seq2 = str(seq2)

    oneago = None
    thisrow = list(range(1, len(seq2) + 1)) + [0]
    for x in range(len(seq1)):
        twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        for y in range(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
            
            # This block deals with transpositions
            if (x > 0 and y > 0 and seq1[x] == seq2[y - 1]
                and seq1[x-1] == seq2[y] and seq1[x] != seq2[y]):
                thisrow[y] = min(thisrow[y], twoago[y - 2] + 1)
    return thisrow[len(seq2) - 1] 

# Compute relative distance between 2 sentences : Using levenshtein distance 
def sequenceDistance(seq1 , seq2) : 
    seq1 = normalized(seq1)
    seq2 = normalized(seq2)

    maxlen = max(len(seq1), len(seq2))

    dist = damerauLevenshtein(seq1, seq2)
    return dist/maxlen

def check(x1, x2) : 
    """
    Allows to compare 2 objects : maybe string int bool list or tuple
    return 1 if they are matching, 0 if not, -1 if there are there missing values
    """
    if isinstance(x1, str) and isinstance(x2, str) : 
        if x1 == "" or x2 == "" : 
            return 0

        if (x1.lower().strip() in x2.lower().strip()) or\
            (x2.lower().strip() in x1.lower().strip()): 
            return 1

        elif not x1 or not x2 :
            return 0

        else : 
            return -1
    
    elif isinstance(x1, (int, bool)) and isinstance(x2, (int, bool)) :
        if x1==x2 : 
            return 1
        else : 
            return -1

    elif isinstance(x1, float) and isinstance(x2, float) :
        if (math.isnan(x1)== 1 or math.isnan(x2)== 1 ):   
            return 0
        else : 
            if x1 == x2 : 
                return 1
            else : 
                return -1
    
    elif isinstance(x1, (list, tuple)) and isinstance(x2, (list, tuple)) : 
        if not x1 or not x2 :
            return 0
        else : 
            return check(x1[0], x2[0]) 
       
    else : # 1 one for missing value : 
        return 0

def checkPageRange(x1, x2) :

    if not x1 or not x2 or x1 == "np" or x2 == "np": 
        return 0 # Missing value
    
    elif isinstance(x1, float) and isinstance(x2, float): 
        if math.isnan(x1) or math.isnan(x2) : 
            return 0 # nan value
        else : 
            if x1!=x2 : 
                return -1 # Different float
            else : 
                return 1 # floats not missing value which are same
    elif x1==x2 : 
        return 1
    else : 
        x1 = "".join([x.lower().strip() for x in str(x1).lower().strip().split("-")])
        x2 = "".join([x.lower().strip() for x in str(x2).lower().strip().split("-")])

        if x1 == x2 : 
            return 1
        else : # Other cases 
            if len(x2)>len(x1) : 
                temp = x1
                x1 = x2
                x2 = temp

            sameSequenceAtBegining = getSameBeginSequence(x1,x2)
            x11 = x1[len(sameSequenceAtBegining):]
            x22 = x2[len(sameSequenceAtBegining):]

            diff = len(x11) - len(x22)
            begin = sameSequenceAtBegining[:diff]

            if x11.endswith(x22) and sameSequenceAtBegining.startswith(begin)\
                and 2*len(sameSequenceAtBegining) == len(x1): 
                return 1
            else :
                return -1 

#####################################
# 2 We define needed functions
#####################################
def comparePublicationSource(publiSource1,publiSource2) :
    publiSource1 = publiSource1
    publiSource2 = publiSource2

    if not publiSource1 or not publiSource2 :
        return 0

    else : 
        d = []
        try : 
            beginDate1 = str(publiSource1['begin']).lower().strip()
            beginDate2 = str(publiSource2['begin']).lower().strip()
        except ValueError as err : 
            raise err

        try :    
            title1 = str(publiSource1['title']).lower().strip()
            title2 = str(publiSource2['title']).lower().strip()
        except ValueError as err : 
            raise err
            
        try : 
            settlement1 = str(publiSource1['settlement']).lower().strip()
            settlement2 = str(publiSource2['settlement']).lower().strip()
        except ValueError as err : 
            raise err

        d.append(check(beginDate1, beginDate2))
        d.append(check(settlement1, settlement2))
        d.append(check(title1, title2))

        if 1 == d :  
            return 1

        elif -1 in d : 
            return -1

        return 0

def compareIssn(issn1, issn2) : 
    issn1 = "".join(str(issn1).strip().lower().split("-"))
    issn2 = "".join(str(issn2).strip().lower().split("-"))
    return check(issn1, issn2)



def getNoticeFromSourceUid(sourceUid, indexor): 
    if not isinstance(sourceUid, str) : 
        sourceUid = str(sourceUid)
    try : 
        return indexor[sourceUid]
    except Exception as err: 
        return err

def compareId(doi1, doi2, nnt1, nnt2, pmId1, pmId2) : 
    """
    check if notice is valid for identifier
    """

    if doi1 and doi2 : 
        if isinstance(doi1, str) and isinstance(doi2, str) :
            if str(doi1).lower().strip() == str(doi2).lower().strip() : 
                return 1
            else : 
                return -1
    
    elif nnt1 and nnt2 : 
        if isinstance(nnt1, str) and isinstance(nnt2, str) :
            if str(nnt1).lower().strip() == str(nnt2).lower().strip() : 
                return 1
            else : 
                return -1

    elif pmId1 and pmId2 : 
        if isinstance(pmId1, str) and isinstance(pmId2, str) :
            if str(pmId1).lower().strip() == str(pmId2).lower().strip() : 
                return 1
            else : 
                return -1

    else : 
        return 0

def comparePageRange(pageRange1,pageRange2) : 
    return checkPageRange(pageRange1, pageRange2)

def compareVolumaison(issue1, issue2, volume1, volume2) : 
    
    if issue1 and issue2 : 
        if issue1== issue2 : 
            return 1
        else : 
            return -1

    elif volume1 and volume2 : 
        if volume1 == volume2 : 
            return 1
        else : 
            return -1
    else : 
        return 0

def comparePublisher(eissn1, eissn2, issn1, issn2, \
                       meeting1, meeting2, journal1, journal2,\
                       publiSource1, publiSource2,eisbn1, eisbn2, isbn1, isbn2) : 
    
    eissn = compareIssn(eissn1, eissn2)
    issn = compareIssn(issn1, issn2)
    meeting = check(meeting1, meeting2)
    journal = check(journal1, journal2)
    settlement = comparePublicationSource(publiSource1, publiSource2)
    isbn = check(isbn1, isbn2)
    eisbn = check(eisbn1, eisbn2)

    if settlement or issn or eissn or meeting or journal or eisbn or isbn == 1 : 
        return 1
    elif settlement or issn or eissn or meeting or journal or eisbn or isbn == -1:
        return -1
    else  :
        return 0 
 
def compareTitle(titleDict1, titleDict2, threshold = .2) : 
    sortedKeys =  sorted(list(titleDict1.keys()))
    for key in sortedKeys : 
        for otherKey in sortedKeys :
            if len(str(titleDict1)[key].split()) == 1 or len(str(titleDict2[otherKey]).split()) == 1 \
                and (titleDict1[key].split()[0] in titleStopwords or titleDict2[otherKey].split()[0] in  titleStopwords ): 
                return 0

            dist = sequenceDistance(titleDict1[key], titleDict2[otherKey])  
            if dist <= threshold : 
                return 1
    return -1


def compareTitle(titleDict1, titleDict2, threshold = .2) : 
    dist = sequenceDistance(titleDict1["default"], titleDict2["default"])  
    if dist <= threshold : 
        return 1
    return -1



class NoticeComparison : 

    def __init__(self, notice1, notice2, threshold = 0.2) : 

        self.n1 = self.Record(notice1)
        self.n2 = self.Record(notice2)
        self.threshold = threshold
        self.validation_dict = {}
        self.result = None
        self.comment = None
        self.status = False

    def compareId(self):
       self.validation_dict["id"] = compareId(self.n1.doi, self.n2.doi,\
                           self.n1.nnt, self.n2.nnt,\
                           self.n1.pmId, self.n2.pmId)
    
    def comparePageRange(self) : 
       self.validation_dict["page"] = comparePageRange(self.n1.pageRange, self.n2.pageRange)

    def compareVolumaison(self) : 
        self.validation_dict["vol"] = compareVolumaison(
            self.n1.issue, self.n2.issue, self.n1.volume, self.n2.volume
        )

    def comparePublisher(self) : 
        self.validation_dict["source"] = comparePublisher(
            self.n1.eissn, self.n2.eissn, self.n1.issn, self.n1.issn,
            self.n1.meeting, self.n2.meeting, self.n1.journal, self.n2.journal,
            self.n1.publiSource, self.n2.publiSource,
            self.n1.eisbn, self.n2.eisbn, self.n1.isbn, self.n2.isbn 
        )


    def compareTitle(self) : 
        self.validation_dict["title"] = compareTitle(
            self.n1.titleDict, self.n2.titleDict, self.threshold
        )


    def checkpoint(self) : 
        try : 
            tup = tuple(self.validation_dict.values())
            if tup[0] == 1 and tup[5] == 1 and (self.n1.typeConditor or self.n2.typeConditor) == "Thèse" : 
                self.result, self.comment = (1, "1id, 1title, typeConditor=thèse")

            elif typeConditorCategory[self.n1.typeConditor] != typeConditorCategory[self.n2.typeConditor] :
                if (typeConditorCategory[self.n1.typeConditor] or typeConditorCategory[self.n2.typeConditor]) != "autre" : 
                    self.result, self.comment = decisionGrid[tup]
                else : 
                    self.result, self.comment = (-1, "#typeConditor")

            else : 
                self.result, self.comment = decisionGrid[tup]
        except : 
            self.result, self.comment = 99, "Record not available"


    def run(self) : 
        self.compareId()
        self.comparePageRange()
        self.compareVolumaison()
        self.comparePublisher()
        self.compareTitle()
        self.checkpoint()
        self.status = True
        
    def decision(self) :
        if self.status : 
            try : 
                tup = tuple(self.validation_dict.values())
                return decisionGrid[tup]
            except :
                pass
        else :
            self.run()
            self.decision()
   
    class Record(Notice):
        pass

class RecordFileComparison : 

    def __init__(self, sourceUidList1, sourceUidList2, indexor, threshold = 0.2) : 
        self.sourceUidList1 = sourceUidList1
        self.sourceUidList2 = sourceUidList2
        self.threshold = threshold
        self.indexor = indexor
        self.dataframe = None

    def run(self) : 
        l = []
        for x,y in zip(self.sourceUidList1, self.sourceUidList2) : 
            try : 
                temp1 = getNoticeFromSourceUid(x, self.indexor)
                temp2 = getNoticeFromSourceUid(y, self.indexor)
                comp = NoticeComparison(temp1, temp2, self.threshold)
                comp.run()
                dico = {"sourceUid1" : x, "sourceUid2" : y, "validation": comp.result, "comment" : comp.comment}
            except : 
                dico = {"sourceUid1" : x, "sourceUid2" : y, "validation" : 99, "comment" : "data not available"}
            l.append(dico)
        self.dataframe = pd.DataFrame(l)
    
    def is_done(self) : 
        if len(self.dataframe) == len(self.sourceUidList1) : 
            return True
        else : 
            return False

    def get_stats(self, y) :
        self.dataframe['validation manuelle'] = y
        yy = list(self.dataframe['validation'])
        v = [(x,t) for x,t in  zip(yy, y) if x  != 99 ]

        ytest = [x[1] for x in v]
        ypred = [x[0] for x in v]

        classif =  classification_report(ytest, ypred)

        return {
               "report" : classif
               }
    
    class Record(Notice) : 
        pass