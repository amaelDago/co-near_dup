# Dictionary of coef

coef_dict = {
    "doi" : 1, 
    "nnt" : 1,
    "pmId" : 1,
    "doc_type" : 1,
    "default_title" : 1,
    "en" : 1,
    "fr" : 1,
    "meeting" : 1,
    "journal" : 1,
    "settlement" :1,  
    "issn" : 1,
    "eissn" : 1,
    'isbn' : 1,
    "eisbn" : 1,
    "source" : 1,
    "page_range" :1,
    "issue" : 1,
    "publi_date" : 1, 
    "volume" : 1
}

check_point_decision = {
    # With 2 parameters : id and pageRange
    (0,-1) : "missing id, different pageRange",
    (-1,-1) : "different id, different pageRange",
    (0, 0) : "missing id, missing pageRange",
    (1,-1) : "different pageRange",
    (-1, 1) : "different id",
    (-1, 0) : "different id",

    # Add one parameter : volumaison
    (0, 1, -1) : "different volumaison",
    (1 ,1, -1) : "different volumaison",
    (1, 0, -1) :  "different volumaison",

    # Add one parameters : settlement
    (0, 1, 0, 0) : "missing id, missing volumaison and publication information",
    (0, 1, 0, -1) : "different publication information",
    (0, 1, 1, 0) : "missing id and publication information",
    (0, 1, 1, -1) : "different publication information",
    (1, 0, 1, 0) : "missing publication information",
    (1, 0, 1, -1) : "different publication information",
    (1, 0, 0, 0) : "missing publication information",
    (1, 0, 0, 1) : "missing publication information",
    (1, 0, 0, -1) : "different publication information", 
    (1, 1, 0, 0) : "missing publication information",
    (1, 1, 0, -1) : "different publication information",
    (1, 1, 1, 0) : "missing publication information",
    (1, 1, 1, -1) : "different publication information",

    # Add final parameters :  title
    (0, 1, 0, 1, 1) : "duplicates",
    (0, 1, 0, 1, -1) : "not duplicates",
    (0, 1, 1, 1, 1) : "duplicates",
    (0, 1, 1, 1, -1) : "not duplicates",
    (1, 0, 1, 1, 1) : "duplicates",
    (1, 0, 1, 1, -1) : "not duplicates",
    (1, 1, 1, 1, 1) : "duplicates",
    (1, 1, 1, 1, -1) : "not duplicates",
}

ratio = 0.2
