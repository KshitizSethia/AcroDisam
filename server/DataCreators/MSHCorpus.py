"""
convert <e> to ( or ""
convert </e> to ) or ""
regex extend: BLM (Bloom's syndrome protein)
"""
import os

import arff

from AcronymExpanders import AcronymExpanderEnum
from AcronymExpanders.Expander_fromText_v2 import Expander_fromText_v2
from Logger import logger
import cPickle as pickle
from helper import AcronymExpansion
from string_constants import folder_msh_arff, file_msh_articleDB,\
    file_msh_acronymDB, file_msh_articleIDToAcronymExpansions
import re
import TextTools


def removeMarkup(text):
    textWithoutMarkup = re.sub(u"\\<e\\>", u"", text)
    textWithoutMarkup = re.sub(u"\\<\\/e\\>", u"", textWithoutMarkup)
    return textWithoutMarkup


def makeDBs():
    acronymExpander = Expander_fromText_v2()
    articleDB = {}
    acronymDB = {}
    CUID_to_expansion = {}
    for fileName in os.listdir(folder_msh_arff):

        filePath = os.path.join(folder_msh_arff, fileName)
        file_reader = arff.Reader(open(filePath, "rb"))
        # the iterator needs to be called for the self.relation part to be
        # initialized
        lines = list(file_reader)
        cuids = file_reader.relation.strip().split("_")
        acronym = _fileNameToAcronym(fileName)
        cuid_and_pmid = []
        
        for line in lines:
            pmid = unicode(line.PMID)
            text = TextTools.toUnicode(line.citation)
            cuid = cuids[_classToIndex(line["class"])]
            

            textWithoutMarkup = removeMarkup(text)

            if(cuid not in CUID_to_expansion):
                acronymExpansion = AcronymExpansion(
                    "", AcronymExpanderEnum.none)
                acronymExpander.expand(
                    acronym, acronymExpansion, textWithoutMarkup)
                if(acronymExpansion.expander != AcronymExpanderEnum.none
                   and acronymExpansion.expansion != acronym):
                    CUID_to_expansion[cuid] = acronymExpansion.expansion

            if(pmid not in articleDB):
                articleDB[pmid] = textWithoutMarkup

            cuid_and_pmid.append([cuid, pmid])

        if(acronym in acronymDB):
            logger.error("acronym already present in acronymDB")
        else:
            acronymDB[acronym] = []

        for cuid, pmid in cuid_and_pmid:
            if( cuid in CUID_to_expansion):
                acronymDB[acronym].append([CUID_to_expansion[cuid], pmid,0])
            else:
                logger.error("Expansion not found for CUID %s of %s" %(cuid, acronym))
                acronymDB[acronym].append([cuid, pmid,0])

    articleIDToAcronymExpansions = {}
    for acronym in acronymDB:
        for expansion, articleID, def_count in acronymDB[acronym]:
            if articleID not in articleIDToAcronymExpansions:
                articleIDToAcronymExpansions[articleID] = {}
                
            acronymExpansion = AcronymExpansion(expansion, AcronymExpanderEnum.none)
            articleIDToAcronymExpansions[articleID][acronym] = acronymExpansion

    pickle.dump(articleDB, open(file_msh_articleDB, "wb"), protocol=2)
    pickle.dump(acronymDB, open(file_msh_acronymDB, "wb"), protocol=2)
    pickle.dump(articleIDToAcronymExpansions, open(file_msh_articleIDToAcronymExpansions, "wb"),protocol=2)


def _classToIndex(cls):
    return int(cls[1:]) - 1


def _fileNameToAcronym(fileName):
    return fileName.split("_")[0]

if __name__ == "__main__":
    makeDBs()
