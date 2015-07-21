import string

import numpy
from sklearn.externals import joblib
from sklearn.svm.classes import LinearSVC

from AcronymExpanders import AcronymExpanderEnum
from AcronymExpanders.AcronymExpander import AcronymExpander
import DataCreators.AcronymDB
import DataCreators.ArticleDB
from Logger import logger
import string_constants


class Expander_SVC(AcronymExpander):
    def __init__(self):
        self.vectorizer = joblib.load(string_constants.file_vectorizer)
        logger.info("TFIDF vectorizer loaded")
        self.acronymdb = DataCreators.AcronymDB.load()
        logger.info("AcronymDB loaded")
        self.articledb = DataCreators.ArticleDB.load()
        logger.info("ArticleDB loaded")
        
    def expand(self, acronym, acronymExpansion, text):
        choices = self.db_lookup(acronym)
        
        if(len(choices)==0):
            logger.warning("No expansion for %s in\n{%s}", acronym, text)
            return acronymExpansion
        elif not self.distinct_results(choices):
            acronymExpansion.expansion = choices[0][0]
            acronymExpansion.expander= AcronymExpanderEnum.SVC
        else:
            definitions, articles = choices[:, 0], choices[:, 1]
            X = self.vectorizer.transform(articles)
            Y = definitions
            
            classifier = LinearSVC(C=1., loss="l1")
            classifier.fit(X, Y)
            s = self.vectorizer.transform([text.translate(string.maketrans("", ""), string.punctuation)])#todo:
            acronymExpansion.expansion = classifier.predict(s)[0]
            acronymExpansion.expander = AcronymExpanderEnum.SVC
            
        return acronymExpansion
            
    # returns numpy array of [definition, article]
    def db_lookup(self, acronym):
        # get relevant expansions from acronymdb
        results = []
        # add singular expansions
        if(acronym in self.acronymdb):
            results += self.acronymdb[acronym]
        # add plural expansions
        if(acronym[-1] == "s" and acronym[:-1] in self.acronymdb):
            results += self.acronymdb[acronym[:-1]]
            
        # make choices from expansions
        choices = []
        for definition, articleid, title, def_count in results:
            text = self.articledb[articleid]
            choices.append([definition, text])
        return numpy.array(choices)
    
    
    def distinct_results(self, choices):  # doubt: should this be done when generating the db?
        count = len(choices)
        if(count <= 1):
            return False
        else:
            res1 = choices[0][0].strip().lower().replace('-', ' ')
            res1 = ' '.join([w[:4] for w in res1.split()])
            res2 = choices[-1][0].strip().lower().replace('-', ' ')
            res2 = ' '.join([w[:4] for w in res2.split()])
            if res1 != res2:
                return True
            return False
