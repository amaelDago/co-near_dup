from bs4 import BeautifulSoup
import base64
from tqdm import tqdm
import numpy as np
import string
import unidecode
from unicodedata import normalize
from config import coef_dict, ratio
import json
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

class Notice : 
    def __init__(self, notice) : 
        self.doi = notice["doi"] if "doi" in notice else None
        self.default_title = notice["title"]['default'] if "title" in notice else None
        self.meeting = notice["title"]["meeting"] if "title" in notice else None
        self.journal = notice["title"]["journal"] if "title" in notice else None
        self.publi_date = notice["publicationDate"] if "publicationDate" in notice else None
        self.page_range = notice["pageRange"] if "pageRange" in notice else None
        self.issue = notice["issue"] if "issue" in notice else None
        self.source = notice["source"] if "source" in notice else None
        self.doc_type = notice["documentType"][0] if "documentType" in notice else None
        self.issn = notice["issn"] if "issn" in notice else None
        self.eissn = notice["eissn"] if "eissn" in notice else None
        self.nnt = notice["nnt"] if "nnt" in notice else None
        self.ppn = notice["ppn"] if "ppn" in notice else None
        self.settlement = getSettlement(notice["teiBlob"]) if "teiBlob" in notice else None
        self.volume = notice["volume"] if "volume" in notice else None
        self.type_conditor = notice["typeConditor"] if "typeConditor" in notice else None
        self.sourceUid = notice['sourceUid'] if "sourceUid" in notice else None
        #if self.settlement : 
        #    self.begin_date = self.settlement.find("date",attrs={"type" : "start"}).text
        #    self.end_date = self.settlement.find("date",attrs={"type" : "end"}).text
        #    self.settlement = self.settlement.find("settlement").text 


# Def settlement
def getSettlement(teiblob) :
    tb_decoded = base64.b64decode(teiblob).decode('utf8')
    soup = BeautifulSoup(tb_decoded, "lxml")
    t = soup.find("meeting")
    if t :
        return t
    else : 
        return None


def normalized(word) : 
    if not isinstance(word, str) : 
        word = str(word)

    word = word.strip()
    word = word.translate(str.maketrans('', '', string.punctuation)) # Remove punctation
    word = normalize("NFKD", word) # Replace some char like \xx
    word = unidecode.unidecode(word).lower() # lower case and remove accent
    return word



def levenshtein_distance(word1, word2) : 

    # Calcul la distance entre deux chaine de carcatères
    assert type(word1)==str and type(word2)==str, "Inputs must be string"
    
    len1 = len(word1)
    len2 = len(word2)
    
    # Zeros Array to fill  
    arr = np.zeros((len1+1, len2+1))
    #cost = 0
    
    arr[:,0] = np.array(list(range(len1+1)))
    arr[0,:] = np.array(list(range(len2+1)))
    


    for i in range(1, len1+1) : 
        for j in range(1, len2+1) : 
            # -1 because python begin count by 0
            if word1[i-1] == word2[j-1] : 
                cost = 0
            else : 
                cost = 1

            arr[i,j] = min(arr[i-1,j]+1, arr[i, j-1]+1, arr[i-1, j-1] + cost)
            
            # Word -1 because python count begin by 0
            #if (i>1 and j>1) and word1[i-1]==word2[j-2] and word1[j-2]==word2[j-1] : 
            #    arr[i,j] = min(arr[i,j], arr[i-2,j-2] + cost)
        
    return(arr[len1, len2])  

# Compute relative distance between 2 sentences : Using levenshtein distance 
def sentenceDistance(sentence1 , sentence2) : 
    sentence1 = normalized(sentence1)
    sentence2 = normalized(sentence2)

    maxlen = max(len(sentence1), len(sentence2))

    dist = levenshtein_distance(sentence1, sentence2)
    return dist/maxlen



def check(x1, x2, coef = 1) : 
    # Check : Compare two object like int bool string list or tuple
    # 1 means can be the same and 0 not

    if isinstance(x1, str) and isinstance(x2, str) : 
        if x1 == "" or x2 == "" : 
            return [0.1*coef, 1]

        if (x1.lower().strip() in x2.lower().strip()) or (x2.lower().strip() in x1.lower().strip()): 
            return [0.9*coef, 1]

        elif not x1 or not x2 :
            return [0.1*coef, 1]

        else : 
            return [0.9*coef, -1]
    
    elif isinstance(x1, (int, bool)) and isinstance(x2, (int, bool)) :
        if x1==x2 : 
            return [0.9*coef, 1]
        else : 
            return [0.9*coef, -1]

    elif isinstance(x1, float) and isinstance(x2, float) :
        return [0.1*coef, 1]
    
    elif isinstance(x1, (list, tuple)) and isinstance(x2, (list, tuple)) : 
        if not x1 or not x2 :
            return [0.1*coef, 1]
        else : 
            return check(x1[0], x2[0]) 
       
    else : # 1 one for missing value : 
        return [0.1*coef, 1]


import math

