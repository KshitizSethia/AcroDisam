from nltk.metrics.distance import edit_distance


class AcronymExpansion:
    """
    Class containing an acronym's expansion
    """

    def __init__(self, expansion, expander, confidence):
        """
        expansion: str of expansion
        expander: str (Enum) of expander
        confidence: float value of confidence in this expansion (ideally within [0,1])
        """
        self.expansion = expansion
        self.expander = expander
        self.confidence = confidence

    def __str__(self):
        return self.expander + "," + self.expansion

    @staticmethod
    def areDistinctChoices(choices):
        """
        Tell whether the choices are distinct
        """
        count = len(choices)
        if(count <= 1):
            return False
        else:
            res1 = choices[0].expansion.strip().lower().replace('-', ' ')
            res1 = ' '.join([w[:4] for w in res1.split()])
            res2 = choices[-1].expansion.strip().lower().replace('-', ' ')
            res2 = ' '.join([w[:4] for w in res2.split()])
            if res1 != res2:
                return True
            return False

    @staticmethod
    def startsSameWay(expansion_1, expansion_2):
        expansion_1 = expansion_1.strip().lower().replace("-", " ")
        expansion_2 = " ".join([word[:4] for word in expansion_2.split()])
        expansion_1 = " ".join([word[:4] for word in expansion_1.split()])
        if(expansion_2 == expansion_1):
            return True
        #    ed = distance.edit_distance(expansion_2, expansion_1)
        #    if ed < 3:
        #        return True
        return False

    @staticmethod
    def areExpansionsSimilar(expansion_1, expansion_2):
        expansion_1 = expansion_1.lower().replace(u"-", u" ")
        expansion_2 = expansion_2.lower().replace(u"-", u" ")
        #numActualWords = len(expansion_1)
        #numPredictedWords = len(expansion_2)

        if(expansion_1 == expansion_2
           or AcronymExpansion.startsSameWay(expansion_1, expansion_2)
           or edit_distance(expansion_1, expansion_2) <= 2):  # max(numActualWords, numPredictedWords)):
            return True

        return False


class ExpansionChoice:
    def __init__(self, article_id, article_text):
        #self.expansion = expansion
        self.article_id = article_id
        self.article_text = article_text


class SavedLDAModel:

    def __init__(self, ldaModel, dictionary, articleIDToLDADict, articleDBused, stem_words, numPasses, removeNumbers):
        self.ldaModel = ldaModel
        self.dictionary = dictionary
        self.articleIDToLDADict = articleIDToLDADict
        self.articleDBused = articleDBused
        self.stem_words = stem_words
        self.numPasses = numPasses
        self.removeNumbers = removeNumbers
