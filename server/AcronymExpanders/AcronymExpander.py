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
                #todo: see if this condition works
                confidence = decision[label]
            else:
                confidence = abs(decision)
            confidences.append(confidence)
        
        return confidences
    
    def _to2dList(self, array):
        if(array):
            if(hasattr(array[0], "__iter__")):
                return array
            else:
                return [array]
        else:
            return [array]
    # todo: not all expanders use articleDB and acronymDB, and getChoices. So
    # create a subclass for ones which do
    # def __init__(self, articleDB, acronymDB):
    #    self.articleDB = articleDB
    #    self.acronymDB = acronymDB
    #    pass
    #
    ## filename is optional
    # returns dictionary of acronym:expansion and
    # a boolean to indicate if all acronyms have been expanded
    # def try_to_expand_acronyms(self, text, expanded_acronyms):
    #    all_acronyms_expanded = True
    #    try:
    #        for (acronym, expansions) in expanded_acronyms.items():
    #            if(len(expansions)!=0):#todo: remove this check
    #                continue
    #            expansions = self.expand(acronym, expansions, text)
    #            if(len(expansions)==0):
    #                all_acronyms_expanded = False
    #            expanded_acronyms[acronym] = expansions
    #    except IndexError:
    #        # todo print file name here
    #        common_logger.error(string_constants.string_error_document_parse)
    #    return expanded_acronyms, all_acronyms_expanded
    #
    # def getChoices(self, acronym):
    #    """returns array of ExpansionChoice"""
    #    results = []
    #    if(acronym in self.acronymDB):
    #        results += self.acronymDB[acronym]
    #    if(acronym[-1] == "s" and acronym[:-1] in self.acronymDB):
    #        results += self.acronymDB[acronym[:-1]]
    #    choices = []
    #    for definition, articleid, def_count in results:
    #        text = self.articleDB[articleid]
    #        choices.append(ExpansionChoice(definition, articleid, text))
    #    return choices
    #
    # def expand(self, acronym, acronymExpansions, text):
    #    """
    #    expand one acronym, to be implemented by subclass
    #    returns an AcronymExpansion instance
    #    """
    #    pass
