import os

from AcronymExtractors.AcronymExtractor_v1 import AcronymExtractor_v1
from Logger import logger
from TextExtractors.Extract_PdfMiner import Extract_PdfMiner
import string_constants


class Controller():  # todo: find better name

    def __init__(self, text_extractor, acronym_extractor, expanders):
        self.acronymExpanders = expanders
        self.textExtractor = text_extractor
        self.acronymExtractor = acronym_extractor

    def supportsFile(self, filename):
        extension = filename.rsplit(".", 1)[1]
        return extension in string_constants.allowed_extensions

    def processFile(self, file_text):
        # expand the acronyms
        expanded_acronyms = self.acronymExtractor.get_acronyms(file_text)
        for expander in self.acronymExpanders:
            expanded_acronyms, allDone = expander.try_to_expand_acronyms(
                file_text, expanded_acronyms)
            if(allDone):
                break

        return expanded_acronyms

    def extractText(self, filename):
        file_path = os.path.join(string_constants.folder_upload, filename)
        file_text = self.textExtractor.get_text(file_path)
        return file_text

    def writeOutputToFile(self, expanded_acronyms, file_path):
        output_file = open(file_path, "w")
        if expanded_acronyms:
            for acronym in sorted(expanded_acronyms.keys()):
                output_file.write(
                    acronym + "," + str(expanded_acronyms[acronym]) + "\n")
        else:
            output_file.close(string_constants.string_error_no_results_to_show)
        output_file.close()

    def getOutputFilename(self, filename):
        return filename[:-4] + ".txt"
