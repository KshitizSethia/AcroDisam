"""
collection of functions used to manipulate the articledb dictionary
articledb is a dictionary in the format (article_id: article_text)
"""
import cPickle as pickle
import csv
import sys

from Logger import common_logger
from string_constants import file_scraped_articles_list, file_articledb
from TextTools import toUnicode


def createFromScrapedArticles():
    common_logger.info("Creating ArticleDB")
    csv.field_size_limit(sys.maxint)

    articleDB = {}
    loaded_articles = 0
    for article_file in file_scraped_articles_list:
        # open as csv file with headers
        article_csv = csv.DictReader(open(article_file, "rb"), delimiter=",")

        for row in article_csv:
            article_id = toUnicode(row["article_id"])
            articleDB[article_id] = toUnicode(row["article_text"])
            loaded_articles += 1
            if(loaded_articles % 10000 == 0):
                common_logger.debug("loaded %d articles", loaded_articles)

    dump(articleDB)
    common_logger.info("Dumped ArticleDB successfully")


def dump(articleDB):
    pickle.dump(
        articleDB, open(file_articledb, "wb"), protocol=2)


def load(path=file_articledb):
    common_logger.debug("loading articleDB from %s" %path)
    return pickle.load(open(path, "rb"))


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
