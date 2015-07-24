"""
Test TextTools.getCleanedWords() by visual inspection
"""
from DataCreators import ArticleDB
import TextTools

articles = ArticleDB.load()

article = articles.values()[0]

print article 

words = TextTools.getCleanedWords(article)
print words

"""
**************************************************************************************************
Check if duplication in scraped_articles is creating article_id: article_text pairs where the acronym is not present
"""
"""
from DataCreators import AcronymDB, ArticleDB
acronymdb = AcronymDB.load()
articledb = ArticleDB.load()#todo:
"""

"""
Re-format the old CSV files to reflect new changes
new scraped_article_infos file
    format: article_id, article_title, article_source
""""""
import cPickle

from string_constants import file_article_infodb, file_scraped_article_info
import csv


article_info = cPickle.load(open(file_article_infodb, "rb"))

headers = ["article_id", "article_title", "article_source"]
csv_writer = csv.DictWriter(
    open(file_scraped_article_info, "wb"), fieldnames=headers)
csv_writer.writeheader()

for article_id in article_info.keys():
    rowdict = {"article_id": article_id, "article_title": article_info[
        article_id][0]}
    
    if(len(article_info[article_id]) == 2):
        rowdict["article_source"] = article_info[article_id][1]

    csv_writer.writerow(rowdict)
"""

"""
**************************************************************************************************
Check scraped_articles for duplicate entries
""""""
from collections import Counter
import csv
import sys

from matplotlib import pyplot

from string_constants import file_scraped_articles


csv.field_size_limit(sys.maxint)
scraped_articles = csv.DictReader(open(file_scraped_articles, "rb"), delimiter=",")

tracker = Counter()
line_num = 1
for line in scraped_articles:
    article_id = line["article_id"]
     
    # if article_id in tracker:
    #    print "First, line " +str(line_num)
    #    print tracker[article_id]
    #    print "Second, line " +str(line_num)
    #    print line["article_text"]
    #    raise Exception
    # line_num+=1
    tracker[article_id] += 1

#unique_repetition_values = list(set(tracker.values()))    
#pyplot.plot(tracker.values())
#pyplot.yticks(unique_repetition_values)
#pyplot.hist(tracker.values(), bins=len(unique_repetition_values))
#pyplot.xticks(unique_repetition_values)
#pyplot.grid()
#pyplot.show()

duplicates = {}
for article_id in tracker.keys():
    if(tracker[article_id]!=1):
        duplicates[article_id] = tracker[article_id]
 
articles_lost = sum(duplicates.values())-len(duplicates.keys())
print "articles lost: " +str(articles_lost)
#unique_duplication_counts = list(set(duplicates.values()))    
#pyplot.subplot(211)
#pyplot.title("plotting duplicate counts")
#pyplot.plot(duplicates.values())
#pyplot.yticks(unique_duplication_counts)
#pyplot.grid()
#
#pyplot.subplot(212)
#pyplot.title("histogram of duplicate counts")
#pyplot.hist(duplicates.values(), bins=len(unique_duplication_counts))
#pyplot.grid()
#
#pyplot.show()

#print type(tracker.values())
#print len(tracker.values())
#print sum(tracker.values())
#print tracker.values()
"""

"""
**************************************************************************************************
Re-format the old CSV files to reflect new changes
scraped_articles
    old format: article_id,article_text,article_path
    new format: article_id,article_text
""""""
import csv
import sys

from string_constants import file_scraped_articles


csv.field_size_limit(sys.maxint)
old_article_file = csv.DictReader(open(file_scraped_articles, "rb"), delimiter=",")

headers = ["article_id", "article_text"]
new_article_file = csv.DictWriter(open(file_scraped_articles + ".new", "wb"), fieldnames=headers)
new_article_file.writeheader()

for line in old_article_file:
    article_id = line["article_id"]
    article_text = line["article_text"]
    
    new_article_file.writerow({"article_id": article_id, "article_text":article_text})
"""

"""
**************************************************************************************************
Re-format the old CSV files to reflect new changes
scraped_definitions
    old format: acronym,acronym_expansion,article_id,article_title
    new format: acronym,acronym_expansion,article_id
""""""
import csv
import sys
from string_constants import file_scraped_definitions

csv.field_size_limit(sys.maxint)
old_acronym_file = csv.DictReader(open(file_scraped_definitions, "rb"), delimiter=",")

headers = ["acronym","acronym_expansion","article_id"]
new_acronym_file = csv.DictWriter(open(file_scraped_definitions+".new", "wb"), fieldnames=headers)
new_acronym_file.writeheader()

for line in old_acronym_file:
    acronym = line["acronym"]
    expansion = line["acronym_expansion"]
    article_id = line["article_id"]
    
    new_acronym_file.writerow({"acronym": acronym, "acronym_expansion": expansion, "article_id": article_id})
"""

"""
**************************************************************************************************
Examine acronymDB, and extract articleID: [article_title, article_source] from it
"""
"""
from string_constants import file_scraped_definitions, file_article_infodb, file_scraped_articles
import csv
import sys
import cPickle
from Logger import logger

csv.field_size_limit(sys.maxint)
old_acronym_file = csv.DictReader(open(file_scraped_definitions, "rb"), delimiter=",")

# dictionary of the form: articleID: [article_title, article_source]
article_info = {}

# put article_title in dictionary
for line in old_acronym_file:
    article_id = line["article_id"]
    article_title = line["article_title"]
    if article_id in article_info:
        if article_title not in article_info[article_id]:
            article_info[article_id].append(article_title)
            logger.critical("article_info creation: " + article_id + ": " + str(article_info[article_id]))
        else:
            continue
    else:
        article_info[article_id] = [article_title]
        
# put article_source in dictionary
old_article_file = csv.DictReader(open(file_scraped_articles, "rb"), delimiter=",")
for line in old_article_file:
    article_id = line["article_id"]
    article_source = line["article_path"]
    if(len(article_info[article_id]) == 1):
        article_info[article_id].append(article_source)
    else:  # (len(article_info[article_id])>2):
        article_info[article_id][-1] += "," + article_source
    
    if((len(article_info[article_id]) > 2)):
        logger.critical("article_info creation: " + article_id + ": " + str(article_info[article_id]))

    

cPickle.dump(article_info, open(file_article_infodb, "wb"), protocol=2)
"""

"""
**************************************************************************************************
Remove article_title from acronymdb
"""
"""
import DataCreators.AcronymDB as AcronymDB

acronymDB = AcronymDB.load()

for acronym in acronymDB.keys():
    expansions = acronymDB[acronym]
    new_expansions = []
    for expansion in expansions:
        new_expansions.append(expansion[:-2])
    
    for expansion in new_expansions:
        if(len(expansion)!=2):
            raise Exception
    
    acronymDB[acronym] = new_expansions

AcronymDB.dump(acronymDB)
"""
