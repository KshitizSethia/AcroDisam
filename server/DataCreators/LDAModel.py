import math
import os

from gensim import corpora
from gensim.models.ldamodel import LdaModel

from DataCreators import ArticleDB
from Logger import logger
import TextTools
import cPickle as pickle
from string_constants import file_lda_model, file_gensim_dictionary, file_temp_word_corpus,\
    file_articleIDToLDA
from gensim.corpora.dictionary import Dictionary


def load():
    """return lda_model, gensim_dictionary, article_id_to_LDA_dictionary"""
    lda_model = LdaModel.load(file_lda_model)
    gensim_dictionary = Dictionary.load(file_gensim_dictionary)
    article_id_to_LDA_dictionary = pickle.load(open(file_articleIDToLDA, "rb"))
    return lda_model, gensim_dictionary, article_id_to_LDA_dictionary


def create_and_save_model():
    """
    This takes a long time to train (~1 day), 
    run on a compute node with ~25 GB RAM and fast processor
    """
    logger.info("Training new LDA model")
    if(os.path.exists(file_lda_model) or os.path.exists(file_gensim_dictionary)):
        os.remove(file_lda_model)
        os.remove(file_gensim_dictionary)

    articleDB = ArticleDB.load()
    logger.info("Getting word_corpus from articles")
    word_corpus = {}
    for article_id, text in articleDB.items():
        word_corpus[article_id] = TextTools.getCleanedWords(text)
        if len(word_corpus) % 1000 == 0:
            logger.debug(
                "converted " + str(len(word_corpus)) + " articles to words")

    logger.info(
        "Saving word_corpus temporarily, in case the script ahead fails")
    pickle.dump(word_corpus, open(file_temp_word_corpus, "wb"), protocol=2)

    logger.info("Creating dictionary from corpus")
    dictionary = corpora.Dictionary(word_corpus.values())
    logger.info("saving dictionary")
    dictionary.save(file_gensim_dictionary)

    logger.info("Creating BoW representations from articles")
    bow_corpus = [dictionary.doc2bow(words) for words in word_corpus.values()]

    logger.info("Training LDA model")
    num_topics = math.log(len(word_corpus.keys()))  # assumption:
    lda_model = LdaModel(bow_corpus, num_topics=num_topics)

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

    #logger.info("Deleting temporary backup copy of word_corpus")
    #os.remove(file_temp_word_corpus)

    logger.info("Done creating articleIDToLDA dictionary")


if __name__ == "__main__":
    create_and_save_model()
