from Benchmarker.Benchmark import Benchmarker
from string_constants import file_msh_articleDB, file_msh_acronymDB,\
    file_msh_articleIDToAcronymExpansions
import cPickle
from multiprocessing import Pool
import functools
from AcronymExpanders import AcronymExpanderEnum

class Benchmarker_MSH(Benchmarker):
    
    def __init__(self):
        self.numProcesses=3
        self.numRounds = 10
        self.articleDBPath = file_msh_articleDB
        self.acronymDBPath = file_msh_acronymDB
        self.expandersToUse = [
            AcronymExpanderEnum.fromText, AcronymExpanderEnum.SVC]
        self.articleIDToAcronymExpansions = cPickle.load(open(file_msh_articleIDToAcronymExpansions, "rb"))
        
    def _getActualExpansions(self, articleID, article):
        return self.articleIDToAcronymExpansions[articleID]
        
    def _removeInTextExpansions(self, article, acronyms):
        return article
    
def _proxyFunction(benchmarker, testArticles):
    return benchmarker.getScores(testArticles)
    
if __name__ =="__main__":
    benchmarker = Benchmarker_MSH()

    partitions = benchmarker.getPartitions()

    partialFunc = functools.partial(_proxyFunction,benchmarker)
    process_pool = Pool(processes=benchmarker.numProcesses, maxtasksperchild=1)

    scores = process_pool.map(partialFunc,partitions,chunksize=1)
    benchmarker.plotStats(scores)
