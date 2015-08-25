import functools
import math
from multiprocessing import Pool
from threading import Thread

from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamodel import LdaModel

from DataCreators import ArticleDB
from Logger import common_logger
from TextTools import getCleanedWords
import TextTools
import cPickle as pickle
from helper import SavedLDAModel
from string_constants import file_lda_word_corpus,\
    file_lda_bow_corpus, file_articledb,\
    file_lda_model_all, file_lda_model,\
    file_lda_articleIDToLDA, file_lda_gensim_dictionary


class USESAVED:
    none = -1
    word_corpus = 0
    dictionary = 1
    bow_corpus = 2
    lda_model = 3


def load(path=file_lda_model_all):
    """
    Returns: SavedLDAModel object
    """
    #lda_model = LdaModel.load(file_lda_model)
    #gensim_dictionary = Dictionary.load(file_lda_gensim_dictionary)
    # article_id_to_LDA_dictionary = pickle.load(
    #    open(file_lda_articleIDToLDA, "rb"))
    # return lda_model, gensim_dictionary, article_id_to_LDA_dictionary
    common_logger.info("Loading LDA model from " + path)
    return pickle.load(open(path, "rb"))

# todo: put "_" in front of all private methods


def serialGetWordCorpus(articleDB):
    word_corpus = {}
    for article_id, text in articleDB.items():
        word_corpus[article_id] = TextTools.getCleanedWords(
            text
            , stem_words=stem_words
            , removeNumbers=removeNumbers)
        if len(word_corpus) % 1000 == 0:
            common_logger.debug(
                "converted " + str(len(word_corpus)) + " articles to words")
    return word_corpus


def serialGetBoWCorpus(dictionary, word_corpus_values):
    return [dictionary.doc2bow(words) for words in word_corpus_values]


def parallelGetCleanedWords(article):
    return article[0], getCleanedWords(article[1]
                                       , stem_words=stem_words
                                       , removeNumbers=removeNumbers)


def parallelGetWordCorpus(articleDB, process_pool):
    articles = articleDB.items()
    results = process_pool.map(
        parallelGetCleanedWords, articles, chunksize=chunkSize_getCleanedWords)

    common_logger.info("Back from multiprocessing, making dict now")
    word_corpus = dict(results)

    return word_corpus


def _doc2bow_alias(dictionary, words):
    """
    Alias for instance method that allows the method to be called in a 
    multiprocessing pool
    see link for details: http://stackoverflow.com/a/29873604/681311
    """
    return dictionary.doc2bow(words)


def parallelGetBoWCorpus(dictionary, word_corpus_values, process_pool):
    bound_instance = functools.partial(_doc2bow_alias, dictionary)

    result = process_pool.map(
        bound_instance, word_corpus_values, chunksize=chunkSize_doc2BoW)

    return result


def getWordCorpus(articleDB, process_pool, useSavedTill):
    if(useSavedTill >= USESAVED.word_corpus):
        common_logger.info("Loading word_corpus from out_file")
        word_corpus = pickle.load(open(file_lda_word_corpus, "rb"))
        return word_corpus, None
    else:
        common_logger.info("Getting word_corpus from articles")
        word_corpus = parallelGetWordCorpus(
            articleDB, process_pool) if process_pool != None else serialGetWordCorpus(articleDB)

        common_logger.info(
            "Saving word_corpus asynchronously, in case the script ahead fails")
        out_file = open(file_lda_word_corpus, "wb")
        word_corpus_dumper = Thread(
            target=pickle.dump, args=(word_corpus, out_file), kwargs={"protocol": 2})
        word_corpus_dumper.start()

        return word_corpus, word_corpus_dumper


def getDictionary(word_corpus, useSavedTill):
    if(useSavedTill >= USESAVED.dictionary):
        common_logger.info("loading dictionary from file")
        dictionary = Dictionary.load(file_lda_gensim_dictionary)
        return dictionary
    else:
        common_logger.info("Creating dictionary from corpus")
        dictionary = Dictionary(word_corpus.values())
        common_logger.info("saving dictionary")
        dictionary.save(file_lda_gensim_dictionary)
        return dictionary


def getBoWCorpus(word_corpus, dictionary, process_pool, useSavedTill):
    if(useSavedTill >= USESAVED.bow_corpus):
        common_logger.info("loading bow_corpus from out_file")
        bow_corpus = pickle.load(open(file_lda_bow_corpus, "rb"))
        return bow_corpus, None
    else:
        common_logger.info("Creating BoW representations from articles")
        bow_corpus = parallelGetBoWCorpus(dictionary, word_corpus.values(
        ), process_pool) if process_pool != None else serialGetBoWCorpus(dictionary, word_corpus.values())

        out_file = open(file_lda_bow_corpus, "wb")
        bow_corpus_dumper = Thread(
            target=pickle.dump, args=(bow_corpus, out_file), kwargs={"protocol": 2})
        bow_corpus_dumper.start()
        return bow_corpus, bow_corpus_dumper


