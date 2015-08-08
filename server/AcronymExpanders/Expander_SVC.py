import string

import numpy
from sklearn.externals import joblib
from sklearn.svm.classes import LinearSVC

from AcronymExpanders import AcronymExpanderEnum
from AcronymExpanders.AcronymExpander import AcronymExpander

from Logger import common_logger
import string_constants
from helper import AcronymExpansion


class Expander_SVC(AcronymExpander):

    def __init__(self, articleDB, acronymDB):
        self.vectorizer = joblib.load(string_constants.file_vectorizer)
        AcronymExpander.__init__(self, articleDB, acronymDB)
        #super(Expander_SVC, self).__init__(articleDB, acronymDB)
        common_logger.info("TFIDF vectorizer loaded")
        common_logger.info("Expander_SVC loaded")

    def expand(self, acronym, acronymExpansion, text):
        choices = self.getChoices(acronym)

        if(len(choices) == 0):
            #todo: uncomment below line
            #common_logger.warning("No expansion for %s in\n{%s}", acronym, text)
            return acronymExpansion
        elif not AcronymExpansion.areDistinctChoices(choices):
            acronymExpansion.expansion = choices[0].expansion
            acronymExpansion.expander = AcronymExpanderEnum.SVC
        else:
            definitions = [choice.expansion for choice in choices]
            articles = [choice.article_text for choice in choices]
            X = self.vectorizer.transform(articles)
            Y = definitions

            classifier = LinearSVC(C=1., loss="l1")
            classifier.fit(X, Y)
            
            #unicode transform works differently, see http://stackoverflow.com/a/11693937/681311
            remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
            s = self.vectorizer.transform(
                [text.translate(remove_punctuation_map)])  # todo:
            acronymExpansion.expansion = classifier.predict(s)[0]
            acronymExpansion.expander = AcronymExpanderEnum.SVC

        return acronymExpansion

    #def distinct_results(self, choices):
    #    count = len(choices)
    #    if(count <= 1):
    #        return False
    #    else:
    #        res1 = choices[0].expansion.strip().lower().replace('-', ' ')
    #        res1 = ' '.join([w[:4] for w in res1.split()])
    #        res2 = choices[-1].expansion.strip().lower().replace('-', ' ')
    #        res2 = ' '.join([w[:4] for w in res2.split()])
    #        if res1 != res2:
    #            return True
    #        return False
