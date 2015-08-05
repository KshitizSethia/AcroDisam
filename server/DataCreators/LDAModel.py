import functools
import math
from multiprocessing import Pool
from threading import Thread

from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamodel import LdaModel

from DataCreators import ArticleDB
from Logger import logger
from TextTools import getCleanedWords
import TextTools
import cPickle as pickle
from string_constants import file_lda_model, file_lda_gensim_dictionary, file_lda_word_corpus,\
    file_lda_articleIDToLDA, file_lda_bow_corpus, file_articledb,\
    file_msh_articleDB


class USESAVED:
    none = -1
    word_corpus = 0
    dictionary = 1
    bow_corpus = 2
    lda_model = 3


def load():
    """return lda_model, gensim_dictionary, article_id_to_LDA_dictionary"""
    lda_model = LdaModel.load(file_lda_model)
    gensim_dictionary = Dictionary.load(file_lda_gensim_dictionary)
    article_id_to_LDA_dictionary = pickle.load(
        open(file_lda_articleIDToLDA, "rb"))
    return lda_model, gensim_dictionary, article_id_to_LDA_dictionary

# todo: put "_" in front of all private methods


def serialGetWordCorpus(articleDB):
    word_corpus = {}
    for article_id, text in articleDB.items():
        word_corpus[article_id] = TextTools.getCleanedWords(text)
        if len(word_corpus) % 1000 == 0:
            logger.debug(
                "converted " + str(len(word_corpus)) + " articles to words")
    return word_corpus


def serialGetBoWCorpus(dictionary, word_corpus_values):
    return [dictionary.doc2bow(words) for words in word_corpus_values]


def parallelGetCleanedWords(article):
    return article[0], getCleanedWords(article[1])


def parallelGetWordCorpus(articleDB, process_pool):
    articles = articleDB.items()
    results = process_pool.map(
        parallelGetCleanedWords, articles, chunksize=chunkSizeWordCorpus)

    logger.info("Back from multiprocessing, making dict now")
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
        bound_instance, word_corpus_values, chunksize=chunkSizeBowCorpus)

    return result


def getWordCorpus(articleDB, process_pool, useSavedTill):
    if(useSavedTill >= USESAVED.word_corpus):
        logger.info("Loading word_corpus from file")
        word_corpus = pickle.load(open(file_lda_word_corpus, "rb"))
        return word_corpus, None
    else:
        logger.info("Getting word_corpus from articles")
        word_corpus = parallelGetWordCorpus(
            articleDB, process_pool) if process_pool != None else serialGetWordCorpus(articleDB)

        logger.info(
            "Saving word_corpus asynchronously, in case the script ahead fails")
        file = open(file_lda_word_corpus, "wb")
        word_corpus_dumper = Thread(
            target=pickle.dump, args=(word_corpus, file), kwargs={"protocol": 2})
        word_corpus_dumper.start()

        return word_corpus, word_corpus_dumper


def getDictionary(word_corpus, useSavedTill):
    if(useSavedTill >= USESAVED.dictionary):
        logger.info("loading dictionary from file")
        dictionary = Dictionary.load(file_lda_gensim_dictionary)
        return dictionary
    else:
        logger.info("Creating dictionary from corpus")
        dictionary = Dictionary(word_corpus.values())
        logger.info("saving dictionary")
        dictionary.save(file_lda_gensim_dictionary)
        return dictionary


def getBoWCorpus(word_corpus, dictionary, process_pool, useSavedTill):
    if(useSavedTill >= USESAVED.bow_corpus):
        logger.info("loading bow_corpus from file")
        bow_corpus = pickle.load(open(file_lda_bow_corpus, "rb"))
        return bow_corpus, None
    else:
        logger.info("Creating BoW representations from articles")
        bow_corpus = parallelGetBoWCorpus(dictionary, word_corpus.values(
        ), process_pool) if process_pool != None else serialGetBoWCorpus(dictionary, word_corpus.values())

        file = open(file_lda_bow_corpus, "wb")
        bow_corpus_dumper = Thread(
            target=pickle.dump, args=(bow_corpus, file), kwargs={"protocol": 2})
        bow_corpus_dumper.start()
        return bow_corpus, bow_corpus_dumper


def getLdaModel(bow_corpus, dictionary, useSavedTill):
    if(useSavedTill >= USESAVED.lda_model):
        logger.info("loading LDA model from file")
        return LdaModel.load(file_lda_model)
    else:
        logger.info("Training LDA model")
        num_topics = int(math.log(len(bow_corpus)) + 1)  # assumption:
        # todo: LdaMulticore is not working on windows, change before running on
        # compute node
        lda_model = LdaModel(
            bow_corpus, num_topics=num_topics, id2word=dictionary)

        logger.info("Saving LDA model")
        lda_model.save(file_lda_model)
        logger.info("Done creating LDA model")
        return lda_model


def createArticleIdToLdaDict(word_corpus, dictionary, lda_model):
    logger.info("Creating article_id -> lda_vector dictionary")
    article_lda = {}
    index = 0
    for article_id in word_corpus.keys():
        bow = dictionary.doc2bow(word_corpus[article_id])
        lda_vec = lda_model[bow]
        article_lda[article_id] = lda_vec
        index += 1
        if(index % 1000 == 0):
            logger.debug("done with %d articles", index)
    logger.info("saving article_id -> lda_vector dictionary")
    pickle.dump(article_lda, open(file_lda_articleIDToLDA, "wb"), protocol=2)


def waitForDumper(dumper, name):
    if(dumper != None):
        if(dumper.is_alive()):
            logger.info(
                "Waiting for" + name + "dumper to finish saving to disk")
            dumper.join()
        else:
            logger.info(
                name + "dumper has already finished saving to disk, not waiting")


def create_and_save_model(process_pool, useSavedTill=USESAVED.none):
    """
    This takes a long time to train (~1 week), 
    run on a compute node with ~250 GB RAM and fast processor
    for wikipedia corpus of 410k documents
    """
    logger.info("Creating lda vectors for articles")

    articleDB = ArticleDB.load(path=articleDBPath)

    word_corpus, word_corpus_dumper = getWordCorpus(
        articleDB, process_pool, useSavedTill)

    dictionary = getDictionary(word_corpus, useSavedTill)

    bow_corpus, bow_corpus_dumper = getBoWCorpus(
        word_corpus, dictionary, process_pool, useSavedTill)

    lda_model = getLdaModel(bow_corpus, dictionary, useSavedTill)

    createArticleIdToLdaDict(word_corpus, dictionary, lda_model)

    waitForDumper(word_corpus_dumper, "word corpus")

    waitForDumper(bow_corpus_dumper, "bow corpus")

    logger.info("Done creating articleIDToLDA dictionary, exiting")


def update_model(articledb_path):
    """returns built lda_model, lda_dictionary"""
    pass  # todo: lda has update method, use it

# global settings for making LDA model
numProcesses = 3
articleDBPath = file_msh_articleDB
goParallel = True
useSavedTill = USESAVED.none
chunkSizeWordCorpus = 1000
chunkSizeBowCorpus = 1000
   
if __name__ == "__main__":
    if(goParallel):
        process_pool = Pool(numProcesses)
        create_and_save_model(process_pool, useSavedTill=useSavedTill)
        pass
    else:
        create_and_save_model(None, useSavedTill=useSavedTill)
