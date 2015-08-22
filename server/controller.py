import os

from Logger import common_logger
from TextExtractors.Extract_PdfMiner import Extract_PdfMiner
import string_constants

class Controller():  # todo: find better name
    """
    Class to process (text/pdf files) and expand the acronyms in it
    """
    
    supported_extensions = ["txt", "pdf"]

    def __init__(self, text_extractor, acronym_extractor, expanders):
        """
        Args:
        text_extractor (TextExtractors.TextExtractor)
        acronym_extractor (AcronymExtractors.AcronymExtractor)
        expanders (list): list of AcronymExpanders.AcronymExpander
        """
        self.acronymExpanders = expanders
        self.textExtractor = text_extractor
        self.acronymExtractor = acronym_extractor

    def supportsFile(self, filename):
        """
        Is file type supported?
        Args:
        filename (string): input file name/path
        Returns: True/False
        """
        extension = filename.rsplit(".", 1)[1]
        return extension in Controller.supported_extensions

    def processText(self, file_text):
        """
        takes text and returns the expanded acronyms in it
        Args:
        file_text: text to expand acronyms in. Use extractText API to get text from file
        Returns:
        dict(acronym (unicode): list(helper.AcronymExpansion) ) 
        """
        # expand the acronyms
        expanded_acronyms = self.acronymExtractor.get_acronyms(file_text)
        for expander in self.acronymExpanders:
            expanded_acronyms, allDone = expander.try_to_expand_acronyms(
                file_text, expanded_acronyms)
            if(allDone):
                break

        return expanded_acronyms

    def extractText(self, filename):
        """Extract text from file pointed to by filename"""
        file_path = os.path.join(string_constants.folder_upload, filename)
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
            output_file.close(string_constants.string_error_no_results_to_show)
        output_file.close()

    def getOutputFilename(self, filename):
        """append .txt to the filename, that is the format results are stored"""
        return filename[:-4] + ".txt"
