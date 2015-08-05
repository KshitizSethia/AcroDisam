"""
**************************************************************************************************
Check what's the role of PMID in MSH Corpus
"""

from arff import load
import os

pmids = {}
folder = r"C:\Cloud\github\AcroDisam\server\storage\data_all\MSHCorpus\arff"
for file_name in os.listdir(folder):
    file_path = os.path.join(folder, file_name)
    for row in load(file_path):
        pmid = row.PMID
        if(pmid not in pmids):
            pmids[pmid] = []
        pmids[pmid].append(file_name)

for pmid in pmids:
    if len(pmids[pmid])>1:
        print("PMID %s is repeated" %str(pmid))
print(len(pmids.keys()))

"""
PMID is a unique identifier of citation text in the MSH corpus
"""

#print(pmids)

"""
**************************************************************************************************
Create a smaller DBs for debugging/testing scripts
Steps:
- Copy the following files to a new_folder:
        scraped_article_info.csv
        scraped_articles.csv
        scraped_definitions.csv
        vectorizer
        vectorizer_01.npy
        vectorizer_02.npy
        wordsEn.txt
- Keep relevant articles from scraped_articles in scraped_articles.csv
- Change data folder in string_constants to point to new_folder
- Run the script below
"""
"""
import csv
import os

from DataCreators import ArticleDB, AcronymDB, ArticleInfoDB
from string_constants import file_scraped_articles_list,\
    file_scraped_definitions_list, file_scraped_article_info
import sys

csv.field_size_limit(sys.maxint)

## Get articleIDs which are needed in each DB
articleIds = []
for file in file_scraped_articles_list:
    for line in csv.DictReader(open(file,"rb"), delimiter=","):
        articleIds.append(line["article_id"])

## Save smaller version of scraped definitions csv
file_path = file_scraped_definitions_list[0]    
small_path = file_path+".csv"
with open(file_path, "rb") as infile, open(small_path, "wb") as outfile:
    source_csv = csv.DictReader(infile, delimiter=",")
    
    headers = ["acronym","acronym_expansion","article_id"]
    small_csv = csv.DictWriter(outfile, fieldnames=headers)
    small_csv.writeheader()
    
    for line in source_csv:
        if(line["article_id"] in articleIds):
            small_csv.writerow(line)

os.remove(file_path)
os.rename(small_path, file_path)

## Save smaller version of scraped article info csv
file_path = file_scraped_article_info    
small_path = file_path+".small"
with open(file_path, "rb") as infile, open(small_path, "wb") as outfile:
    source_csv = csv.DictReader(infile, delimiter=",")
    
    headers = ["article_id","article_title","article_source"]
    small_csv = csv.DictWriter(outfile, fieldnames=headers)
    small_csv.writeheader()
    
    for line in source_csv:
        if(line["article_id"] in articleIds):
            small_csv.writerow(line)
    
os.remove(file_path)
os.rename(small_path, file_path)

## Make new DB files
ArticleDB.createFromScrapedArticles()
AcronymDB.createFromScrapedDefinitions()
ArticleInfoDB.dump(ArticleInfoDB.fromCSV())
"""

"""
**************************************************************************************************
Handle missing article aHR0cHM6Ly9lbi53aWtpcGVkaWEub3JnL3dpa2kvU2h1amFheg== in articleDB
"""
"""
import csv
import sys

from DataCreators import ArticleDB
from string_constants import file_scraped_articles


articleDB = ArticleDB.load()
csv.field_size_limit(sys.maxint)
file = csv.DictReader(open(file_scraped_articles,"rb"), delimiter=",")

changeSuccessful = False

for line in file:
    if(line["article_id"] == "aHR0cHM6Ly9lbi53aWtpcGVkaWEub3JnL3dpa2kvU2h1amFheg=="):
        articleDB[line["article_id"]] = line["article_text"]
        changeSuccessful = True

if changeSuccessful:
    ArticleDB.dump(articleDB)
else:
    print "badluck!"
"""

"""
**************************************************************************************************
Check if duplication in scraped_articles is creating article_id: article_text pairs where the acronym is not present
"""
"""
from __future__ import division
from DataCreators import AcronymDB, ArticleDB
acronymDB = AcronymDB.load()
articleDB = ArticleDB.load()

errors = []
missing_articles=[]
numSuccesses = 0

for acronym in acronymDB.keys():
    for expansion, article_id, def_count in acronymDB[acronym]:
        if(article_id in articleDB):
            article = articleDB[article_id].lower()
            expansion = expansion.lower()
            if(acronym.lower() not in article):# or expansion not in article):
                errors.append([acronym, expansion, article_id])
            else:
                numSuccesses+=1
        else:
            missing_articles.append(article_id)

print "errors:", len(errors), "successes: ", numSuccesses, "%age error: ", len(errors)*100/(len(errors)+numSuccesses)
print errors[:10]

missing_articles = set(missing_articles)
print "missing articles: " +str(len(missing_articles))
print missing_articles
"""

"""
**************************************************************************************************
Test TextTools.getCleanedWords() by visual inspection
"""
"""
from DataCreators import ArticleDB
import TextTools

articles = ArticleDB.load()

article = articles.values()[0]

print article 

words = TextTools.getCleanedWords(article)
print words
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
