
import os
import string
from vark_extract import get_font_filtered_text, get_text
import numpy as np
import pandas as pd
import re
from sklearn.svm import LinearSVC
from sklearn.externals import joblib
import shelve
import time
import cPickle

def get_acronyms(text):  # Find Acronyms in text
    english_words = set(word.strip().lower() for word in open(os.path.join(data_path, "wordsEn.txt")))
    pattern = r'\b[A-Z]{3,8}s{0,1}\b'  # Limit length 8
    acronyms = re.findall(pattern, text)
    acronyms = [acronym for acronym in acronyms if acronym.lower() not in english_words]
    return set(acronyms)


def definition_patterns(acronym):  # Create definition regex patterns from acronym
    def_pattern1, def_pattern2 = r'', r''
    between_chars1 = r'\w{3,}[-\s](?:\w{2,5}[-\s]){0,1}'
    between_chars2 = r'\w+[-\s]{0,1}(?:\w{2,5}[-\s]{0,1}){0,1}'
    for i, c in enumerate(acronym):
        c = "[" + c + c.lower() + "]"
        if i == 0:
            def_pattern1 += r'\b' + c + between_chars1
            def_pattern2 += r'\b' + c + between_chars2
        elif i < len(acronym) - 1:
            def_pattern1 += c + between_chars1  # acronym letter, chars, periods, space
            def_pattern2 += c + between_chars2
        else:
            def_pattern1 += c + r'\w+\b'
            def_pattern2 += c + r'\w+\b'
    acronym = r'' + acronym + r'\b'
    patterns = []
    for def_pattern in [def_pattern1, def_pattern2]:
        patterns = patterns + [def_pattern + r'(?=\sor\s{0,1}(?:the\s){0,1}(?:a\s){0,1}' + acronym + r')',
                           def_pattern + r'(?=["(\s,]{2,}(?:or\s){0,1}(?:the\s){0,1}["]{0,1}' + acronym + r')',
                           r'(?<=' + acronym + r'\s\W)' + def_pattern]
    print "Acronym", acronym
    for pattern in patterns:
        print pattern
    patterns = [re.compile(pattern) for pattern in patterns]
    return patterns

def text_expand(acronym, text, patterns):  # Search original text for acronyms
    for pattern in patterns:
        pattern_result = re.findall(pattern, text)
        if pattern_result:
            return pattern_result[0]
    return None

def db_lookup(acronym):  # Lookup acronym in database
    results = []
    if acronym in acronymdb:
        results += acronymdb[acronym]
    if acronym[-1] == 's' and acronym[:-1] in acronymdb:  # plural / sing forms
        results += acronymdb[acronym[:-1]]
    definitions = []
    for definition, articleid, title, def_count in results:
        text = articledb[articleid]
        definitions.append([definition, text])
    return np.array(definitions)

def distinct_results(results):  # This relies on db returning ordered results
    count = len(results)
    if count <= 1:
        return False
    else:
        res1 = results[0][0].strip().lower().replace('-', ' ')
        res1 = ' '.join([w[:4] for w in res1.split()])
        res2 = results[-1][0].strip().lower().replace('-', ' ')
        res2 = ' '.join([w[:4] for w in res2.split()])
        if res1 != res2:
            return True
        return False

def db_expand(acronym, text):  # Chooses expansion from db
    results = db_lookup(acronym)
    if len(results) == 0:
        pred_exp = "NONE FOUND"
    elif not distinct_results(results):
        pred_exp = results[0][0]
    else:
        definitions, articles = results[:, 0], results[:, 1]
        X = vectorizer.transform(articles)
        clf = LinearSVC(C=1., loss='l1')
        Y = definitions
        clf.fit(X, Y)
        s = vectorizer.transform([text.translate(string.maketrans("", ""), string.punctuation)])
        pred_exp = clf.predict(s)[0]
    return pred_exp

