

from Logger import logger
import string_constants
from AcronymExpanders import AcronymExpanderEnum
class AcronymExpander:
    
    def __init__(self):
        pass
    
    # filename is optional
    # returns dictionary of acronym:expansion and
    # a boolean to indicate if all acronyms have been expanded
    def try_to_expand_acronyms(self, text, expanded_acronyms, filename=""):
        self.filename = filename  # todo: temporary hack as Expander SVC requires file to text in two ways
        all_acronyms_expanded = True
        try:
            for (acronym, expansion) in expanded_acronyms.items():
                if(expansion.expander != AcronymExpanderEnum.none):
                    continue
                expansion = self.expand(acronym, expansion, text)
                if(expansion.expander == AcronymExpanderEnum.none):
                    all_acronyms_expanded = False
                expanded_acronyms[acronym] = expansion
        except IndexError:
            logger.error(string_constants.string_error_document_parse)  # todo print file name here
        return expanded_acronyms, all_acronyms_expanded
    
    def expand(self, acronym, acronymExpansion, text):
        """
        expand one acronym, to be implemented by subclass
        returns an AcronymExpansion instance
        """
        pass
