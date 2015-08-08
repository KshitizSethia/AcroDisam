from nltk.metrics.distance import edit_distance

from Logger import common_logger


class AcronymExpansion:

    def __init__(self, expansion, expander):
        self.expansion = expansion
        self.expander = expander

    def __str__(self):
        return self.expander + "," + self.expansion

    @staticmethod
    def areDistinctChoices(choices):
        """
        Tell whether the choices are distinct
        #todo: This should be done at DB build time
        """
        count = len(choices)
        if(count <= 1):
            return False
        else:
            res1 = choices[0].expansion.strip().lower().replace('-', ' ')
            res1 = ' '.join([w[:4] for w in res1.split()])
            res2 = choices[-1].expansion.strip().lower().replace('-', ' ')
            res2 = ' '.join([w[:4] for w in res2.split()])
            if res1 != res2:
                return True
            return False

    @staticmethod
    def startsSameWay(true_exp, pred_exp):
        true_exp = true_exp.strip().lower().replace("-", " ")
        pred_exp = " ".join([word[:4] for word in pred_exp.split()])
        true_exp = " ".join([word[:4] for word in true_exp.split()])
        if(pred_exp == true_exp):
            return True
        #    ed = distance.edit_distance(pred_exp, true_exp)
        #    if ed < 3:
        #        return True
        return False

    @staticmethod
    def areExpansionsSimilar(actual_expansion, predicted_expansion):
        actual_expansion = actual_expansion.lower().replace(u"-", u" ")
        predicted_expansion = predicted_expansion.lower().replace(u"-", u" ")
        #numActualWords = len(actual_expansion)
        #numPredictedWords = len(predicted_expansion)

        if(actual_expansion == predicted_expansion
           or AcronymExpansion.startsSameWay(actual_expansion, predicted_expansion)
           or edit_distance(actual_expansion, predicted_expansion) <= 2):  # max(numActualWords, numPredictedWords)):
            return True

        return False


class ExpansionChoice:

    def __init__(self, expansion, article_id, article_text):
        self.expansion = expansion
        self.article_id = article_id
        self.article_text = article_text