def getLdaModel(bow_corpus, dictionary, useSavedTill):
    if(useSavedTill >= USESAVED.lda_model):
        common_logger.info("loading LDA model from file")
        return LdaModel.load(file_lda_model)
    else:
        common_logger.info("Training LDA model")
        num_topics = int(math.log(len(bow_corpus)) + 1)  # assumption:
        lda_model = LdaModel(
            bow_corpus, num_topics=num_topics, id2word=dictionary, passes=numPasses)
        common_logger.info("Saving LDA model")
        lda_model.save(file_lda_model)
        common_logger.info("Done creating LDA model")
        return lda_model


def createArticleIdToLdaDict(word_corpus, dictionary, lda_model):
    common_logger.info("Creating article_id -> lda_vector dictionary")
    article_lda = {}
    index = 0
    for article_id in word_corpus.keys():
        bow = dictionary.doc2bow(word_corpus[article_id])
        lda_vec = lda_model[bow]
        article_lda[article_id] = lda_vec
        index += 1
        if(index % 1000 == 0):
            common_logger.debug("done with %d articles", index)
    common_logger.info("saving article_id -> lda_vector dictionary")
    pickle.dump(article_lda, open(file_lda_articleIDToLDA, "wb"), protocol=2)
    return article_lda


def waitForDumper(dumper, name):
    if(dumper != None):
        if(dumper.is_alive()):
            common_logger.info(
                "Waiting for" + name + " dumper to finish saving to disk")
            dumper.join()
        else:
            common_logger.info(
                name + " dumper has already finished saving to disk, not waiting")


def create_and_save_model(process_pool, useSavedTill=USESAVED.none):
    """
    This takes a long time to train (~1 week), 
    run on a compute node with ~250 GB RAM and fast processor
    for wikipedia corpus of 410k documents

    Above time and storage estimates are not correct yet.
    """

    articleDB = ArticleDB.load(path=articleDBPath)

    word_corpus, word_corpus_dumper = getWordCorpus(
        articleDB, process_pool, useSavedTill)

    dictionary = getDictionary(word_corpus, useSavedTill)

    bow_corpus, bow_corpus_dumper = getBoWCorpus(
        word_corpus, dictionary, process_pool, useSavedTill)

    if(process_pool):
        common_logger.info("terminating process pool")
        process_pool.close()
        process_pool.terminate()

    lda_model = getLdaModel(bow_corpus, dictionary, useSavedTill)

    articleIDToLDADict = createArticleIdToLdaDict(
        word_corpus, dictionary, lda_model)

    _saveAll(lda_model, dictionary, articleIDToLDADict, articleDBPath,
             stem_words, numPasses, removeNumbers, path=file_lda_model_all)

    waitForDumper(word_corpus_dumper, "word corpus")

    waitForDumper(bow_corpus_dumper, "bow corpus")

    common_logger.info("Done creating articleIDToLDA dictionary, exiting")


def _saveAll(ldaModel, dictionary, articleIDToLDADict, articleDBused, stem_words, numPasses, removeNumbers, path=file_lda_model_all):
    common_logger.info("Saving LDA model object with all data")
    model_all = SavedLDAModel(
        ldaModel, dictionary, articleIDToLDADict, articleDBused, stem_words, numPasses, removeNumbers)
    pickle.dump(model_all, open(file_lda_model_all, "wb"), protocol=-1)


def update_model(articledb_path):
    """returns built lda_model, lda_dictionary"""
    pass  # todo: lda has update method, use it


def logConfig():
    common_logger.info("Logging config of script")
    common_logger.info("numProcesses = %d" % numProcesses)
    common_logger.info("articleDBPath = %s" % articleDBPath)
    common_logger.info("goParallel = %s" % goParallel)
    common_logger.info("useSavedTill = %d" % useSavedTill)
    common_logger.info("chunkSize_getCleanedWords = %d" %
                       chunkSize_getCleanedWords)
    common_logger.info("chunkSize_doc2BoW = %d" % chunkSize_doc2BoW)
    common_logger.info("stem_words = %s" % stem_words)
    common_logger.info(
        "removeNumbers = %s" % removeNumbers)
    common_logger.info("numPasses = %d" % numPasses)

# global config for making LDA model
numProcesses = 3
articleDBPath = file_articledb
goParallel = True
useSavedTill = USESAVED.none
chunkSize_getCleanedWords = 1000
chunkSize_doc2BoW = 1000
stem_words = False
removeNumbers = True
numPasses = 2

if __name__ == "__main__":
    common_logger.info("LDA Model script started")
    logConfig()
    if(goParallel):
        process_pool = Pool(numProcesses)
        create_and_save_model(process_pool, useSavedTill=useSavedTill)
    else:
        create_and_save_model(None, useSavedTill=useSavedTill)
