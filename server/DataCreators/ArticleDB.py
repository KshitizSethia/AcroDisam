"""
collection of functions used to manipulate the articledb dictionary
articledb is a dictionary in the format (article_id: article_text)
"""
import cPickle as pickle
import csv
import sys

from Logger import logger
import string_constants


def createFromScrapedArticles():
    logger.info("Creating ArticleDB")
    csv.field_size_limit(sys.maxint)
    
    # open as csv file with headers
    article_csv = csv.DictReader(open(string_constants.file_scraped_articles, "rb")
                                 , delimiter=",")
    articleDB = {}
    loaded_articles = 0
    for row in article_csv:
        articleDB[row["article_id"]] = row["article_text"]
        loaded_articles += 1
        if(loaded_articles % 10000==0):
            logger.debug("loaded %d articles", loaded_articles)
    
    dump(articleDB)
    logger.info("Dumped ArticleDB successfully")
        
def dump(articleDB):
    pickle.dump(articleDB
                 , open(string_constants.file_articledb, "wb")
                 , protocol=2)

def load():
    return pickle.load(open(string_constants.file_articledb, "rb"))

def addArticles(articleDB, articles):
    """ 
    takes in array of [article_id, article_text] entries 
    and adds them to articleDB
    returns articleDB with added articles
    """

    for [article_id, article_text] in articles:
        articleDB[article_id] = article_text
    
    return articleDB

if __name__ == "__main__":
    createFromScrapedArticles()
