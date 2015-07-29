import math
from multiprocessing.pool import Pool
import os
from threading import Thread

from gensim import corpora
from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamodel import LdaModel
from gensim.models.ldamulticore import LdaMulticore

from DataCreators import ArticleDB
from Logger import logger
from TextTools import getCleanedWords
import TextTools
import cPickle as pickle
from string_constants import file_lda_model, file_gensim_dictionary, file_word_corpus,\
    file_articleIDToLDA
import functools


# global settings for parallelization
numProcesses = 3
# keep chunksize low so that the result  array is not appended to at once.
chunkSize = 50


def load():
    """return lda_model, gensim_dictionary, article_id_to_LDA_dictionary"""
    lda_model = LdaModel.load(file_lda_model)
    gensim_dictionary = Dictionary.load(file_gensim_dictionary)
    article_id_to_LDA_dictionary = pickle.load(open(file_articleIDToLDA, "rb"))
    return lda_model, gensim_dictionary, article_id_to_LDA_dictionary


def getWordCorpus(articleDB):
    word_corpus = {}
    for article_id, text in articleDB.items():
        word_corpus[article_id] = TextTools.getCleanedWords(text)
        if len(word_corpus) % 1000 == 0:
            logger.debug(
                "converted " + str(len(word_corpus)) + " articles to words")

    logger.info(
        "Saving word_corpus temporarily, in case the script ahead fails")
    pickle.dump(word_corpus, open(file_word_corpus, "wb"), protocol=2)
    return word_corpus


def getBoWCorpus(dictionary, word_corpus_values):
    return [dictionary.doc2bow(words) for words in word_corpus_values]


def parallelGetCleanedWords(article):
    return article[0], getCleanedWords(article[1])


def parallelGetWordCorpus(articleDB):
    articles = articleDB.items()
    pool = Pool()  # processes=numProcesses)
    results = pool.map(parallelGetCleanedWords, articles, chunksize=chunkSize)

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


def parallelGetBoWCorpus(dictionary, word_corpus_values):
    bound_instance = functools.partial(_doc2bow_alias, dictionary)

    pool = Pool(processes=numProcesses)
    result = pool.map(bound_instance, word_corpus_values, chunksize=chunkSize)
    return result


def create_and_save_model():
    """
    This takes a long time to train (~1 day), 
    run on a compute node with ~25 GB RAM and fast processor
    """
    logger.info("Training new LDA model")
    if os.path.exists(file_lda_model):
        os.remove(file_lda_model)
    if os.path.exists(file_gensim_dictionary):
        os.remove(file_gensim_dictionary)

    articleDB = ArticleDB.load()
    logger.info("Getting word_corpus from articles")
    word_corpus = parallelGetWordCorpus(articleDB)

    logger.info(
        "Saving word_corpus asynchronously, in case the script ahead fails")
    file = open(file_word_corpus, "wb")
    slave = Thread(
        target=pickle.dump, args=(word_corpus, file), kwargs={"protocol": 2})
    slave.start()

    logger.info("Creating dictionary from corpus")
    dictionary = corpora.Dictionary(word_corpus.values())
    logger.info("saving dictionary")
    dictionary.save(file_gensim_dictionary)

    #dictionary = Dictionary.load(file_gensim_dictionary)

    logger.info("Creating BoW representations from articles")
    bow_corpus = parallelGetBoWCorpus(dictionary, word_corpus.values())

    logger.info("Training LDA model")
    num_topics = int(math.log(len(word_corpus.keys())) + 1)  # assumption:
    lda_model = LdaModel(
        bow_corpus, num_topics=num_topics)#, workers=numProcesses)

    logger.info("Saving LDA model")
    lda_model.save(file_lda_model)
    logger.info("Done creating LDA model")

    logger.info("Creating article_id -> lda_vector dictionary")
    article_lda = {}
    index = 0
    for article_id in articleDB.keys():
        bow = dictionary.doc2bow(word_corpus[article_id])
        lda_vec = lda_model[bow]
        article_lda[article_id] = lda_vec
        index += 1
        if(index % 1000 == 0):
            logger.debug("done with %d articles", index)
    logger.info("saving article_id -> lda_vector dictionary")
    pickle.dump(article_lda, open(file_articleIDToLDA, "wb"), protocol=2)

    if(slave.is_alive()):
        logger.info(
            "Waiting for temporary word_corpus to finish saving to disk")
        slave.join()
    else:
        logger.info(
            "word_corpus has already finished saving to disk, not waiting")

    #logger.info("Deleting temporary backup copy of word_corpus")
    # os.remove(file_word_corpus)

    logger.info("Done creating articleIDToLDA dictionary, exiting")


if __name__ == "__main__":
    create_and_save_model()
