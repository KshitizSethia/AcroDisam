"""
Collection of functions used to manipulate the article_info_db dictionary 
with the format (article_id: [article_title, article_source])
article_source may be 
    a single entry
    a list of entries, each seperated by a comma 
        (this is for backward compatibility only, do not use in new code)
"""
from Logger import logger
import csv
import sys
import cPickle as pickle
from string_constants import file_scraped_article_info, file_article_infodb


class ArticleInfo:
    article_id = "article_id"
    article_title = "article_title"
    article_source = "article_source"


def fromCSV():
    logger.info("Creating ArticleInfoDB")
    csv.field_size_limit(sys.maxint)

    article_info_csv = csv.DictReader(
        open(file_scraped_article_info, "rb"), delimiter=",")

    article_info_db = {}
    for row in article_info_csv:
        article_info_db[row[ArticleInfo.article_id]] = [
            row[ArticleInfo.article_title], row[ArticleInfo.article_source]]

    logger.info("Done creating ArticleInfoDB")
    return article_info_db


def toCSV(article_info_db):
    headers = [ArticleInfo.article_id,
               ArticleInfo.article_title, ArticleInfo.article_source]

    csv_writer = csv.DictWriter(
        open(file_scraped_article_info, "wb"), fieldnames=headers)
    csv_writer.writeheader()

    for article_id in article_info_db.keys():
        rowdict = {ArticleInfo.article_id: article_id,
                   ArticleInfo.article_title: article_info_db[article_id][0]}

        if(len(article_info_db[article_id]) == 2):
            rowdict[ArticleInfo.article_source] = article_info_db[
                article_id][1]

        csv_writer.writerow(rowdict)


def dump(article_info_db):
    pickle.dump(article_info_db, open(file_article_infodb, "wb"), protocol=2)


def load():
    return pickle.load(open(file_article_infodb, "rb"))

if __name__ == "__main__":
    dump(fromCSV())
