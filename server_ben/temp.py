import codecs
from nltk import word_tokenize

def getWords(path):
    lines = codecs.open(path, "r", "UTF", errors='replace')
    words = []
    for num, line in enumerate(lines):
        line.replace("\\xad", "-")
        parts = word_tokenize(line)
        words.extend(parts)
         
    return set(words)

def output(words):
    for word in words:
        print repr(word)

#set of words in file from text copy paste
base_words = getWords(r"C:\Users\Kshitiz\Downloads\acro\text.txt")
print len(base_words)

#set of words in file from PdfBox
new_words = getWords(r"C:\Users\Kshitiz\Downloads\acro\pdfMiner2.txt")
print len(new_words)
#output(new_words)

not_in_new = base_words.difference(new_words)

not_in_base = new_words.difference(base_words)


print "done"