"""
collection of functions used to manipulate the acronymdb dictionary
acronymdb is a dictionary in the format:
(acronym: [array of [acronym_expansion, article_id]])

OLD FORMAT:(acronym: [array of [acronym_expansion, article_id, article_title]])
"""
import cPickle as pickle
import csv
import sys

from Logger import logger
import string_constants
import numpy
from string_constants import file_list_scraped_definitions


def createFromScrapedDefinitions():
    logger.info("Creating AcronymDB")
    csv.field_size_limit(sys.maxint)
    
    acronymDB = {}
    loaded_acronyms = 0
    for definition_file in file_list_scraped_definitions:
        # open as csv file with headers
        acronym_csv = csv.DictReader(open(definition_file, "rb"), delimiter=",")
    
        for row in acronym_csv:
            if(row["acronym"] not in acronymDB):
                acronymDB[row["acronym"]] = []
            acronymDB[row["acronym"]].append([row["acronym_expansion"]
                                              .strip().lower().replace('-', ' ')
                                              , row["article_id"]])
                                              # , row["article_title"]]) # title was part of old format
            loaded_acronyms += 1
            if(loaded_acronyms % 10000 == 0):
                logger.debug("loaded %d acronyms", loaded_acronyms)
        
    logger.info("adding def_count values to acronymDB")
    defs_per_acronym = [0] * 1000
    insts_per_def = [0] * 1000
    num_acronyms = len(acronymDB)    
    for acronym, values_for_this_acronym in acronymDB.items():
        values_for_this_acronym = sorted(values_for_this_acronym
                                         , key=lambda x:x[0])
        
        def_count = 0
        inst_count = 0
        expansion_of_last_acronym = values_for_this_acronym[0][0]
        #, article_title]\ # title was part of old format in the line below
        for index, [acronym_expansion, article_id]\
                            in enumerate(values_for_this_acronym):
            if is_same_expansion(acronym_expansion, expansion_of_last_acronym):
                inst_count += 1
                values_for_this_acronym[index].append(def_count)
                values_for_this_acronym[index][0] = expansion_of_last_acronym
            else:
                insts_per_def[min(inst_count, len(insts_per_def) - 1)] += 1
                inst_count = 0
                def_count += 1
                expansion_of_last_acronym = acronym_expansion
                values_for_this_acronym[index].append(def_count)
        defs_per_acronym[min(def_count, len(defs_per_acronym) - 1)] += 1
        acronymDB[acronym] = numpy.array(values_for_this_acronym)
                
    dump(acronymDB)
    logger.info("Dumped AcronymDB successfully")
    
def is_same_expansion(true_exp, pred_exp):
    true_exp = true_exp.strip().lower().replace("-", " ")
    pred_exp = " ".join([word[:4] for word in pred_exp.split()])
    true_exp = " ".join([word[:4] for word in true_exp.split()])
    if(pred_exp == true_exp):
        return True
    #    ed = distance.edit_distance(pred_exp, true_exp)
    #    if ed < 3:
    #        return True
    return False

def dump(acronymDB):
    pickle.dump(acronymDB
                 , open(string_constants.file_acronymdb, "wb")
                 , protocol=2)

def load():
    return pickle.load(open(string_constants.file_acronymdb, "rb"))

# def addAcronyms(acronymDB, acronyms):#todo: add acronyms and articles

if __name__ == "__main__":
    createFromScrapedDefinitions()
