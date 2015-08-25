from itertools import izip_longest

from numpy import mean, std

from AcronymExpanders.Expander_fromText import Expander_fromText
from AcronymExpanders.Expander_fromText_v2 import Expander_fromText_v2
from DataCreators import AcronymDB, ArticleDB
from Logger import common_logger
from TextExtractors.Extract_PdfMiner import Extract_PdfMiner
from controller import Controller
from helper import AcronymExpansion
import random
import cPickle
from string_constants import file_benchmark_report, file_benchmark_report_pickle,\
    min_confidence


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

    # def __makeExpanders(self, articleDB, acronymDB):
    #    expanders = []
    #    for expanderType in self.expandersToUse:
    #        if (expanderType == AcronymExpanderEnum.fromText):
    #            expanders.append(Expander_fromText())
    #        elif (expanderType == AcronymExpanderEnum.fromText_v2):
    #            expanders.append(Expander_fromText_v2())
    #        elif (expanderType == AcronymExpanderEnum.LDA_cossim):
    #            expanders.append(Expander_LDA(articleDB, acronymDB))
    #        elif (expanderType == AcronymExpanderEnum.LDA_multiclass):
    #            expanders.append(Expander_LDA_multiclass(articleDB, acronymDB))
    #        elif (expanderType == AcronymExpanderEnum.SVC):
    #            expanders.append(Expander_SVC(articleDB, acronymDB))
    #
    #    return expanders

    def __createController(self, articleDB, acronymDB):
        #text_expander = Expander_fromText()
        #expanders = self.__makeExpanders(articleDB, acronymDB)

        return Controller(text_extractor=self.textExtractor,
                          acronym_extractor=self.acronymExtractor,
                          expanders=self.expandersToUse,
                          articleDB=articleDB,
                          acronymDB=acronymDB,
                          ldaModelAll=self.ldaModelAll,
                          vectorizer=self.vectorizer)

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

    def __getResults(self, actual_expansions, predicted_expansions):
        """
        Compares the actual and predicted expansions
        Args:
        actual_expansions (dict):
        predicted_expansions (dict): A dictionary with acronym: AcronymExpansion object

        Returns:
        correct_expansions: number of correct expansions (present in actual and predicted)
        incorrect_expansions: number of incorrect expansions (present in actual, but not in predicted)
        detailed_results: an array of [acronym, actual expansion, predicted expansion, confidence], sorted by acronym
        """
        correct_expansions = 0
        incorrect_expansions = 0
        detailed_results = []
        for acronym in actual_expansions:
            actual_expansion = actual_expansions[acronym][0].expansion

            if (acronym in predicted_expansions
                and AcronymExpansion.
                    areExpansionsSimilar(actual_expansion, predicted_expansions[acronym][0].expansion)):
                common_logger.debug("Expansion matching succeeded (%s): %s, %s, confidence: %f" % (
                    acronym, actual_expansion, predicted_expansions[
                        acronym][0].expansion,
                    predicted_expansions[acronym][0].confidence))
                correct_expansions += 1
                detailed_results.append(
                    [acronym, True, actual_expansion, predicted_expansions[acronym][0].expansion, predicted_expansions[acronym][0].confidence])
            else:
                predicted_expansion = "expansion not predicted"
                confidence = min_confidence
                if (acronym in predicted_expansions):
                    predicted_expansion = predicted_expansions[
                        acronym][0].expansion
                    confidence = predicted_expansions[
                        acronym][0].confidence
                else:
                    common_logger.warning(
                        "Expansion not predicted for %s" % acronym)
                common_logger.debug(
                    "Expansion matching failed (%s): %s, %s, confidence: %f" % (acronym, actual_expansion, predicted_expansion, confidence))
                incorrect_expansions += 1
                detailed_results.append(
                    [acronym, False, actual_expansion, predicted_expansion, confidence])

        sorted_detailed_results = sorted(
            detailed_results, key=lambda item: item[0])

        return correct_expansions, incorrect_expansions, sorted_detailed_results

    def getScoresAndReport(self, testArticles):
        """
        Takes in test articles and gives back a report on the prediction performance.

        Args:
        testArticles (dict): {articleID: article text}

        Returns:
        scores (dict): None or {"correct_expansions": <0.0 to 1.0>, "incorrect_expansions": <0.0 to 1.0>}
        report (list): None or [articleID, [[acronym (sorted order), correct expansion?, true expansion, predicted expansion, confidence]] ]
        """

        common_logger.info("filtering articles with None")
        testArticles = dict(
            [article for article in testArticles if article != None])

        articleDB = ArticleDB.load(path=self.articleDBPath)

        # todo: temp hack, remove!!!
        testArticles["2957215"] = articleDB["2957215"]

        common_logger.info("removing test articles from articleDB")
        for articleID in testArticles.keys():
            del articleDB[articleID]

        common_logger.info("correcting acronymDB")
        acronymDB = self.__getRealignedAcronymDb(testArticles.keys())

        common_logger.info("verifying training dataset")
        if self.__verifyTrainSet(articleDB, acronymDB, testArticles.keys()):
            controller = self.__createController(articleDB, acronymDB)

            common_logger.info("evaluating test performance")
            results = {"correct_expansions": 0.0, "incorrect_expansions": 0.0}
            report = []
            totalExpansions = 0.0
            articlesWithErrors = []
            for articleID in testArticles:
                common_logger.debug("articleID: %s" % articleID)
                try:
                    article = testArticles[articleID]
                    actual_expansions = self._getActualExpansions(
                        articleID, article)
                    article_for_testing = self._removeInTextExpansions(
                        article, actual_expansions)

                    predicted_expansions = controller.processText(
                        article_for_testing)

                    correct, incorrect, detailed_results = self.__getResults(
                        actual_expansions, predicted_expansions)

                    totalExpansions += correct + incorrect
                    results["correct_expansions"] += correct
                    results["incorrect_expansions"] += incorrect
                    report.append([articleID, detailed_results])
                except:
                    common_logger.exception(
                        "skipping articleID: %s, error details:" % (articleID))
                    articlesWithErrors.append(articleID)

            common_logger.error("Total articles: %d, skipped: %d" %
                                (len(testArticles.keys()), len(articlesWithErrors)))

            if(totalExpansions > 0):
                results["correct_expansions"] = results[
                    "correct_expansions"] / totalExpansions
                results["incorrect_expansions"] = results[
                    "incorrect_expansions"] / totalExpansions

            return results, report

        else:
            common_logger.error("verification of train datasets failed for articleIDs %s" % str(
                testArticles.keys()))
            return None, None

    def __grouper(self, iterable, n, fillvalue=None):
        """
        Collect data into fixed-length chunks or blocks
        Copied from https://docs.python.org/2/library/itertools.html
        """
        # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
        args = [iter(iterable)] * n
        return izip_longest(fillvalue=fillvalue, *args)

    def getPartitions(self):
        articleDb = ArticleDB.load(path=self.shuffledArticleDBPath)
        partitions = []

        articleDbItems = articleDb.items()
        random.shuffle(articleDbItems)

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
        common_logger.critical("Processed %d rounds out of %d" %
                               (len(validSuccesses), len(results)))
        common_logger.critical("Mean %f, Standard Deviation: %f" %
                               (mean_val, std_dev))

    def extractScores(self, inputs):
        result = []
        for input in inputs:
            result.append(input[0])

        return result

    def extractReports(self, inputs):
        result = []
        for input in inputs:
            result.append(input[1])
        return result

    def saveAndPrintReport(self, reports):

        # flatten reports
        flattened_reports = []
        for report in reports:
            flattened_reports.extend(report)

        # sort reports by articleID
        sorted_reports = sorted(flattened_reports, key=lambda item: item[0])

        cPickle.dump(
            sorted_reports, open(file_benchmark_report_pickle, "wb"), protocol=-1)

        report_file = open(file_benchmark_report, "wb")
        for report in sorted_reports:
            report_file.write(report[0] + "\n")
            for detailed_result in report[1]:
                report_file.write("\t" + str(detailed_result) + "\n")
