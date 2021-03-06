"""
This file contains all the strings (file/folder paths, error messages, etc)
that the program can use
"""


import os


"""Paths for folders and files"""
sep = os.path.sep
folder_root = os.path.dirname(os.path.realpath(__file__)) + sep

folder_output = folder_root + "storage" + sep + "outputs" + sep
folder_upload = folder_root + "storage" + sep + "uploads" + sep
folder_data = folder_root + "storage" + sep + "data_small" + sep
folder_logs = folder_root + "logs" + sep

folder_lda = folder_data + "lda" + sep

folder_msh_corpus = folder_data + "MSHCorpus" + sep
folder_msh_arff = folder_msh_corpus + "arff" + sep

folder_scienceWise = folder_data + "ScienceWISE" + sep
folder_scienceWise_pdfs = folder_scienceWise + "pdfs" + sep

for folder in [folder_output, folder_data, folder_upload, folder_logs, folder_lda, folder_msh_corpus, folder_msh_arff, folder_scienceWise, folder_scienceWise_pdfs]:
    if(not os.path.exists(folder)):
        os.makedirs(folder)

file_acronymdb = folder_data + "acronymdb.pickle"
file_article_infodb = folder_data + "article_infodb.pickle"
file_articledb = folder_data + "articledb.pickle"
file_articledb_shuffled = folder_data +"articledb_shuffled.pickle"
file_english_words = folder_data + "wordsEn.txt"
file_errorpage = "500.html"
file_homepage = "index.html"

file_benchmark_report_pickle = folder_logs + "report_benchmark.pickle"
file_benchmark_report = folder_logs + "report_benchmark.txt"

file_lda_articleIDToLDA = folder_lda + "articleIDToLDA.pickle"
file_lda_bow_corpus = folder_lda + "bow_corpus.bin"
file_lda_gensim_dictionary = folder_lda + "gensim_dictionary.bin"
file_lda_model = folder_lda + "lda_model.bin"
file_lda_word_corpus = folder_lda + "temp_word_corpus.bin"
file_lda_model_all = folder_lda + "lda_model_noStem_noNums_3Pass.pickle"

file_logs = folder_logs + "log.txt"

file_msh_articleDB = folder_msh_corpus + "articledb.pickle"
file_msh_articleDB_shuffled = folder_msh_corpus + "articledb_shuffled.pickle"
file_msh_acronymDB = folder_msh_corpus + "acronymdb.pickle"
file_msh_manual_corrections = folder_msh_corpus + "ManualCorrections.csv"
file_msh_articleIDToAcronymExpansions = folder_msh_corpus + \
    "articleIDToAcronymExpansions.pickle"

file_ScienceWise_index_train = folder_scienceWise + "sw_train_abstracts.txt"

file_scraped_article_info = folder_data + "scraped_article_info.csv"
file_scraped_articles_list = [folder_data + "scraped_articles.csv"]
file_scraped_definitions_list = [folder_data + "scraped_definitions.csv"]
file_vectorizer = folder_data + "vectorizer"

"""Miscellaneous"""
name_logger = "acronym_disambiguator"
string_unexpanded_acronym = "___EXPANSION_NOT_FOUND___"
max_confidence = 10.0
min_confidence = -5.0

"""Error strings"""
string_error_no_results_to_show = "No acronyms (between 3 and 8 letters long) were found"
string_error_document_parse = 'The document could not be parsed.  Please try again with plaintext, or a different document.'
