class AcronymExpansion:
    def __init__(self, expansion, expander):
        self.expansion = expansion
        self.expander = expander
    def __str__(self):
        return self.expander + "," + self.expansion

class ExpansionChoice:
    def __init__(self, expansion, article_id, article_text):
        self.expansion = expansion
        self.article_id = article_id
        self.article_text = article_text