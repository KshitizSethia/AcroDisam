class AcronymExpansion:
    def __init__(self, expansion, expander):
        self.expansion = expansion
        self.expander = expander
    def __str__(self):
        return self.expander + "," + self.expansion
