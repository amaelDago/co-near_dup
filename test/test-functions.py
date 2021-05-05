# -*- coding : utf-8 -*-

import sys
parent_dir = "."
sys.path.insert(0, parent_dir)

import json
#from utils2 import compare_doi
from utils import *

with open("example/test.json", "r") as f : 
    test = json.load(f)

notice = test[0]

# Instanciate example
notice_test = Notice(notice)

#class TestNotice(unittest.TestCase) : 
def test_check_page_range() : 
    assert check_page_range("1444-1449", "1444-9") == 1
    assert check_page_range("1544-1550", "1544-50") ==  1
    assert check_page_range("1544-1549", "1544-549") == 1
    assert check_page_range("1544-1550", "1544") == 1
    assert check_page_range("1544-1550", "1550") == -1 # but to check
    assert check_page_range("1544-1550", "1551") == -1
    assert check_page_range("1544-1546", "1544-15447") == -1
    assert check_page_range("1544-1550", "154") == -1
    assert check_page_range("1544-1550", "155") == -1
    assert check_page_range("1544-1550", None) == 0
    assert check_page_range(None, None) == 0


def test_compare_doi() : 
    doi1 = notice_test.doi
    doi2 = doi1
    assert compare_doi(doi1, doi2) == [0.9,1]
    assert compare_doi(doi1, None) == [0.1,1]
    assert compare_doi(None, doi2) == [0.1,1]
    assert compare_doi(None, None) == [0.1,1]
    assert compare_doi(doi1, doi2[:-1]) == [0.9,-1]


def test_compare_publi_date() : 
    pd1 = notice_test.publi_date
    pd2 = pd1
    assert compare_publi_date(pd1, pd2) == [0.9,1]
    assert compare_publi_date(pd1, None) == [0.1,1]
    assert compare_publi_date(None, pd2) == [0.1,1]
    assert compare_publi_date(None, None) == [0.1,1]
    assert compare_publi_date(pd1, "26/11/1192") == [0.9,-1]


def test_levenshtein_distance() : 
    assert levenshtein_distance(notice_test.default_title, notice_test.default_title) == 0
    assert levenshtein_distance(notice_test.default_title, notice_test.default_title[:-10]) == 10
    assert levenshtein_distance(notice_test.default_title[5:], notice_test.default_title[:-5]) == 10
    assert levenshtein_distance("C'est un essai à tester","C'est un essai a tester") == 1


def test_check() :
    assert check(['2012/10/12'], ['2012/10/12']) == 1
    assert check(['2012/10/12'], ['2012']) == 1
    assert check(['2012'], ['2012/10/12']) == 1
    assert check('2012/10/12', None) == 0
    assert check(None, ['2012/10/12']) == 0
    assert check(None, None) == 0
    assert check('2012/10/12', "") == 0
    assert check(1,0) == -1
    assert check(float("nan"), 0.555) == 0
    assert check("", "") == 0
    assert check("this is a test", "a test") == 1
    assert check("this is a test", "that is a test") == -1
    assert check(0.755, 0.7776) == -1

def test_compare_source() : 
    source1 = notice_test.source
    source2 = source1
    assert compare_source(source1, source2) == ("hal","hal", [0.9,1])
    assert compare_source(source1, None) == ("hal",None, [0.1,1])
    assert compare_source(None, source2) == (None,"hal", [0.1,1])
    assert compare_source(None, None) == (None,None, [0.1,1])
    assert compare_source(source1, "crossref") == ("hal","crossref", [0.9,-1])



def test_compare_issue():
    issue1 = 10
    issue2 = issue1
    assert compare_issue(issue1, issue2) == 1
    assert compare_issue(issue1, None) == 0
    assert compare_issue(None, issue2) == 0
    assert compare_issue(None, None) == 0
    assert compare_issue(issue1, 100) == -1    


def test_compare_meeting():
    meeting1 = notice_test.meeting
    meeting2 = meeting1
    assert compare_meeting(meeting1, meeting2) == [0.9,1]
    assert compare_meeting(meeting1, None) == [0.1,1]
    assert compare_meeting(None, meeting2) == [0.1,1]
    assert compare_meeting(None, None) == [0.1,1]
    assert compare_meeting(meeting1, "") == [0.1,1] 


def test_compare_doc_type():
    doc_type1 = notice_test.doc_type
    doc_type2 = doc_type1
    assert compare_doc_type(doc_type1, doc_type2) == 1
    assert compare_doc_type(doc_type1, None) == 0
    assert compare_doc_type(None, doc_type2) == 0
    assert compare_doc_type(None, None) == 0
    assert compare_doc_type(doc_type1, "") == 0

def test_compare_settlement(): 
    settlement1 = notice_test.settlement
    settlement2 = settlement1
    assert compare_settlement(settlement1, settlement2) == 1
    assert compare_settlement(settlement1, None) == 0
    assert compare_settlement(None, settlement2) == 0
    assert compare_settlement(None, None) == 0
    assert compare_settlement(settlement1, "") == 0
    #assert compare_meeting(settlement1, "unknown") == [0.1,1]

def test_compare_issn() :
    pass

def test_compare_eissn() :
    pass

def test_compare_meeting() :
    pass


# def test_compare_notice() : 
#     assert compare_notice(notice_test, notice_test)[1] == 1
#     n = notice_test.copy()
#     n.default_title = "test du titre très différents du premier."
#     assert compare_notice(notice_test, n)[1] == 0
#     n1 = notice_test.copy()
#     n1.doi = "doi inconnu"
#     assert compare_notice(notice_test, n1)[1] == 1
#     n2 = notice_test.copy()
#     n2.doc_type = 'INCONNU'
#     assert compare_notice(notice_test, n2)[1] == 0
#     n3 = notice_test.copy()
#     n3.page_range = "0000"
#     n3.doc_type = "doi"
#     assert compare_notice(notice_test, n3)[1] == 0










