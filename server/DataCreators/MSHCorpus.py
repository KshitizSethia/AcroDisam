"""
convert <e> to ( or ""
convert </e> to ) or ""
regex extend: BLM (Bloom's syndrome protein)
"""
from csv import DictReader
import os
import re

import arff

from AcronymExpanders import AcronymExpanderEnum
from AcronymExpanders.Expander_fromText_v2 import Expander_fromText_v2
from Logger import common_logger
import TextTools
import cPickle as pickle
from helper import AcronymExpansion
from string_constants import folder_msh_arff, file_msh_articleDB,\
    file_msh_acronymDB, file_msh_articleIDToAcronymExpansions,\
    file_msh_manual_corrections, file_msh_articleDB_shuffled, max_confidence
import random
from collections import OrderedDict


def _removeMarkup(text):
    textWithoutMarkup = re.sub(u"\\<e\\>", u"", text)
    textWithoutMarkup = re.sub(u"\\<\\/e\\>", u"", textWithoutMarkup)
    return textWithoutMarkup


def _createArticleIDToAcronymExpansions(acronymDB):
    articleIDToAcronymExpansions = {}
    for acronym in acronymDB:
        for expansion, articleID, def_count in acronymDB[acronym]:
            if articleID not in articleIDToAcronymExpansions:
                articleIDToAcronymExpansions[articleID] = {}
            acronymExpansion = AcronymExpansion(
                expansion, AcronymExpanderEnum.none, confidence=max_confidence)
            articleIDToAcronymExpansions[articleID][
                acronym] = [acronymExpansion]

    return articleIDToAcronymExpansions


def _createArticleAndAcronymDB():
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
        # storing all acronyms as uppercase values
        acronym = _fileNameToAcronym(fileName).upper()
        cuid_and_pmid = []
        for line in lines:
            pmid = unicode(line.PMID)
            text = TextTools.toUnicode(line.citation)
            cuid = cuids[_classToIndex(line["class"])]
            textWithoutMarkup = _removeMarkup(text)
            if (cuid not in CUID_to_expansion):
                acronymExpansions = []
                acronymExpansions = acronymExpander.expand(
                    acronym, acronymExpansions, textWithoutMarkup)
                if (len(acronymExpansions) != 0 and
                        acronymExpansions[0].expansion != acronym):
                    CUID_to_expansion[cuid] = acronymExpansions[0].expansion
            if (pmid not in articleDB):
                articleDB[pmid] = textWithoutMarkup
            cuid_and_pmid.append([cuid, pmid])

        if (acronym in acronymDB):
            common_logger.error("acronym already present in acronymDB")
        else:
            acronymDB[acronym] = []
        for cuid, pmid in cuid_and_pmid:
            if (cuid in CUID_to_expansion):
                acronymDB[acronym].append([CUID_to_expansion[cuid], pmid, 0])
            else:
                common_logger.error(
                    "Expansion not found for CUID %s of %s" % (cuid, acronym))
                acronymDB[acronym].append([cuid, pmid, 0])

    return acronymDB, articleDB


def _createShuffledArticleDB(articleDB):
    items = articleDB.items()
    random.shuffle(items)
    shuffledArticleDB = OrderedDict(items)
    return shuffledArticleDB


def makeDBs():
    acronymDB, articleDB = _createArticleAndAcronymDB()

    acronymDB = applyManualCorrections(acronymDB)

    articleIDToAcronymExpansions = _createArticleIDToAcronymExpansions(
        acronymDB)

    shuffledArticleDB = _createShuffledArticleDB(articleDB)

    pickle.dump(articleDB, open(file_msh_articleDB, "wb"), protocol=2)
    pickle.dump(acronymDB, open(file_msh_acronymDB, "wb"), protocol=2)
    pickle.dump(articleIDToAcronymExpansions, open(
        file_msh_articleIDToAcronymExpansions, "wb"), protocol=2)
    pickle.dump(shuffledArticleDB, open(
        file_msh_articleDB_shuffled, "wb"), protocol=2)


def applyManualCorrections(acronymDB):
    for line in DictReader(open(file_msh_manual_corrections, "rb"), delimiter=","):
        acronym = TextTools.toUnicode(line["acronym"])
        wrong_exp = TextTools.toUnicode(line["wrong_expansion"])
        correct_exp = TextTools.toUnicode(line["correct_expansion"])

        for entry in acronymDB[acronym]:
            if entry[0] == wrong_exp:
                entry[0] = correct_exp

    return acronymDB


def _classToIndex(cls):
    return int(cls[1:]) - 1


def _fileNameToAcronym(fileName):
    return fileName.split("_")[0]

if __name__ == "__main__":
    makeDBs()
