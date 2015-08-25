from sklearn.svm.classes import LinearSVC

from AcronymExpanders import AcronymExpanderEnum
from AcronymExpanders.AcronymExpander import PredictiveExpander
import string

class Expander_Tfidf_multiclass(PredictiveExpander):

    def __init__(self, vectorizer, expander_type=AcronymExpanderEnum.Tfidf_multiclass):
        PredictiveExpander.__init__(self, expander_type)
        self.vectorizer=vectorizer
        self.classifier = LinearSVC(C=1., loss="l1") 

    def transform(self, X):
        # unicode transform works differently, see  
        # http://stackoverflow.com/a/11693937/681311
        remove_punctuation_map = dict(
                (ord(char), None) for char in string.punctuation)
        texts = [item.article_text.translate(remove_punctuation_map) for item in X]
        
        return self.vectorizer.transform(texts)
    
    def fit(self, X_train, y_train):
        self.classifier.fit(X_train, y_train)
        
    def predict(self, X_test, acronym):
        labels = self.classifier.predict(X_test)
        
        decisions = self.classifier.decision_function(X_test)
        
        confidences = self._getConfidencesFromDecisionFunction(labels, decisions)
        
        return labels, confidences
