import os

from AcronymExpanders.Expander_SVC import Expander_SVC
from AcronymExpanders.Expander_fromText_v2 import Expander_fromText_v2
from AcronymExtractors.AcronymExtractor_v1 import AcronymExtractor_v1
from Logger import logger
from TextExtractors.Extract_PdfMiner import Extract_PdfMiner
import string_constants


class Controller():  # todo: find better name

    def __init__(self):
        logger.info("Initializing Controller")
        self.acronymExpanders = [Expander_fromText_v2(), Expander_SVC()]
        logger.info("AcronymExpanders loaded")
        self.textExtractor = Extract_PdfMiner()
        logger.info("TextExtractor loaded")
        self.acronymExtractor = AcronymExtractor_v1()
        logger.info("AcronymExtractor loaded")

    def supportsFile(self, filename):
        extension = filename.rsplit(".", 1)[1]
        return extension in string_constants.allowed_extensions

    def processFile(self, filename):
        # expand the acronyms
        file_path = os.path.join(string_constants.folder_upload, filename)
        file_text = self.textExtractor.get_text(file_path)
        expanded_acronyms = self.acronymExtractor.get_acronyms(file_text)
        for expander in self.acronymExpanders:
            expanded_acronyms, allDone = expander.try_to_expand_acronyms(
                file_text, expanded_acronyms)
            if(allDone):
                break

        return expanded_acronyms

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
