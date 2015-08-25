from gensim.matutils import cossim

from AcronymExpanders import AcronymExpanderEnum
from AcronymExpanders.AcronymExpander import PredictiveExpander
import TextTools
from string_constants import min_confidence


class Expander_LDA_cossim(PredictiveExpander):
    """
    Expand acronyms based on their cosine similarity to the Latent Dirichlet Allocation
    vectors of articles containing expansions of the acronym
    """

    def __init__(self, ldaModelAll, expander_type=AcronymExpanderEnum.LDA_cossim):
        PredictiveExpander.__init__(self, expander_type)

        self.ldaModel = ldaModelAll.ldaModel
        self.dictionary = ldaModelAll.dictionary
        self.articleIDToLDADict = ldaModelAll.articleIDToLDADict
        self.stem_words = ldaModelAll.stem_words
        self.removeNumbers = ldaModelAll.removeNumbers

    def transform(self, X):
        results = []
        for input in X:
            if(input.article_id):
                results.append(self.articleIDToLDADict[input.article_id])
            else:
                cleaned_words = TextTools.\
                    getCleanedWords(
                        input.article_text, stem_words=self.stem_words, removeNumbers=self.removeNumbers)
                bow = self.dictionary.doc2bow(cleaned_words)
                lda_vector = self.ldaModel[bow]
                results.append(lda_vector)

        return results

    def fit(self, X_train, y_train):
        self.X_train_lda = X_train
        self.y_train_labels = y_train

    def predict(self, X_test, acronym):
        labels = []
        confidences = []
        for test_lda in X_test:
            similarities = map(
                lambda article_lda: cossim(article_lda, test_lda), self.X_train_lda)
            similarityByLabel = sorted(
                zip(similarities, self.y_train_labels), key=lambda item: item[0], reverse=True)

            chosen_label = similarityByLabel[0][1]
            max_similarity = similarityByLabel[0][0]

            similarityByLabelForNotChosen = [
                item for item in similarityByLabel if item[1] != chosen_label]

            confidence = min_confidence
            if(similarityByLabelForNotChosen):
                confidence = max_similarity - \
                    similarityByLabelForNotChosen[0][0]

            labels.append(chosen_label)
            confidences.append(confidence)
        
        return labels, confidences