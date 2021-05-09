import json
from collections import Counter
from utils import check_page_range, check, compare_settlement, sentence_distance, Notice

def is_id_valid(doi1, doi2, nnt1, nnt2, pmId1, pmId2) : 
    """
    check if notice is valid for identifier
    """

    if doi1 and doi2 : 
        if doi1 == doi2 : 
            return "doi", 1
        return "doi", -1

    
    elif nnt1 and nnt2 : 
        if nnt1 == nnt2 : 
            return "nnt", 1
        return "nnt", -1


    elif pmId1 and pmId2 : 
        if pmId1 == pmId2 : 
            return "pmId", 1
        return "pmId", -1
    
    else : 
        return None, 0



def is_page_range_valid(page_range1,page_range2) : 
    
    if page_range1 and page_range2 : 
        return "page_range", check_page_range(page_range1, page_range2)

    return "page_range", 0  #, Coef

# def checkpoint1() : 
#     cp_id = is_id_valid()
#     cp_pr = is_page_range_valid()
#     if cp_id and cp_pr : 
#         continue
#     else : 
#         return 0, # 

def is_volumaison_valid(page_range1, page_range2, issue1, issue2, volume1, volume2) : 
    
    dictionary = {}
    dictionary["page_range"] = check_page_range(page_range1, page_range2)
    dictionary["issue"] = check_page_range(issue1, issue2)
    dictionary["volume"] = check_page_range(volume1, volume2)

    if dictionary["page_range"] == 1 : 

        if dictionary["issue"] == 1 : 
            return "issue",1
        
        elif dictionary["issue"] == -1 : 
            return "issue", -1

        elif dictionary["issue"] == 0 : 
            return "issue", 0

        elif dictionary['volume'] == 1 :
            return "volume", 1

        elif dictionary["volume"] == -1 : 
            return "volume", -1

        elif dictionary["volume"] == 0 : 
            return "volume", 0

    elif dictionary["page_range"] == -1 : # page range different ==> 
        return None, -1

    else : 
        return None, 0

# def checkpoint_volumaison(type_conditor1, type_conditor2, publi_date1, publi_date2) : 
#     if type_conditor1 == "Thèse" or type_conditor2 == "Thèse" : 
#         if is_volumaison_valid() == 0 : 
#             return 0

#         else : 
#             continue 


def is_container_valid(eissn1, eissn2, issn1, issn2, \
                       meeting1, meeting2, journal1, journal2,\
                       settlement1, settlement2,eisbn1, eisbn2, isbn1, isbn2) : 
    
    container_dict = {}
    container_dict["eissn"] = check(eissn1, eissn2)
    container_dict["issn"] = check(issn1, issn2)
    container_dict["meeting"] = check(meeting1, meeting2)
    container_dict["journal"] = check(journal1, journal2)
    container_dict["settlement"] = compare_settlement(settlement2, settlement2)
    container_dict["isbn"] = check(isbn1, isbn2)
    container_dict["eisbn"] = check(eisbn1, eisbn2)

    if container_dict["settlement"] :
        return "settlement", container_dict["settlement"]
        
    elif container_dict["meeting"] : 
        return "meeting", container_dict["settlement"]

    elif container_dict["issn"] : 
        return "issn", container_dict["issn"]

    elif container_dict['eissn'] : 
        return "eissn",container_dict["eissn"]

    elif container_dict["journal"] :
        return "journal", container_dict["journal"]

    elif container_dict["isbn"] : 
        return "isbn", container_dict["isbn"]

    else : 
        return None, 0

def checkpoint4() : 
    pass

def is_content_valid(default_title1,default_title2, threshold = 0.2) :
    dist = sentence_distance(default_title1, default_title2)
    if dist <= threshold : 
        return "default_title", 1
    else : 
        return "default_title", -1 


class NoticeComparison : 
    def __init__(self, notice1, notice2) : 

        self.n1 = self.Record(notice1)
        self.n2 = self.Record(notice2)
        self.validation_dict = {}
        self.status = None
        #self.decision_dict = {}

    def is_id_valid(self):
        self.validation_dict["id"] = is_id_valid(self.n1.doi, self.n2.doi,\
                            self.n1.nnt, self.n2.nnt,\
                            self.n1.pmId, self.n2.pmId
                        )
    
    def is_page_range_valid(self) : 
        #print('on', self.n1.page_range)
        self.validation_dict["page_range"] = is_page_range_valid(self.n1.page_range, self.n2.page_range)


    def checkpoint1(self) : 
        pass
        # if not self.validation_dict["id"] and \
        #     not self.validation_dict["page_range"] : 
        #     self.final_value = 0

    def is_volumaison_valid(self) : 
        self.validation_dict["volumaison"] = is_volumaison_valid(
            self.n1.page_range, self.n2.page_range,
            self.n1.issue, self.n2.issue, self.n1.volume, self.n2.volume
        )

    def checkpoint2(self) : 
        pass
    #     if not self.validation_dict["volumaison"] and \
    #         (self.n1.source == "Thèse" or self.n2.source == "Thèse") : 
    #         pass
            #self.status = 0

    def is_container_valid(self) : 
        self.validation_dict["container"] = is_container_valid(
            self.n1.eissn, self.n2.eissn, self.n1.issn, self.n1.issn,
            self.n1.meeting, self.n2.meeting, self.n1.journal, self.n2.journal,
            self.n1.settlement, self.n2.settlement,
            self.n1.eisbn, self.n2.eisbn, self.n1.isbn, self.n2.isbn 
        )
    
    def checkpoint3(self):
        pass

    def is_content_valid(self) : 
        self.validation_dict["content"] = is_content_valid(
            self.n1.default_title, self.n2.default_title
        )

    def checkpoint4(self) : 
        pass

    def run(self) : 
        self.is_id_valid()
        self.is_page_range_valid()
        self.checkpoint1()

        self.is_volumaison_valid()
        self.checkpoint2()

        self.is_container_valid()
        self.checkpoint3()

        self.is_content_valid()
        self.checkpoint4()

        self.status = "DONE"

    def is_done(self) : 
        if self.status == "DONE" :
            return 1

    def decision(self) : #, coef_dict) :
        if self.is_done() : 
            value = [x[1] for x in self.validation_dict.values()]
            
            if -1 in value :
                return -1

            elif 0 in value :
                return 0
            
            else : 
                return 1 
        
        else : 
            self.is_done()
            self.decision() 

    class Record(Notice):
        pass

#######################################

# Class for files comparison







if __name__ == "__main__" :     

    with open("example/test.json", "r") as f : 
        test = json.load(f)

    n1 = test[0]
    n2 = n1.copy()
    n2["doi"] = "autre_doi_inconnu" 

    #print(notice2.doi)
    comp = NoticeComparison(n1, n1)
    comp.run()
    print(comp.validation_dict)
    print(comp.decision())

    print("########################")
    comp = NoticeComparison(n1, n2)
    comp.run()
    print(comp.validation_dict)
    print(comp.decision())

    print("########################")
    n3 = n1.copy()
    n3["pageRange"] = 777
    n3["volume"] = 47
    pcomp = NoticeComparison(n1, n3)
    comp.run()
    print(1,comp.validation_dict)
    print(2, comp.decision())

    #print(is_volumaison_valid(47,47,None, None, 15,15))
    #print(is_page_range_valid(47,47))