def expand(acronym, text):  # Top level expansion function, calls others
    print text
    patterns = definition_patterns(acronym)
    definition = text_expand(acronym, text, patterns)
    if definition:
        return definition + " (from text)"
    else:
        return db_expand(acronym, text)

def is_same_expansion(true_exp, pred_exp):
    true_exp = true_exp.strip().lower().replace('-', ' ')
    pred_exp = ' '.join([w[:4] for w in pred_exp.split()])
    true_exp = ' '.join([w[:4] for w in true_exp.split()])
    if pred_exp == true_exp:
        return True
    #    ed = distance.edit_distance(pred_exp, true_exp)
    #    if ed < 3:
    #        return True
    return False



def expand_acronyms(path):
    t00 = time.time()
    try:
        filtered_text = get_font_filtered_text(path)
        all_text = get_text(path)
        acronyms = list(get_acronyms(filtered_text))[:100]  # Limit to 100
        result = []
        for acronym in acronyms:
            acr_t0 = time.time()
            definition = ' '.join(expand(acronym, all_text).split())
            result.append(acronym + ': ' + definition)
        return result
    except IndexError:
        return 'The document at ' + path + ' could not be parsed.  Please try again with plaintext, or a different document.'




# **************************  SETUP  **************************

script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
data_path = script_dir + '/values_for_this_acronym/'

data_path = script_dir + '\\data\\'
# data_path = '/Users/Ben/Desktop/masters_thesis/webapp/static/'
vectorizer = joblib.load(os.path.join(data_path, "vectorizer"))

acronym_csv = pd.read_csv(data_path + 'scraped_definitions.csv')

# articledb = shelve.open(data_path+'articledb')    # Open articledb

import csv
import sys
articledb = {}
print 'Importing articles...'
n = 0
# csv.field_size_limit(sys.maxsize) #todo: uncomment this line
csv.field_size_limit(sys.maxint)
with open(data_path + '/scraped_articles.csv', 'rb') as f:
    article_csv_file = csv.reader(f, delimiter=',')
    for row in article_csv_file:
        id = row[0]
        text = row[1]
        articledb[id] = text
        n += 1
        if n % 10000 == 0:
            print n

acronymdb = {}  # Preprocess Acronym Defs
for acronym, expantion, articleid, article_title in acronym_csv.values:
    if acronym not in acronymdb:
        acronymdb[acronym] = []
    acronymdb[acronym].append([expantion.strip().lower().replace('-', ' '), articleid, article_title])

defs_per_acronym = [0] * 1000
insts_per_def = [0] * 1000  # doubt: what does this variable mean?
num_acronyms = len(acronymdb)
for acronym, values_for_this_acronym in acronymdb.items():
    values_for_this_acronym = sorted(values_for_this_acronym
									, key=lambda x:x[0])
    def_count = 0
    inst_count = 0
    expansion_of_last_acronym = values_for_this_acronym[0][0]
    for i, (acronym_expansion, article_id, article_title) in enumerate(values_for_this_acronym):
        if is_same_expansion(acronym_expansion, expansion_of_last_acronym):
            inst_count += 1
            values_for_this_acronym[i].append(def_count)  # doubt: what's this used for?
            values_for_this_acronym[i][0] = expansion_of_last_acronym
        else:
            insts_per_def[min(inst_count, len(insts_per_def) - 1)] += 1  # doubt: to keep indices inside 1000? if yes, then loop only 1000 times
            inst_count = 0
            def_count += 1
            expansion_of_last_acronym = acronym_expansion
            values_for_this_acronym[i].append(def_count)  # doubt: same as line 177
            # doubt: same line as above in line 177, move outside if-else?
    defs_per_acronym[min(def_count, len(defs_per_acronym) - 1)] += 1
    acronymdb[acronym] = np.array(values_for_this_acronym)

# cPickle.dump(acronymdb, open("data/acronymdb.pickle", "w"))
# cPickle.dump(articledb, open("data/articledb.pickle", "w"))

# *******************************************************************
