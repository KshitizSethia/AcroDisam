import functools
import gc
from multiprocessing import Pool

from AcronymExpanders import AcronymExpanderEnum
from AcronymExpanders.Expander_fromText import Expander_fromText
from AcronymExtractors.AcronymExtractor_v1 import AcronymExtractor_v1
from AcronymExtractors.AcronymExtractor_v2 import AcronymExtractor_v2
from Benchmarker.Benchmark import Benchmarker
from Logger import common_logger
from string_constants import file_articledb, file_acronymdb,\
    file_articledb_shuffled, file_lda_model_all, folder_lda, file_vectorizer
from AcronymExtractors.AcronymExtractor_v2_small import AcronymExtractor_v2_small
from DataCreators import LDAModel
from sklearn.externals import joblib
from TextExtractors.Extract_PdfMiner import Extract_PdfMiner


class Benchmarker_wiki(Benchmarker):

    def _getActualExpansions(self, articleID, article):
        extractor = AcronymExtractor_v1()
        acronymExpansions = extractor.get_acronyms(article)

        expander = Expander_fromText()
        actualExpansions, ignore_boolean = expander.try_to_expand_acronyms(
            article, acronymExpansions)

        result = [item for item in actualExpansions.items() if len(item)>0]

        return dict(result)

    def _removeInTextExpansions(self, article, acronyms):
        expander = Expander_fromText()

        for acronym in acronyms:
            for pattern in expander.definition_patterns(acronym):
                results = pattern.findall(article)
                for result in results:
                    article = article.replace(result, " ")

        self.__verifyRemovalOfInTextExpansions(article, acronyms)

        return article

    def __verifyRemovalOfInTextExpansions(self, article_for_testing, acronyms):
        expander = Expander_fromText()

        for acronym in acronyms:
            for pattern in expander.definition_patterns(acronym):
                if(len(pattern.findall(article_for_testing)) > 0):
                    errorString = "Verification of text expansion removal failed:\nAcronym: " +\
                        acronym + "\nText:\n" + article_for_testing
                    common_logger.error(errorString)
                    raise RuntimeError(errorString)

            if acronym not in article_for_testing:
                errorMessage = "Acronym removed from text while cleaning:\nAcronym: " +\
                    acronym + "\nText:\n" + article_for_testing
                common_logger.error(errorMessage)
                raise RuntimeError(errorMessage)

    def __init__(self):
        self.numRounds = 3
        self.numProcesses = 1
        
        self.articleDBPath = file_articledb
        self.shuffledArticleDBPath = file_articledb_shuffled
        self.acronymDBPath = file_acronymdb
        
        self.expandersToUse = [AcronymExpanderEnum.LDA_multiclass]
        self.ldaModelAll = LDAModel.load(path=folder_lda+"lda_model_noStem_noNums_3Pass.pickle")
        self.vectorizer = joblib.load(file_vectorizer)
        
        self.acronymExtractor = AcronymExtractor_v2_small()
        self.textExtractor = Extract_PdfMiner()


def _proxyFunction(benchmarker, testArticles):
    return benchmarker.getScoresAndReport(testArticles)

if __name__ == "__main__":
    common_logger.info("Starting Benchmarking")

    benchmarker = Benchmarker_wiki()

    common_logger.info("making partitions")
    partitions = benchmarker.getPartitions()
    gc.collect()

    pool = Pool(processes=benchmarker.numProcesses, maxtasksperchild=1)
    common_logger.info("delegating work to pools")

    partialFunc = functools.partial(_proxyFunction, benchmarker)

    results = pool.map(partialFunc, partitions, chunksize=1)
    benchmarker.plotStats(benchmarker.extractScores(results))
    benchmarker.saveAndPrintReport(benchmarker.extractReports(results))
