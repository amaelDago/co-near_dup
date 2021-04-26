# -*- coding : utf-8 -*-

import sys
parent_dir = "."
sys.path.insert(0, parent_dir)

import json
#from utils2 import compare_doi
from utils import checkPR, levenshtein_distance, compare_doi, compare_publi_date

with open("example/test.json", "r") as f : 
    test = json.load(f)

n = test[0]


#class TestNotice(unittest.TestCase) : 
def test_checkPR() : 
    assert checkPR("1444-1449", "1444-9") == [0.9, 1]
    assert checkPR("1544-1550", "1544-50")==  [0.9, 1]
    assert checkPR("1544-1549", "1544-549") == [0.9, 1]
    assert checkPR("1544-1550", "1544") == [0.9, 1]
    assert checkPR("1544-1550", "1550") == [0.9, 1]
    assert checkPR("1544-1550", "1551") == [0.9, -1]
    #assert checkPR("1544-1546", "1544-15446") == -1
    #assert checkPR("1544-1550", "154") == -1
    assert checkPR("1544-1550", "155") == [0.9, -1]
    assert checkPR("1544-1550", None) == [0.1, 1]
    assert checkPR(None, None) == [0.1, 1]




def test_compare_doi() : 
    doi1 = n["doi"]
    doi2 = doi1
    assert compare_doi(doi1, doi2) == [0.9,1]
    assert compare_doi(doi1, None) == [0.1,1]
    assert compare_doi(None, doi2) == [0.1,1]
    assert compare_doi(None, None) == [0.1,1]
    assert compare_doi(doi1, doi2[:-1]) == [0.9,-1]


def test_compare_publi_date() : 
    pd1 = n["publicationDate"]
    pd2 = pd1
    assert compare_publi_date(pd1, pd2) == [0.9,1]
    assert compare_publi_date(pd1, None) == [0.1,1]
    assert compare_publi_date(None, pd2) == [0.1,1]
    assert compare_publi_date(None, None) == [0.1,1]
    assert compare_publi_date(pd1, "26/11/1192") == [0.9,-1]


def test_levenshtein_distance() : 
    assert levenshtein_distance(n["title"]["default"], n["title"]["default"]) == 0
    assert levenshtein_distance(n["title"]["default"], n["title"]["default"][:-10]) == 10
    assert levenshtein_distance(n["title"]["default"][5:], n["title"]["default"][:-5]) == 10
    assert levenshtein_distance("C'est un essai à tester","C'est un essai a tester") == 1


#def test


#def 



