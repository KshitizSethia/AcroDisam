#import numpy
#
#from AcronymExpanders import AcronymExpanderEnum
#from Logger import common_logger
#from helper import ExpansionChoice
#import string_constants
#
from string_constants import min_confidence

class AcronymExpander:

    def __init__(self, expander_type):
        """
        inputs:
        expander_type: the AcronymExpanderEnum that this expander implements
        """
        self.type = expander_type

    def transform(self, X):
        """
        transforms input list to form accepted by fit and predict function
        inputs:
        X (list): of helper.ExpansionChoice
        returns:
        result (list): of inputs to predict and fit functions
        """
        pass

    def fit(self, X_train, y_train):
        """
        fits the current algo to training data
        inputs:
        X_train (list): of training input variables
        y_train (list): of training labels
        """
        pass

    def predict(self, X_test, acronym):
        """
        predicts the labels possible for test data
        inputs:
        X_test (list): of input data
        acronym (unicode): the acronym for which the expansion is being predicted  
        returns:
        labels (list): of labels for test data
        confidences (list): corresponding un-normalized confidence values
        """
        pass

    def getType(self):
        """
        returns: the AcronymExpanderEnum that this expander implements
        """
        return self.type


class PredictiveExpander(AcronymExpander):
    """
    for expanders which use a machine learning algo to expand acronyms 
    """
    
    def __init__(self, expander_type):
        AcronymExpander.__init__(self, expander_type)
        
    def _getConfidencesFromDecisionFunction(self, labels, decisions):
        confidences=[]
        for label, decision in zip(labels, decisions):
            confidence = min_confidence
            if (hasattr(decision, "__iter__")):
                confidence = decision[label]
            else:
                confidence = abs(decision)
            confidences.append(confidence)
        
        return confidences
