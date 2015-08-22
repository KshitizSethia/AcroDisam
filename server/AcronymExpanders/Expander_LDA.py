from gensim.matutils import cossim

from AcronymExpanders import AcronymExpanderEnum
from AcronymExpanders.AcronymExpander import AcronymExpander
from Logger import common_logger
from TextTools import getCleanedWords
from DataCreators.LDAModel import SavedLDAModel
from DataCreators import LDAModel
from helper import AcronymExpansion


class Expander_LDA(AcronymExpander):
    """
    Expand acronyms based on their cosine similarity to the Latent Dirichlet Allocation
    vectors of articles containing expansions of the acronym
    """

    def __init__(self, articleDB, acronymDB):
        common_logger.info("Loading LDA model and dictionary")
        AcronymExpander.__init__(self, articleDB, acronymDB)

        lda_model_all = LDAModel.load()
        self.ldamodel = lda_model_all.ldaModel
        self.dictionary = lda_model_all.dictionary
        self.articleIDToLDADict = lda_model_all.articleIDToLDADict
        self.stem_words = lda_model_all.stem_words
        self.removeNumbers = lda_model_all.removeNumbers

        self.expander_type = AcronymExpanderEnum.LDA_cossim

    def getChosenExpansion(self, choices, target_lda):
        max_cos_sim = -1.0
        chosen_expansion = ""
        for choice in choices:
            choice_lda = self.articleIDToLDADict[choice.article_id]
            cos_sim = cossim(target_lda, choice_lda)
            if (cos_sim > max_cos_sim):
                chosen_expansion = choice.expansion
                max_cos_sim = cos_sim

        # todo: make this return a confidence score as well
        # low priority as multiclass is performing better than this
        return chosen_expansion

    def expand(self, acronym, acronymExpansions, text):
        choices = self.getChoices(acronym)

        cleaned_words = getCleanedWords(
            text, stem_words=self.stem_words, removeNumbers=self.removeNumbers)
        bow = self.dictionary.doc2bow(cleaned_words)
        target_lda = self.ldamodel[bow]

        chosen_expansion, confidence = self.getChosenExpansion(choices, target_lda)
        if(chosen_expansion != ""):
            acronymExpansions.append(
                AcronymExpansion(expansion=chosen_expansion
                                 , expander=self.expander_type
                                 , confidence=confidence))

        return acronymExpansions
