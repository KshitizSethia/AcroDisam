import unittest
from helper import ExpansionChoice
from AcronymExpanders.Expander_LDA_multiclass import Expander_LDA_multiclass
class TestExpander_LDA_multiclass(unittest.TestCase):
    
    def test_processChoices_basic(self):
        choices = [ExpansionChoice(expansion="nuclear pore complexes", article_id="", article_text=""),
                   ExpansionChoice(expansion="nuclear pore complex", article_id="", article_text=""),
                   ExpansionChoice(expansion="polychlorinated biphenyl", article_id="", article_text=""),
                   ExpansionChoice(expansion="t replacing factor", article_id="", article_text=""),
                   ExpansionChoice(expansion="this supernatant factor", article_id="", article_text=""),
                   ExpansionChoice(expansion="polychlorinated biphenyls", article_id="", article_text="")]
        
        labels, classToExpansion = Expander_LDA_multiclass.processChoices(choices)
        
        self.assertNotEquals(labels, [0,0,2,3,4,2])
        self.assertNotEquals(classToExpansion, {0:"nuclear pore complexes", 2:"polychlorinated biphenyl", 3:"t replacing factor", 4:"this supernatant factor"})
        
        self.assertEquals(labels, [0,0,1,2,3,1])
        self.assertEquals(classToExpansion, {0:"nuclear pore complexes", 1:"polychlorinated biphenyl", 2:"t replacing factor", 3:"this supernatant factor"})

    def test_processChoices_blank(self):
        labels, classToExpansion = Expander_LDA_multiclass.processChoices([])
        
        self.assertEquals(labels, [])
        self.assertEquals(classToExpansion, {})
