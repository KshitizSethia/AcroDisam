import cPickle
import functools
from multiprocessing import Pool

from AcronymExpanders import AcronymExpanderEnum
from AcronymExtractors.AcronymExtractor_v1 import AcronymExtractor_v1
from AcronymExtractors.AcronymExtractor_v2 import AcronymExtractor_v2
from AcronymExtractors.AcronymExtractor_v2_small import AcronymExtractor_v2_small
from Benchmarker.Benchmark import Benchmarker
from string_constants import file_msh_articleDB, file_msh_acronymDB,\
    file_msh_articleIDToAcronymExpansions, file_msh_articleDB_shuffled


class Benchmarker_MSH(Benchmarker):

    def __init__(self):
        self.numProcesses = 1
        self.numRounds = 10
        self.articleDBPath = file_msh_articleDB
        self.shuffledArticleDBPath = file_msh_articleDB_shuffled
        self.acronymDBPath = file_msh_acronymDB
        self.expandersToUse = [AcronymExpanderEnum.SVC]
        self.acronymExtractor = AcronymExtractor_v2_small()
        self.articleIDToAcronymExpansions = cPickle.load(
            open(file_msh_articleIDToAcronymExpansions, "rb"))

    def _getActualExpansions(self, articleID, article):
        return self.articleIDToAcronymExpansions[articleID]

    def _removeInTextExpansions(self, article, acronyms):
        return article


def _proxyFunction(benchmarker, testArticles):
    return benchmarker.getScoresAndReport(testArticles)

if __name__ == "__main__":
    benchmarker = Benchmarker_MSH()

    partitions = benchmarker.getPartitions()

    partialFunc = functools.partial(_proxyFunction, benchmarker)
    process_pool = Pool(processes=benchmarker.numProcesses, maxtasksperchild=1)

    results = process_pool.map(partialFunc, partitions, chunksize=1)

    benchmarker.plotStats(benchmarker.extractScores(results))
    benchmarker.saveAndPrintReport(benchmarker.extractReports(results))
