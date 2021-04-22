# -*- coding : utf-8 -*-

import sys
parent_dir = "../"
sys.path.insert(0, parent_dir)


from utils import *
#import unittest

#class TestNotice(unittest.TestCase) : 
def test_checkPR() : 
    assert checkPR("1444-1449", "1444-9") == 1
    assert checkPR("1544-1550", "1544-50")==  1
    assert checkPR("1544-1549", "1544-549") == 1
    assert checkPR("1544-1550", "1544") == 1
    assert checkPR("1544-1550", "1550") == 1


def test_levenshtein_distance() : 
    assert levenshtein_distance("this is a test", "that is a test.") == 3
    assert levenshtein_distance("C'est un essai à tester","C'est un essai a tester") == 1

