"""
These are classes which expand acronyms.
All classes here have to inherit AcronymExpander class.
List all the expanders in the enum below
"""
from DataCreators import ArticleDB, AcronymDB
from Logger import logger
class AcronymExpanderEnum():
    none = "None"
    fromText = "Text"
    fromText_v2 = "Text v2"
    SVC = "SVC"
    LDA = "LDA"

articleDB = ArticleDB.load()
logger.info("AcronymDB loaded")

acronymDB = AcronymDB.load()
logger.info("ArticleDB loaded")
