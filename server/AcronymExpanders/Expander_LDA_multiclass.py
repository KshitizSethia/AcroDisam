from sklearn.svm.classes import LinearSVC

from string_constants import min_confidence
from AcronymExpanders.Expander_LDA_cossim import Expander_LDA_cossim
from AcronymExpanders import AcronymExpanderEnum
from gensim.matutils import sparse2full


class Expander_LDA_multiclass(Expander_LDA_cossim):
    """
    take LDA vectors of labelled articles and do a multi-class
    classification for deciding where the LDA of the test text belongs
    """

    def __init__(self, ldaModelAll, expander_type=AcronymExpanderEnum.LDA_multiclass):
        Expander_LDA_cossim.__init__(self, ldaModelAll, expander_type)
        self.classifier = LinearSVC()

    def transform(self, X):
        results = Expander_LDA_cossim.transform(self, X)
        return [self._getDenseVector(item) for item in results]

    def _getDenseVector(self, sparse_vec):
        return sparse2full(sparse_vec, self.ldaModel.num_topics)

    def fit(self, X_train, y_train):
        self.classifier.fit(X_train, y_train)

    def predict(self, X_test, acronym):
        labels = self.classifier.predict(X_test)

        decisions = self.classifier.decision_function(X_test)

        confidences = self._getConfidencesFromDecisionFunction(
            labels, decisions)

        return labels, confidences
