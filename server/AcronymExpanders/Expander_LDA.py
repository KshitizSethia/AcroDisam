import math
import os

from gensim import corpora
from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamodel import LdaModel

from AcronymExpanders import acronymDB, articleDB, AcronymExpanderEnum
from AcronymExpanders.AcronymExpander import AcronymExpander
from DataCreators import ArticleDB
from Logger import logger
import TextTools
from string_constants import file_lda_model, file_gensim_dictionary, file_articleIDToLDA
from TextTools import getCleanedWords
import cPickle as pickle
import sys
from scipy.spatial.distance import cosine


class Expander_LDA(AcronymExpander):

    def __init__(self):
        logger.info("Loading LDA model and dictionary")
        self.ldamodel = LdaModel.load(file_lda_model)
        self.dictionary = Dictionary.load(file_gensim_dictionary)
        self.articleLDADict = pickle.load(open(file_articleIDToLDA, "rb"))

    def expand(self, acronym, acronymExpansion, text):
        choices = self.getChoices(acronym)

        cleaned_words = getCleanedWords(text)
        bow = self.dictionary.doc2bow(cleaned_words)
        target_lda = self.ldamodel[bow]

        min_cos_dist = sys.maxint
        chosen_expansion = ""
        for choice in choices:
            choice_lda = self.articleLDADict[choice.article_id]
            cos_dist = cosine(target_lda, choice_lda)
            if(cos_dist < min_cos_dist):
                chosen_expansion = choice.expansion
                min_cos_dist = cos_dist
        if(chosen_expansion != ""):
            acronymExpansion.expansion = chosen_expansion
            acronymExpansion.expander = AcronymExpanderEnum.LDA
        return acronymExpansion
    @staticmethod
    def update_model(articledb_path):
        """returns built lda_model, lda_dictionary"""
        pass  # todo: lda has update method, use it

    @staticmethod
    def create_and_save_model():
        """
        This takes a long time to train, 
        run on a compute node with ~25 GB RAM and fast processor
        """
        logger.info("Training new LDA model")
        if(os.path.exists(file_lda_model) or os.path.exists(file_gensim_dictionary)):
            os.remove(file_lda_model)
            os.remove(file_gensim_dictionary)

        articleDB = ArticleDB.load()
        articles = articleDB.values()
        logger.info("Getting word_corpus from articles")
        word_corpus = []
        for article in articles:
            word_corpus.append(TextTools.getCleanedWords(article))
            if len(word_corpus) % 1000 == 0:
                logger.debug(
                    "converted " + str(len(word_corpus)) + " articles to words")

        logger.info("Creating dictionary from corpus")
        dictionary = corpora.Dictionary(word_corpus)
        logger.info("saving dictionary")
        dictionary.save(file_gensim_dictionary)

        logger.info("Creating BoW representations from articles")
        bow_corpus = [dictionary.doc2bow(article) for article in word_corpus]

        logger.info("Training LDA model")
        num_topics = math.log(len(articles))  # assumption:
        lda_model = LdaModel(bow_corpus, num_topics=num_topics)

        logger.info("Saving LDA model")
        lda_model.save(file_lda_model)
        logger.info("Done creating LDA model")
        logger.info("Creating article_id -> lda_vector dictionary")
        article_lda = {}
        for article_id, article_text in articleDB.items():
            bow = dictionary.doc2bow(getCleanedWords(article_text))
            lda_vec = lda_model[bow]
            article_lda[article_id] = lda_vec
        logger.info("saving article_id -> lda_vector dictionary")
        pickle.dump(article_lda, open(file_articleIDToLDA, "wb"), protocol=2)
        logger.info("Done creating articleIDToLDA dictionary")

if __name__ == "__main__":
    Expander_LDA.create_and_save_model()
