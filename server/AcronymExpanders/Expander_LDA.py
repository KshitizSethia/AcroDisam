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
from string_constants import file_lda_model, file_gensim_dictionary


class Expander_LDA(AcronymExpander):

    def __init__(self):
        logger.info("Loading LDA model and dictionary")
        self.ldamodel = LdaModel.load(file_lda_model)
        self.dictionary = Dictionary.load(file_gensim_dictionary)
        

    def expand(self, acronym, acronymExpansion, text):
        pass#todo:

    @staticmethod
    def update_model(articledb_path):
        """returns built lda_model, lda_dictionary"""
        pass  # todo: lda has update method, use it

    @staticmethod
    def create_and_save_model():
        if(os.path.exists(file_lda_model) or os.path.exists(file_gensim_dictionary)):
            os.remove(file_lda_model)
            os.remove(file_gensim_dictionary)

        articleDB = ArticleDB.load()
        articles = articleDB.values()
        word_corpus = [
            TextTools.getCleanedWords(article) for article in articles]

        dictionary = corpora.Dictionary(word_corpus)

        bow_corpus = [dictionary.doc2bow(article) for article in word_corpus]

        num_topics = math.log(len(articles))  # assumption:
        lda_model = LdaModel(bow_corpus, num_topics=num_topics)

        lda_model.save(file_lda_model)
        dictionary.save(file_gensim_dictionary)


if __name__ == "__main__":
    Expander_LDA.create_and_save_model()
