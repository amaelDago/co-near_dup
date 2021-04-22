from bs4 import BeautifulSoup
import base64
from tqdm import tqdm
import numpy as np
import string
import unidecode
from unicodedata import normalize

# Def settlement
def getSettlement(notice) :
    tb = notice['teiBlob']
    tb_decoded = base64.b64decode(tb).decode('utf8')
    soup = BeautifulSoup(tb_decoded, "xml")
    t = soup.find("meeting")
    if t :
        return t
    else : 
        return ""



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



def check(x1, x2) : 
    # Check : Compare two object like int bool string list or tuple
    # 1 means can be the same and 0 not

    if isinstance(x1, str) and isinstance(x2, str) : 
        if (x1.lower().strip() in x2.lower().strip()) or (x2.lower().strip() in x1.lower().strip()): 
            return 1
        elif not x1 or not x2 :
            return 1
        else : 
            return 0
    
    elif isinstance(x1, (float, int, bool)) and isinstance(x2, (float, int, bool)) :
        if x1==x2 : 
            return 1
        else : 
            return 0
    
    elif isinstance(x1, (list, tuple)) and isinstance(x2, (list, tuple)) : 
        return check(x1[0], x2[0]) 
       
    else : # 1 one for missing value : 
        return 1


import math

def checkPR(x1, x2) :

    if not x1 or not x2 : 
        return 1
    
    elif isinstance(x1, float) and isinstance(x2, float): 
        if math.isnan(x1) or math.isnan(x2) : 
            return 1
        else : 
            if x1!=x2 : 
                return -1
    elif x1==x2 : 
        return 1
    else : 
        x1 = str(x1)
        x2 = str(x2)

        x1_l = [x for x in x1.strip().split("-") if x]
        x2_l = [x for x in x2.strip().split("-") if x]

        if x1_l == x2_l : 
            return 1

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
                        return 1

                else : 
                    #x11 = x1[:i].strip()
                    x12 = x1[i:].replace("-","").strip()
                    x22 = x2[i:].replace("-","").strip()

                    x121 = x12[:-len(x22)]
                    temp = x121 + x22

                    if temp == x12 : 
                        return 1
                    else : 
                        return -1
                    flag = False



#####################################
# 2 We define needed functions
#####################################

def checkDoi(notice1, notice2) : 

    if isinstance(notice1["doi"], float) or isinstance(notice2["doi"], float) : 
        return 0
    else :  
        if str(notice1["doi"]).lower().strip()==str(notice2["doi"]).lower().strip() : 
            return 1    
        else : 
            return -1

def checkPublicationDate(notice1, notice2) : 

    if isinstance(notice1["publicationDate"], float) or isinstance(notice2["publicationDate"], float) : 
        return 0
    else :  
        pd1 = str(notice1["publicationDate"]).lower().strip()
        pd2 = str(notice2["publicationDate"]).lower().strip()

        if pd1 in pd2 or pd2 in pd1 :  
            return 1    
        else : 
            return -1

def checkPageRange(notice1, notice2) : 

    if isinstance(notice1["pageRange"], float) or isinstance(notice2["pageRange"], float) : 
        return 0
    elif notice1['pageRange'] == "np" or notice2["pageRange"] == "np" : 
        return 0
    else :  
        return checkPR(notice1['pageRange'], notice2['pageRange'])

def checkIssue(notice1, notice2) : 

    if isinstance(notice1["issue"], float) or isinstance(notice2["issue"], float) : 
        return 0
    else :  
        if str(notice1["issue"]).lower().strip()==str(notice2["issue"]).lower().strip() : 
            return 1    
        else : 
            return -1

def checkSource(notice1, notice2) : 
    if not notice1["source"] or not notice2["source"]: 
        return 0
    else : 
        if notice1['source'] == notice2['source'] : 
            return notice1['source'],notice2['source'], 1
        else : 
            return notice1['source'],notice2['source'], -1


def checkMeeting(notice1, notice2) : 
    meeting1 = notice1['title']['meeting']
    meeting2 = notice2['title']['meeting']

    if not meeting1 or not meeting2 : 
        return 0
    else : 
        if meeting1 == meeting2: 
            return 1
        else : 
            return -1

def checkDocumentType(notice1, notice2) : 
    dt1 = notice1['documentType'][0]
    dt2 = notice2['documentType'][0]

    if not dt1 or not dt2 : 
        return 0
    else : 
        if dt1 == dt1: 
            return 1
        else : 
            return -1


def checkSettlement(notice1,notice2) :
    n1 = getSettlement(notice1)
    n2 = getSettlement(notice2)
    if not n1 or not n2 : 
        return 0
    else : 
        settlementBeginDate1 = n1.find("date",attrs={"type" : "start"})
        settlementEndDate1 = n1.find("date",attrs={"type" : "end"})

        settlementBeginDate2 = n2.find("date",attrs={"type" : "start"})
        settlementEndDate2 = n2.find("date",attrs={"type" : "end"})

        if (settlementBeginDate1 == settlementBeginDate2) and (settlementEndDate1 == settlementEndDate2) :
            return 1
        else : 
            return -1


def checkDefaultTitle(notice1, notice2) : 
    x1,x2 = str(notice1["title"]["default"]), str(notice2["title"]["default"])

    dist = sentenceDistance(notice1["title"]["default"], notice2["title"]["default"])

    return dist



def checkNotice(notice1, notice2, threshold = 0.1) : 

    x = checkDefaultTitle(notice1, notice2)

    if x>threshold : 
        return 0
    else : 
        source1,source2, value = checkSource(notice1, notice2)
        doi = checkDoi(notice1, notice2)
        meeting = checkMeeting(notice1, notice2)
        #journal = checkJournal(notice1, notice2)
        settlement = checkSettlement(notice1, notice2)
        pd = checkPublicationDate(notice1, notice2)
        dp = checkDocumentType(notice1, notice2)
        pr = checkPageRange(notice1, notice2)
        issue = checkIssue(notice1, notice2)

    #if source1 != source2 : 
        if doi == 1 : 
            if meeting >= 0 and settlement >= 0 : 
                return 1
            else : 
                return 0

        elif doi == 0 : 
            if (meeting and settlement and dp and issue)>=0 and pd==1 :
                return 1
            else :      
                return 0

        else :
            if (meeting and settlement and pd and pr and dp and issue) == 1 :
                return 1
            else :      
                return 0


