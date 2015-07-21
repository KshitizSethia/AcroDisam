import re

from AcronymExtractors.AcronymExtractor import AcronymExtractor
import string_constants
from helper import AcronymExpansion
from AcronymExpanders import AcronymExpanderEnum


class AcronymExtractor_v1(AcronymExtractor):
    def get_acronyms(self, text):
        english_words = set(word.strip().lower() for word in open(string_constants.file_english_words))
        pattern = r'\b[A-Z]{3,8}s{0,1}\b'  # Limit length 8
        acronyms = re.findall(pattern, text)
        acronyms = [acronym for acronym in acronyms if acronym.lower() not in english_words]#todo: eliminates some acronyms like MOO
        result = {}
        for acronym in set(acronyms):
            result[acronym] = AcronymExpansion(string_constants.string_unexpanded_acronym, AcronymExpanderEnum.none)
        return result