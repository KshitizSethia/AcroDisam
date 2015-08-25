import os

from AcronymExpanders import AcronymExpanderEnum
from AcronymExpanders.AcronymExpander import PredictiveExpander
from AcronymExpanders.Expander_LDA_cossim import Expander_LDA_cossim
from AcronymExpanders.Expander_LDA_multiclass import Expander_LDA_multiclass
from AcronymExpanders.Expander_Tfidf_multiclass import Expander_Tfidf_multiclass
from AcronymExpanders.Expander_fromText import Expander_fromText
from AcronymExpanders.Expander_fromText_v2 import Expander_fromText_v2
from helper import AcronymExpansion, ExpansionChoice
from string_constants import min_confidence, folder_upload,\
    string_error_no_results_to_show


class Controller():  # todo: find better name
    """
    Class to process (text/pdf files) and expand the acronyms in it
    """

    supported_extensions = ["txt", "pdf"]

    def __init__(self, text_extractor,
                 acronym_extractor,
                 expanders,
                 articleDB,
                 acronymDB,
                 ldaModelAll=None,
                 vectorizer=None):
        """
        Args:
        text_extractor (TextExtractors.TextExtractor)
        acronym_extractor (AcronymExtractors.AcronymExtractor)
        expanders (list): list of AcronymExpanderEnum to indicate which expanders to use
        """
        self.acronymExpanders = expanders
        self.textExtractor = text_extractor
        self.acronymExtractor = acronym_extractor
        self.articleDB = articleDB
        self.acronymDB = acronymDB
        self.ldaModelAll = ldaModelAll
        self.vectorizer = vectorizer

    def supportsFile(self, filename):
        """
        Is file type supported?
        Args:
        filename (string): input file name/path
        Returns: True/False
        """
        extension = filename.rsplit(".", 1)[1]
        return extension in Controller.supported_extensions

    def processText(self, text):
        """
        takes text and returns the expanded acronyms in it
        Args:
        file_text: text to expand acronyms in. Use extractText API to get text from file
        Returns:
        dict(acronym (unicode): list(helper.AcronymExpansion) )
        """

        acronyms = self.acronymExtractor.get_acronyms(text)
        for acronym, expansions in acronyms.items():
            X_train, y_train, labelToExpansion = self._getChoices(acronym)

            for expander_type in self.acronymExpanders:
                expander = self._createExpander(expander_type)

                # check if this is a suitable problem for predictive expanders
                if(isinstance(expander, PredictiveExpander)):
                    if(len(X_train) == 0):
                        # no point using prediction, no training data
                        # move to next expander
                        continue
                    if(len(labelToExpansion) == 1):
                        # no point using prediction, all same class
                        # predict as the only present class
                        expansion = AcronymExpansion(
                            expansion=labelToExpansion[0],
                            expander=expander.getType,
                            confidence=min_confidence)
                        expansions.append(expansion)
                        continue

                X_transformed = expander.transform(X_train)

                expander.fit(X_transformed, y_train)

                X_test = expander.transform(
                    [ExpansionChoice(article_id=None, article_text=text)])

                results, confidences = expander.predict(X_test, acronym)
                result = results[0]
                confidence = confidences[0]

                if(isinstance(expander, PredictiveExpander)):
                    # always predicts, no need to check for None
                    expansions.append(AcronymExpansion(expansion=labelToExpansion[
                        result],
                        expander=expander.getType(),
                        confidence=confidence))
                else:
                    # expansion from non-predictive may sometimes be None
                    if(result):
                        expansions.append(
                            AcronymExpansion(expansion=result,
                                             expander=expander.getType(),
                                             confidence=confidence))

            acronyms[acronym] = self._chooseAmongstExpansions(expansions)

        return acronyms

    def _createExpander(self, expander_type):
        if(expander_type == AcronymExpanderEnum.fromText):
            return Expander_fromText()
        elif(expander_type == AcronymExpanderEnum.fromText_v2):
            return Expander_fromText_v2()
        elif(expander_type == AcronymExpanderEnum.LDA_cossim):
            if(not self.ldaModelAll):
                raise ValueError("LDA model not given to controller")
            return Expander_LDA_cossim(self.ldaModelAll)
        elif(expander_type == AcronymExpanderEnum.LDA_multiclass):
            if(not self.ldaModelAll):
                raise ValueError("LDA model not given to controller")
            return Expander_LDA_multiclass(self.ldaModelAll)
        elif(expander_type == AcronymExpanderEnum.Tfidf_multiclass):
            if(not self.vectorizer):
                raise ValueError("vectorizer not given to controller")
            return Expander_Tfidf_multiclass(self.vectorizer)

    def _chooseAmongstExpansions(self, expansions):
        """
        choose between expansions from all algos
        inputs:
        expansions (list): of helper.AcronymExpansion
        returns:
        list of chosen helper.AcronymExpansion to be put in final results
        """
        if expansions:
            return [expansions[0]]
        return expansions

    def _getChoices(self, acronym):
        """
        takes in an acronym, returns the choices in the following form
        returns:
        X_train (list): of helper.ExpansionChoice
        y_labels (list): of integer labels associated with each entry in X_train
        labelToExpansion (dict): to convert label number to expansion 
        """
        # get matches from acronymDB
        matches = []
        # todo: get acronymDB in self
        if(acronym in self.acronymDB):
            matches += self.acronymDB[acronym]
        if(acronym[-1] == "s" and acronym[:-1] in self.acronymDB):
            matches += self.acronymDB[acronym]

        # create training data
        X_train, y_train = [], []
        for definition, articleID, def_count in matches:
            text = self.articleDB[articleID]
            X_train.append(
                ExpansionChoice(article_id=articleID, article_text=text))
            y_train.append(definition)

        # create y labels to group similar acronyms
        y_labels, labelToExpansion = self._processChoices(y_train)

        return X_train, y_labels, labelToExpansion

    def _processChoices(self, acronym_expansions):
        """
        input: list(acronym expansion strings)
        returns:
        y_labels (list): of integer labels assigned to acronym expansions
        labelToExpansion (dict): to convert label number to acronym expansion  
        """
        y_labels = []
        labelToExpansion = {}

        if(len(acronym_expansions) == 0):
            return y_labels, labelToExpansion

        y_labels = [index for index in range(len(acronym_expansions))]
        labelToExpansion[0] = acronym_expansions[0]

        for indexAhead in range(1, len(acronym_expansions)):
            new_expansion = acronym_expansions[indexAhead]
            newIsUnique = True

            # check if new_expansion is same as a previous expansion
            # if same assign previous label and move on
            for label, expansion in labelToExpansion.items():
                if(AcronymExpansion.areExpansionsSimilar(expansion, new_expansion)):
                    newIsUnique = False
                    y_labels[indexAhead] = label
                    break
            # if label is new indeed, then give it a label ID (integer) and
            # make an entry in the labelToExpansion dictionary
            if(newIsUnique):
                new_class_label = len(labelToExpansion)
                labelToExpansion[new_class_label] = new_expansion
                y_labels[indexAhead] = new_class_label

        return y_labels, labelToExpansion

    def extractText(self, filename):
        """Extract text from file pointed to by filename"""
        file_path = os.path.join(folder_upload, filename)
        file_text = self.textExtractor.get_text(file_path)
        return file_text

    def writeOutputToFile(self, expanded_acronyms, file_path):
        """
        format output from processText to print to a file
        Args:
        expanded_acronyms (dict): with acronym (unicode) as key and AcronymExpansion as value
        file_path (string): file path for pretty printing the results
        Returns: None
        """
        output_file = open(file_path, "w")
        if expanded_acronyms:
            for acronym in sorted(expanded_acronyms.keys()):
                output_file.write(
                    acronym + "," + str(expanded_acronyms[acronym]) + "\n")
        else:
            output_file.close(string_error_no_results_to_show)
        output_file.close()

    def getOutputFilename(self, filename):
        """append .txt to the filename, that is the format results are stored"""
        return filename[:-4] + ".txt"
