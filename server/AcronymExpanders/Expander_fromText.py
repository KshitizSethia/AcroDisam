from AcronymExpanders.AcronymExpander import AcronymExpander
import re
import string_constants
from Logger import logger
from AcronymExpanders import AcronymExpanderEnum


class Expander_fromText(AcronymExpander):
    
    def __init__(self):
        pass  # todo:
    
    def expand(self, acronym, acronymExpansion, text):
        patterns = self.definition_patterns(acronym)
        
        #logger.debug("Text:\n%s", text)
        
        for pattern in patterns:
            pattern_result = re.findall(pattern, text)
            if pattern_result:
                # todo: this assumption might be wrong
                # what if there's a document with different senses of an acronym
                # and disambiguation nearby
                acronymExpansion.expansion = pattern_result[0]
                acronymExpansion.expander = AcronymExpanderEnum.fromText
                return acronymExpansion  
            
        return acronymExpansion
        
    def definition_patterns(self, acronym):
        def_pattern1, def_pattern2 = r'', r''
        between_chars1 = r'\w{3,}[-\s](?:\w{2,5}[-\s]){0,1}'
        between_chars2 = r'\w+[-\s]{0,1}(?:\w{2,5}[-\s]{0,1}){0,1}'
        for i, c in enumerate(acronym):
            c = "[" + c + c.lower() + "]"
            if i == 0:
                def_pattern1 += r'\b' + c + between_chars1
                def_pattern2 += r'\b' + c + between_chars2
            elif i < len(acronym) - 1:
                def_pattern1 += c + between_chars1  # acronym letter, chars, periods, space
                def_pattern2 += c + between_chars2
            else:
                def_pattern1 += c + r'\w+\b'
                def_pattern2 += c + r'\w+\b'
        acronym = r'' + acronym + r'\b'
        patterns = []
        for def_pattern in [def_pattern1, def_pattern2]:
            patterns = patterns + [def_pattern + r'(?=\sor\s{0,1}(?:the\s){0,1}(?:a\s){0,1}' + acronym + r')',
                               def_pattern + r'(?=["(\s,]{2,}(?:or\s){0,1}(?:the\s){0,1}["]{0,1}' + acronym + r')',
                               r'(?<=' + acronym + r'\s\W)' + def_pattern]
        # log the patterns
        #logger.debug("Acronym: %s, Patterns:", acronym)
        #for pattern in patterns:
        #    logger.debug(pattern)        
        
        patterns = [re.compile(pattern) for pattern in patterns]
        return patterns