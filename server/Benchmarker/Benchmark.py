from itertools import izip_longest

from numpy import mean, std

from AcronymExpanders import AcronymExpanderEnum
from AcronymExpanders.Expander_LDA import Expander_LDA
from AcronymExpanders.Expander_SVC import Expander_SVC
from AcronymExpanders.Expander_fromText import Expander_fromText
from AcronymExpanders.Expander_fromText_v2 import Expander_fromText_v2
from AcronymExtractors.AcronymExtractor_v1 import AcronymExtractor_v1
from DataCreators import AcronymDB, ArticleDB
from Logger import logger
from TextExtractors.Extract_PdfMiner import Extract_PdfMiner
from controller import Controller
from nltk.metrics.distance import edit_distance


class Benchmarker:

    def __getRealignedAcronymDb(self, articleIDsToRemove):
        acronymDb = AcronymDB.load(path=self.acronymDBPath)

        for acronym in acronymDb.keys():
            validEntries = []
            for entry in acronymDb[acronym]:
                if entry[1] not in articleIDsToRemove:
                    validEntries.append(entry)
            acronymDb[acronym] = validEntries

        return acronymDb

    def __makeExpanders(self, articleDB, acronymDB):
        expanders = []
        for expanderType in self.expandersToUse:
            if (expanderType == AcronymExpanderEnum.fromText):
                expanders.append(Expander_fromText())
            elif (expanderType == AcronymExpanderEnum.fromText_v2):
                expanders.append(Expander_fromText_v2())
            elif (expanderType == AcronymExpanderEnum.LDA):
                expanders.append(Expander_LDA(articleDB, acronymDB))
            elif (expanderType == AcronymExpanderEnum.SVC):
                expanders.append(Expander_SVC(articleDB, acronymDB))

        return expanders

    def __createController(self, articleDB, acronymDB):
        #text_expander = Expander_fromText()
        expanders = self.__makeExpanders(articleDB, acronymDB)

        return Controller(text_extractor=Extract_PdfMiner(), acronym_extractor=AcronymExtractor_v1(), expanders=expanders)

    def __verifyTrainSet(self, articleDB, acronymDB, testArticleIDs):
        for articleId in articleDB:
            if(articleId in testArticleIDs):
                return False
        for acronym in acronymDB:
            for expansion, articleId, ignored_field in acronymDB[acronym]:
                if articleId in testArticleIDs:
                    return False
        return True

    def _getActualExpansions(self, articleID, article):
        pass
    
    def _removeInTextExpansions(self, article, acronyms):
        pass

    def __areExpansionsSimilar(self, actual_expansion, predicted_expansion):
        actual_expansion = actual_expansion.lower().replace(u"-", u" ")
        predicted_expansion = predicted_expansion.lower().replace(u"-", u" ")
        numActualWords = len(actual_expansion)
        numPredictedWords = len(predicted_expansion)
        
        if(actual_expansion == predicted_expansion):
            return True
        elif AcronymDB.is_same_expansion(actual_expansion, predicted_expansion):
            logger.debug("Expansion matching succeeded: " +
                         actual_expansion + ", " + predicted_expansion)
            return True
        elif(edit_distance(actual_expansion, predicted_expansion)<=2):#max(numActualWords, numPredictedWords)):
            logger.debug("Expansion matching succeeded: " +
                         actual_expansion + ", " + predicted_expansion)
            return True
        logger.debug(
            "Expansion matching failed: " + actual_expansion + ", " + predicted_expansion)
        return False

    def __getResults(self, actual_expansions, predicted_expansions):
        correct_expansions = 0
        incorrect_expansions = 0

        for acronym in actual_expansions:
            actual_expansion = actual_expansions[acronym].expansion

            if (acronym in predicted_expansions
                    and self.__areExpansionsSimilar(actual_expansion, predicted_expansions[acronym].expansion)):
                correct_expansions += 1
            else:
                incorrect_expansions += 1

        return correct_expansions, incorrect_expansions

    def getScores(self, testArticles):

        logger.info("filtering articles with None")
        testArticles = dict(
            [article for article in testArticles if article != None])

        articleDB = ArticleDB.load(path=self.articleDBPath)

        logger.info("removing test articles from articleDB")
        for articleID in testArticles.keys():
            del articleDB[articleID]

        logger.info("correcting acronymDB")
        acronymDB = self.__getRealignedAcronymDb(testArticles.keys())

        logger.info("verifying training dataset")
        if self.__verifyTrainSet(articleDB, acronymDB, testArticles.keys()):
            controller = self.__createController(articleDB, acronymDB)

            logger.info("evaluating test performance")
            results = {"correct_expansions": 0.0, "incorrect_expansions": 0.0}
            totalExpansions = 0.0
            articlesWithErrors = []
            for articleID in testArticles:
                try:
                    article = testArticles[articleID]
                    actual_expansions = self._getActualExpansions(
                        articleID, article)
                    article_for_testing = self._removeInTextExpansions(
                        article, actual_expansions)

                    predicted_expansions = controller.processText(
                        article_for_testing)

                    correct, incorrect = self.__getResults(
                        actual_expansions, predicted_expansions)

                    totalExpansions += correct + incorrect
                    results["correct_expansions"] += correct
                    results["incorrect_expansions"] += incorrect
                except:
                    logger.exception(
                        "skipping articleID: %s, error details:" % (articleID))
                    articlesWithErrors.append(articleID)

            logger.error("Total articles: %d, skipped: %d" %
                         (len(testArticles.keys()), len(articlesWithErrors)))

            if(totalExpansions > 0):
                results["correct_expansions"] = results[
                    "correct_expansions"] / totalExpansions
                results["incorrect_expansions"] = results[
                    "incorrect_expansions"] / totalExpansions

            return results

        else:
            logger.error("verification of train datasets failed for articleIDs %s" % str(
                testArticles.keys()))
            return None

    def __grouper(self, iterable, n, fillvalue=None):
        """
        Collect data into fixed-length chunks or blocks
        Copied from https://docs.python.org/2/library/itertools.html
        """
        # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
        args = [iter(iterable)] * n
        return izip_longest(fillvalue=fillvalue, *args)

    def getPartitions(self):
        articleDb = ArticleDB.load(path=self.articleDBPath)
        partitions = []

        articleDbItems = articleDb.items()
        #random.shuffle(articleDbItems)#todo: un-comment this

        partitionSize = int(len(articleDbItems) / self.numRounds)
        if((len(articleDbItems) % self.numRounds) != 0):
            partitionSize += 1

        for ids in self.__grouper(articleDbItems, partitionSize, fillvalue=None):
            partitions.append(list(ids))
        articleDb.clear()
        return partitions

    def plotStats(self, results):
        validSuccesses = [item["correct_expansions"]
                          for item in results if item != None]

        mean_val = mean(validSuccesses)
        std_dev = std(validSuccesses)
        logger.critical("Processed %d rounds out of %d" %
                        (len(validSuccesses), len(results)))
        logger.critical("Mean %f, Standard Deviation: %f" %
                        (mean_val, std_dev))
