from gensim.matutils import sparse2full
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm.classes import LinearSVC

from AcronymExpanders import AcronymExpanderEnum
from AcronymExpanders.Expander_LDA import Expander_LDA
from helper import AcronymExpansion
from Logger import common_logger
from string_constants import min_confidence


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
            return chosenExpansion, min_confidence
        
        train_x = [self.getDenseVector(self.articleIDToLDADict[choice.article_id])
                   for choice in choices]
        train_y, labelToExpansion = self.processChoices(choices)
        test_x = [self.getDenseVector(target_lda)]

        confidence = min_confidence
        #check if only one label in training, then return that label
        if(len(labelToExpansion)>1):
        
            model = OneVsRestClassifier(LinearSVC()).fit(train_x, train_y)
            predicted_label = model.predict(test_x)[0]
            
            decisions = model.decision_function(test_x)
            
            if(len(labelToExpansion)==2):
                confidence = abs(decisions[0][0])
            else:
                confidence = decisions[0][predicted_label]
        else:
            common_logger.warning("training data has just one label, predicting the only training label present")
            predicted_label=0
            confidence = min_confidence
        
        chosenExpansion = labelToExpansion[predicted_label]
        return chosenExpansion, confidence

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