def checkPR(x1, x2, coef = 1) :

    if not x1 or not x2 : 
        return [0.1*coef, 1]
    
    elif isinstance(x1, float) and isinstance(x2, float): 
        if math.isnan(x1) or math.isnan(x2) : 
            return [0.1*coef, 1]
        else : 
            if x1!=x2 : 
                return [0.9*coef, -1]
    elif x1==x2 : 
        return [0.9*coef, 1]
    else : 
        x1 = str(x1)
        x2 = str(x2)

        x1_l = [x for x in x1.strip().split("-") if x]
        x2_l = [x for x in x2.strip().split("-") if x]

        if x1_l == x2_l : 
            return [0.9*coef, 1]

        else : 
            flag = True
            i = 0

            if len(x2)>len(x1) : 
                temp = x1
                x1 = x2
                x2 = temp
            while flag : 
                if x1[i].strip() == x2[i].strip() : 
                    flag = True
                    i +=1 
                    if i == min(len(x1), len(x2)): 
                        flag = False
                        return [0.9*coef, 1]

                else : 
                    #x11 = x1[:i].strip()
                    x12 = x1[i:].replace("-","").strip()
                    x22 = x2[i:].replace("-","").strip()

                    x121 = x12[:-len(x22)]
                    temp = x121 + x22

                    if temp == x12 : 
                        return [0.9*coef, 1]
                    else : 
                        return [0.9*coef, -1]
                    flag = False



#####################################
# 2 We define needed functions
#####################################

def checkDoi(notice1, notice2, coef = 1) : 

    if isinstance(notice1["doi"], float) or isinstance(notice2["doi"], float) : 
        return 0
    else :  
        if str(notice1["doi"]).lower().strip()==str(notice2["doi"]).lower().strip() : 
            return 1    
        else : 
            return -1

def compare_doi(doi1, doi2, coef = 1) : 
    #return check(doi1, doi2)
    if isinstance(doi1, str) and isinstance(doi2, str) : 
        
        if doi1 == doi2 : 
            return [0.9*coef,1]
        elif doi1 == "" or doi2=="" : 
            return [0.1,1]
        else  :
            return [0.9*coef, -1]

    elif isinstance(doi1, str) or isinstance(doi2, str) : 
        return [0.1*coef, 1]

    else :
        return [0.1*coef,1]


def compare_publi_date(pd1, pd2, coef = 1) : 

    if not (isinstance(pd1, str) and isinstance(pd2, str)) : 
        return [0.1*coef, 1]
    else :  
        pd1 = str(pd1).lower().strip()
        pd2 = str(pd2).lower().strip()

        if pd1 in pd2 or pd2 in pd1 :  
            return [0.9*coef, 1]   
        else : 
            return [0.9*coef, -1]

def compare_page_range(page_range1, page_range2, coef = 1) : 

    # if not isinstance(page_range1, str) or isinstance(page_range2, str) : 
    #     return [0.1*coef, 1]
    # elif page_range1 == "np" or page_range2 == "np" : 
    #     return [0.1*coef, 1]
    # else :  
    return checkPR(page_range1, page_range2)

def compare_issue(issue1, issue2, coef = 1) : 

    #if isinstance(issue1, float) or isinstance(issue2 float) : 
    #    return 0
    #else :  
    #    if str(notice1["issue"]).lower().strip()==str(notice2["issue"]).lower().strip() : 
    #        return 1    
    #    else : 
    #        return -1
    return check(issue1, issue2, coef = 1)

def compare_source(source1, source2, coef = 1) : 
    if not source1 or not source2 : 
        return source1, source2, [0.1*coef, 1]
    else : 
        if source1 == source2 : 
            return source1, source2, [0.9*coef,1]
        else : 
            return source1, source2, [0.9*coef,-1]


def compare_meeting(meeting1, meeting2, coef = 1) : 
    return check(meeting1, meeting2, coef) 

def compare_doc_type(doc_type1, doc_type2, coef = 1) : 
    return check(doc_type1, doc_type2, coef)

def compare_issn(issn1, issn2, coef = 1) : 
    return check(issn1, issn2, coef)

def compare_eissn(eissn1, eissn2, coef = 1) : 
    return check(eissn1, eissn2, coef)

def compare_journal(journal1, journal2, coef = 1) : 
    return check(journal1, journal2, coef)


def compare_nnt(nnt1, nnt2, coef = 1): 
    return check(nnt1,nnt2, coef)

def compare_ppn(ppn1, ppn2, coef = 1): 
    return check(ppn1,ppn2, coef)

def compare_volume(volume1, volume2, coef = 1): 
    return check(volume1,volume2, coef)


