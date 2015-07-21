from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.externals import joblib
import shelve
import csv
import sys

article_csv_file = csv.reader(open('data/scraped_articles.csv', 'rb'), delimiter=',')
article_csv=[]
csv.field_size_limit(sys.maxint)
for row in article_csv_file:
    id = row[0]
    text = row[1]
    article_csv.append([id, text])


n = 0
csv.field_size_limit(sys.maxint)
article_samples=[]
for row in article_csv:
    if n%20 ==0:
        id = row[0]
        text = row[1]
        #source = row[2] #FIXME: this index is not created!!
        article_samples.append(text)
    n += 1
    if n % 10000 ==0:
        print n
    if n > 30000:
        break

vectorizer = TfidfVectorizer(max_df=1.0, max_features=10000, stop_words='english', use_idf=True, binary=False, decode_error='ignore')
vectorizer.fit(article_samples)

joblib.dump(vectorizer, 'data/vectorizer')


article_csv = csv.reader(open('data/scraped_articles.csv', 'rb'), delimiter=',')#doubt: why not reuse article_csv_file?
articlevectdb = shelve.open('data/articlevdb')

print 'Importing articles...'
n = 0
csv.field_size_limit(sys.maxint)
for row in article_csv:
    id = row[0]
    text = row[1]
    source = row[2]
    articlevectdb[id]=text#doubt: nothing is being done with this variable
    n += 1
    if n % 10000 ==0:
        print n

print "stored %d articles" % n
#article.close()#doubt: what is being closed here?
articlevectdb.close()

#    articlevectdb[id] = vectorizer.transform([text])[0]



# Try to save numpy arrays instead

vectorizer = joblib.load('Desktop/masters_thesis/cims/vectorizer')

article_csv = csv.reader(open('Desktop/masters_thesis/webapp/data/scraped_articles.csv', 'rb'), delimiter=',')

article_ids=[]
article_vects=[]

print 'Importing articles...'
n = 0
csv.field_size_limit(sys.maxsize)
for row in article_csv:
    id = row[0]
    text = row[1]
    source = row[2]
    article_ids.append(id)
    article_vects.append(vectorizer.transform([text])[0])
    n += 1
    if n % 10000 ==0:
        print n




# For saving vectorizer from cims
from sklearn.externals import joblib
import pickle

vectorizer = joblib.load('data/vectorizer')
output = open('data/vectdata.pkl','wb')
pickle.dump(vectorizer, output)
output.close()

# now read it
import pickle
vectorizer = pickle.load(open('Desktop/masters_thesis/cims/vectdata.pkl'))


###
print 'Importing articles...'
n = 0
for row in article_csv:
    id = row[0]
    text = row[1]
    articledb[id]=text
    n += 1
    if n % 10000 ==0:
        print n



