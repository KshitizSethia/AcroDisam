"""
These are classes which expand acronyms.
All classes here have to inherit AcronymExpander class.
List all the expanders in the enum below
"""
from Logger import logger
class AcronymExpanderEnum():
    none = "None"
    fromText = "Text"
    fromText_v2 = "Text v2"
    SVC = "SVC"
    LDA = "LDA"
