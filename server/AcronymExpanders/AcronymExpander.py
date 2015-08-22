import numpy

from AcronymExpanders import AcronymExpanderEnum
from Logger import common_logger
import string_constants
from helper import ExpansionChoice


class AcronymExpander:

    # todo: not all expanders use articleDB and acronymDB, and getChoices. So
    # create a subclass for ones which do
    def __init__(self, articleDB, acronymDB):
        self.articleDB = articleDB
        self.acronymDB = acronymDB
        pass

    # filename is optional
    # returns dictionary of acronym:expansion and
    # a boolean to indicate if all acronyms have been expanded
    def try_to_expand_acronyms(self, text, expanded_acronyms):
        all_acronyms_expanded = True
        try:
            for (acronym, expansions) in expanded_acronyms.items():
                if(len(expansions)!=0):#todo: remove this check
                    continue
                expansions = self.expand(acronym, expansions, text)
                if(len(expansions)==0):
                    all_acronyms_expanded = False
                expanded_acronyms[acronym] = expansions
        except IndexError:
            # todo print file name here
            common_logger.error(string_constants.string_error_document_parse)
        return expanded_acronyms, all_acronyms_expanded

    def getChoices(self, acronym):
        """returns array of ExpansionChoice"""
        results = []
        if(acronym in self.acronymDB):
            results += self.acronymDB[acronym]
        if(acronym[-1] == "s" and acronym[:-1] in self.acronymDB):
            results += self.acronymDB[acronym[:-1]]
        choices = []
        for definition, articleid, def_count in results:
            text = self.articleDB[articleid]
            choices.append(ExpansionChoice(definition, articleid, text))
        return choices

    def expand(self, acronym, acronymExpansions, text):
        """
        expand one acronym, to be implemented by subclass
        returns an AcronymExpansion instance
        """
        pass
