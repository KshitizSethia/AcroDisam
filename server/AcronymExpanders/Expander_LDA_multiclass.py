from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm.classes import LinearSVC

from AcronymExpanders.Expander_LDA import Expander_LDA
from helper import AcronymExpansion
from gensim.matutils import sparse2full
from AcronymExpanders import AcronymExpanderEnum


class Expander_LDA_multiclass(Expander_LDA):
    """
    take LDA vectors of labelled articles and do a multi-class
    classification for deciding where the LDA of the test text belongs
    """

    def __init__(self, articleDB, acronymDB):
        Expander_LDA.__init__(self, articleDB, acronymDB)
        self.expander_type = AcronymExpanderEnum.LDA_multiclass

    def getChosenExpansion(self, choices, target_lda):
        chosenExpansion = ""
        if(len(choices)==0):
            return chosenExpansion
        
        train_x = [self.getDenseVector(self.articleIDToLDADict[choice.article_id])
                   for choice in choices]
        train_y, labelToExpansion = self.processChoices(choices)
        test_x = [self.getDenseVector(target_lda)]

        model = OneVsRestClassifier(LinearSVC()).fit(train_x, train_y)

        predicted_label = model.predict(test_x)[0]
        chosenExpansion = labelToExpansion[predicted_label]
        return chosenExpansion

    def getDenseVector(self, lda_vec):
        return sparse2full(lda_vec,self.ldamodel.num_topics)
    
    @staticmethod
    def processChoices(choices):

        indexToClass = []
        labelToExpansion = {}

        if(len(choices) == 0):
            return indexToClass, labelToExpansion

        indexToClass = [index for index in range(len(choices))]
        labelToExpansion[0] = choices[0].expansion

        for indexAhead in range(1, len(choices)):
            new_exp = choices[indexAhead].expansion
            newIsUnique = True

            for label, expansion in labelToExpansion.items():
                if AcronymExpansion.areExpansionsSimilar(expansion, new_exp):
                    newIsUnique = False
                    indexToClass[indexAhead] = label
                    break

            if(newIsUnique):
                new_class_label = len(labelToExpansion.keys())
                labelToExpansion[new_class_label] = new_exp
                indexToClass[indexAhead] = new_class_label

        return indexToClass, labelToExpansion
