import re

from AcronymExpanders import AcronymExpanderEnum
from AcronymExpanders.AcronymExpander import AcronymExpander
from helper import AcronymExpansion


class Expander_fromText_v2(AcronymExpander):
    """
    Changes over Expander_fromText:
    multiline regex
    regex will now look for more than one line breaks between expansions (changing between_chars1)
        needs a join on split up expansion: " ".join([word for word in pattern_result[0].split()])
    changing regex between_chars to support acronyms like: Integrated Definition (IDEF)
    """

    def __init__(self):
        # less confidence than fromText
        self.confidence = 0.9  

    def expand(self, acronym, acronymExpansions, text):
        patterns = self.definition_patterns(acronym)

        #common_logger.debug("Text:\n%s", text)

        for pattern in patterns:
            pattern_result = re.findall(pattern, text)
            if pattern_result and pattern_result[0] != acronym:
                                # todo: this assumption might be wrong
                # what if there's a document with different senses of an acronym
                # and disambiguation nearby
                expansion = " ".join(
                    [word for word in pattern_result[0].split()])
                acronymExpansions.append(
                    AcronymExpansion(expansion=expansion, expander=AcronymExpanderEnum.fromText_v2, confidence=self.confidence))
                return acronymExpansions

        return acronymExpansions

    def definition_patterns(self, acronym):
        def_pattern = r''
        between_chars1 = r'\w*[-.\s]*'  # (?:\w{2,5}[-\s]){0,1}'
        # between_chars2 = r'\w*[-\s]*(?:\w{2,5}[-\s]{0,1}){0,1}'
        after_chars = r"\w*"
        between_def_and_acronym = r"[-,\"'\(\s\w]{0,10}"
        for i, c in enumerate(acronym):
            c = "[" + c + "]"
            if i == 0:
                def_pattern += r'\b' + c + between_chars1
            elif i < len(acronym) - 1:
                # acronym letter, chars, periods, space
                def_pattern += c + between_chars1
            else:
                def_pattern += c + after_chars
        patterns = []
        patterns = patterns + ["(" + def_pattern + ")" + between_def_and_acronym + acronym,
                               acronym + between_def_and_acronym + "(" + def_pattern + ")"]
        # log the patterns
        #common_logger.debug("Acronym: %s, Patterns:", acronym)
        # for pattern in patterns:
        #    common_logger.debug(pattern)

        patterns = [
            re.compile(pattern, re.MULTILINE | re.IGNORECASE) for pattern in patterns]
        return patterns