def compare_settlement(settlement1,settlement2, coef = 1) :
    
    if not (settlement1 and settlement2) :
        return [0.1, 1]

    else : 
        try : 
            begin_date1 = settlement1.find("date",attrs={"type" : "start"}).text
            begin_date2 = settlement2.find("date",attrs={"type" : "start"}).text
        except :
             begin_date1 = None
             begin_date2 = None

        try : 
            end_date1 = settlement1.find("date",attrs={"type" : "end"}).text
            end_date2 = settlement2.find("date",attrs={"type" : "end"}).text
        except : 
            end_date1 = None
            end_date2 = None

        try : 
            settlement1 = settlement1.find("settlement").text
            settlement2 = settlement2.find("settlement").text
        except : 
            settlement1 = None
            settlement2 = None

        if begin_date1 and begin_date2 : 
            return check(begin_date1, begin_date2)

        elif settlement1 and settlement2 : 
            return check(settlement1, settlement2)

        elif end_date1 and end_date2 : 
            return check(end_date1, end_date2)

        else : 
            return [0.1*coef, 1]

def compare_default_title(td1, td2, threshold = .2) : 

    dist = sentenceDistance(str(td1), str(td2))
    if dist > threshold : 
        return [0.9, -1]
    else : 
        return [0.9, 1] 


#####################################

# Compute matching function
#n1 = Notice(notice1)
#n2 = Notice(notice2)


def compare_notice(n1, n2, coef_dict = coef_dict, threshold = 0.2) : 

    # Recuperer les champs utiles
    dico = {}

    # titledefault
    dico["default_title"] = compare_default_title(n1.default_title,\
         n2.default_title, coef_dict['default_title'])       

    # source: sudoc
    if n1.source == "sudoc" or n2.source == "sudoc": 
        
        # nnt
        dico["nnt"] = compare_issue(n1.nnt, n2.nnt, coef_dict["nnt"])
        
        # publi_date
        dico["publi_date"] = compare_publi_date(n1.publi_date, n2.publi_date, coef_dict['publi_date'])

    
    else :
        # doi 
        dico["doi"] = compare_doi(n1.doi, n2.doi, coef_dict["doi"])

        # issn
        dico["eissn"] = compare_eissn(n1.eissn, n2.eissn, coef_dict["eissn"])
        
        # eissn
        dico["issn"] = compare_issn(n1.issn, n2.issn, coef_dict["issn"])

        # settlement
        dico["settlement"] = compare_settlement(n1.settlement, n2.settlement,coef_dict["settlement"])

        # meeting
        dico["meeting"] = compare_meeting(n1.meeting, n2.meeting, coef_dict["meeting"])

        # issue
        dico["issue"] = compare_issue(n1.issue, n2.issue, coef_dict["issue"])

        # volume
        dico["volume"] = compare_volume(n1.volume, n2.volume, coef_dict["volume"])

        # page_range
        dico["page_range"] = compare_page_range(n1.page_range, n2.page_range, coef_dict["page_range"])

    return dico
    
    
def get_validation(dico, ratio = ratio) : # publi_date
    try : 

        length = len(dico)
        count_dup = 0
        count_not_dup = 0
        count_near_dup = 0
        
        for _, value in dico.items() :
            if value == [0.9, 1] :
                count_dup+=1

            elif value == [0.1,1] : 
                count_near_dup += 1 

            else :  
                count_not_dup += 1 
            
        if count_not_dup > 0 : 
            return 0

        elif count_near_dup >= int(length*ratio) : 
            return 0

        else : 
            return 1

    except : 
        return 0 


###############################################

# Class for compute comparison

def get_notice_from_sourceUid(sourceUid, df): 
    if not isinstance(sourceUid, str) : 
        sourceUid = str(sourceUid)
    n_serie = df[df.sourceUid == sourceUid]
    t = n_serie.T.to_json()
    t_json = list(json.loads(t).values())[0]
    return t_json

class NoticeComparison : 

    def __init__(self, list_of_sourceUid1, list_of_sourceUid2, df, ratio) : 
        self.list_of_sourceUid1 = list_of_sourceUid1
        self.list_of_sourceUid2 = list_of_sourceUid2
        self.ratio = ratio
        self.df = df
        self.dataframe = []
        self.validation = []

    def compare_notice(self) : 
        for x,y in zip(self.list_of_sourceUid1, self.list_of_sourceUid2) : 
            temp1 = self.Record(get_notice_from_sourceUid(x, self.df))
            temp2 = self.Record(get_notice_from_sourceUid(y, self.df))
            dictionary = compare_notice(temp1, temp2)
            result = get_validation(dictionary, self.ratio)
            self.dataframe.append(result)
            self.validation.append((x, y, result))

    def is_done(self) : 
        if len(self.dataframe) == len(self.list_of_sourceUid1) : 
            return True
        else : 
            return False

    def get_stats(self, y) :
        try :
            if self.is_done() == True :  
                prec = precision_score(y, self.dataframe)
                recall = recall_score(y, self.dataframe)
                f1 = f1_score(y, self.dataframe)
                conf = confusion_matrix(y, self.dataframe)
                return {"Precision": round(prec,3), 
                        "Recall" : round(recall,3),
                        "f1_score" : round(f1,3),
                        "confusion_matrix" : conf
                }

        except Exception as err : 
            return err 

            
    class Record(Notice) : 
        pass
        