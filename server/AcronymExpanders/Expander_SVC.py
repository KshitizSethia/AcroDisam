import string

import numpy
from sklearn.externals import joblib
from sklearn.svm.classes import LinearSVC

from AcronymExpanders import AcronymExpanderEnum, articleDB, acronymDB
from AcronymExpanders.AcronymExpander import AcronymExpander

from Logger import logger
import string_constants


class Expander_SVC(AcronymExpander):

    def __init__(self):
        self.vectorizer = joblib.load(string_constants.file_vectorizer)
        logger.info("TFIDF vectorizer loaded")

    def expand(self, acronym, acronymExpansion, text):
        choices = self.getChoices(acronym)

        if(len(choices) == 0):
            logger.warning("No expansion for %s in\n{%s}", acronym, text)
            return acronymExpansion
        elif not self.distinct_results(choices):
            acronymExpansion.expansion = choices[0].expansion
            acronymExpansion.expander = AcronymExpanderEnum.SVC
        else:
            definitions = [choice.expansion for choice in choices]
            articles = [choice.article_text for choice in choices]
            X = self.vectorizer.transform(articles)
            Y = definitions

            classifier = LinearSVC(C=1., loss="l1")
            classifier.fit(X, Y)
            s = self.vectorizer.transform(
                [text.translate(string.maketrans("", ""), string.punctuation)])  # todo:
            acronymExpansion.expansion = classifier.predict(s)[0]
            acronymExpansion.expander = AcronymExpanderEnum.SVC

        return acronymExpansion

    # todo: this should be done when generating the db?
    def distinct_results(self, choices):
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