import mysql.connector
import csv
import re
from preprocess import tokenize
from preprocess import preprocess
from preprocess import pred_stem
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.feature_extraction.text import TfidfTransformer

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="skripsi",
    ssl_disabled=True
)

mycursor = mydb.cursor()
mycursor.execute("TRUNCATE abstrak;")
mycursor.execute("TRUNCATE kata;")
with open('Abstrak.csv', 'r', encoding='utf8') as i:
    reader = csv.reader(i)
    next(reader, None) # skip header
    corpus = []
    for i, line in enumerate(reader):
        ABSTRAK = line[1]
        ABSTRAK_PRED = preprocess(ABSTRAK)
        ABSTRAK_STEM = pred_stem(ABSTRAK)
        corpus.append(ABSTRAK_PRED)
        mycursor.execute(
            "INSERT INTO abstrak (id_abstrak, kal_abs, kal_pred, kal_stem) VALUES (%s, %s, %s, %s)",
            (i + 1, ABSTRAK, ABSTRAK_PRED, ABSTRAK_STEM))
    word_id_map = {}
    for i, text in enumerate(corpus):
        words = tokenize(text)
        for word in words:
            sql = "INSERT INTO kata VALUES (%s, %s)"
            mycursor.execute(sql, [i + 1, word])
    mydb.commit()
