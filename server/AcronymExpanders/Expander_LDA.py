import sys

from scipy.spatial.distance import cosine

from AcronymExpanders import acronymDB, articleDB, AcronymExpanderEnum
from AcronymExpanders.AcronymExpander import AcronymExpander
from Logger import logger
from TextTools import getCleanedWords
import cPickle as pickle
from string_constants import file_lda_model, file_gensim_dictionary, file_articleIDToLDA
from DataCreators import LDAModel


class Expander_LDA(AcronymExpander):
    """
    Expand acronyms based on their closeness to the Latent Dirichlet Allocation
    vectors of articles containing expansions of the acronym
    """

    def __init__(self):
        logger.info("Loading LDA model and dictionary")
        self.ldamodel, self.dictionary, self.articleIDToLDADict = LDAModel.load()

    def expand(self, acronym, acronymExpansion, text):
        choices = self.getChoices(acronym)

        cleaned_words = getCleanedWords(text)
        bow = self.dictionary.doc2bow(cleaned_words)
        target_lda = self.ldamodel[bow]

        min_cos_dist = sys.maxint
        chosen_expansion = ""
        for choice in choices:
            choice_lda = self.articleIDToLDADict[choice.article_id]
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
