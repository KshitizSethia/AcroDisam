from gensim.matutils import cossim

from AcronymExpanders import AcronymExpanderEnum
from AcronymExpanders.AcronymExpander import AcronymExpander
from DataCreators import LDAModel
from Logger import logger
from TextTools import getCleanedWords


class Expander_LDA(AcronymExpander):
    """
    Expand acronyms based on their closeness to the Latent Dirichlet Allocation
    vectors of articles containing expansions of the acronym
    """

    def __init__(self, articleDB, acronymDB):
        logger.info("Loading LDA model and dictionary")
        AcronymExpander.__init__(self, articleDB, acronymDB)
        self.ldamodel, self.dictionary, self.articleIDToLDADict = LDAModel.load()

    def expand(self, acronym, acronymExpansion, text):
        choices = self.getChoices(acronym)

        cleaned_words = getCleanedWords(text)
        bow = self.dictionary.doc2bow(cleaned_words)
        target_lda = self.ldamodel[bow]

        max_cos_sim = -1.0
        chosen_expansion = ""
        for choice in choices:
            choice_lda = self.articleIDToLDADict[choice.article_id]
            cos_sim = cossim(target_lda, choice_lda)
            if(cos_sim > max_cos_sim):
                chosen_expansion = choice.expansion
                max_cos_sim = cos_sim
        if(chosen_expansion != ""):
            acronymExpansion.expansion = chosen_expansion
            acronymExpansion.expander = AcronymExpanderEnum.LDA
        return acronymExpansion
