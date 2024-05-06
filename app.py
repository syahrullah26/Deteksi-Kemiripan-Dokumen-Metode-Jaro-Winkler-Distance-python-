import nltk, string, re, math
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
factory = StemmerFactory()
stemmer = factory.create_stemmer()
from nltk.corpus import stopwords
listStopword = set(stopwords.words('indonesian'))
from flask import Flask, render_template, request, session
from flask_mysqldb import MySQL
from nltk.corpus import wordnet as wn
from jaro import jaroWinkler
import textdistance
import json
# import mysql.connector

app = Flask(__name__, 
            )
app.config["SECRET_KEY"] = "kepo"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'skripsi'
app.app_context().push()
mysql = MySQL(app)

@app.route("/")
def index():
    return render_template("main_index.html")

def preprocess(abstrak):
    abstrak = abstrak.lower()
    abstrak = abstrak.translate(str.maketrans("", "", string.punctuation))
    abstrak = re.sub(r"\d+", "", abstrak)
    abstrak = stemmer.stem(abstrak)
    abstrak = ' '.join([x for x in abstrak.split(' ') if x not in listStopword])
    return abstrak

def tokenize(abstrak):
    tokens = nltk.tokenize.word_tokenize(abstrak)
    # tokens2 = [x for x in tokens if x not in listStopword]
    return tokens

def pred_stem(abstrak):
    abstrak = abstrak.lower()
    abstrak = abstrak.translate(str.maketrans("", "", string.punctuation))
    abstrak = re.sub(r"\d+", "", abstrak)
    abstrak = ' '.join([x for x in abstrak.split(' ') if x not in listStopword])
    return abstrak

def tokenize_stem(abstrak):
    tokens = nltk.tokenize.word_tokenize(abstrak)
    # tokens2 = [x for x in tokens if x not in listStopword]
    return tokens

def loaddoc(tokens):
    cur = mysql.connection.cursor()
    cur.execute('''
  SELECT id_abstrak, kal_abs, kal_pred, kal_stem FROM abstrak WHERE id_abstrak IN
(SELECT DISTINCT id_abstrak FROM kata WHERE 
kata.kata IN  ('''
    + ', '.join(['%s'] * len(tokens)) +
    '))', (tokens))
   
    docs = list(cur.fetchall())
    results = []
    for doc in docs:
        results.append({
            'id_abstrak': doc[0],
            'kal_abs': doc[1],
            'kal_pred': doc[2],
            'kal_stem': doc[3]

        })
    return results

def loaddoc_stem(tokens):
    cur = mysql.connection.cursor()
    cur.execute('''
  SELECT id_abstrak, kal_abs, kal_pred, kal_stem FROM abstrak WHERE id_abstrak IN
(SELECT DISTINCT id_abstrak FROM kata WHERE 
kata.kata IN  ('''
    + ', '.join(['%s'] * len(tokens)) +
    '))', (tokens))
   
    docs = list(cur.fetchall())
    results_stem = []
    for doc in docs:
        results_stem.append({
            'id_abstrak': doc[0],
            'kal_abs': doc[1],
            'kal_pred': doc[2],
            'kal_stem': doc[3]

        })
    return results_stem

with open('dict.json', 'r') as json_file:
    syn_data = json.load(json_file)

def get_synonym_list(word):
    if word in syn_data:
        return syn_data[word]['sinonim']
    else:
        return [word]


def get_synonyms(words):
    synonyms = list()
    for word in words:
        synonyms.extend(get_synonym_list(word))
    return synonyms


def getscore(doks, abstrak, lenquery):
    scores = {}
    abstrak_str = ' '.join(abstrak)
    for dok in doks:
        scores[dok['id_abstrak']] =  jaroWinkler(abstrak_str, dok['kal_pred'],lenquery)
    return scores

def getscore_stem(doks, abstrak, lenquery):
    scores_stem = {}
    abstrak_str = ' '.join(abstrak)
    for dok in doks:
        scores_stem[dok['id_abstrak']] =  jaroWinkler(abstrak_str, dok['kal_stem'],lenquery)
    return scores_stem


def loaddocuments(docids, scores):
    cur = mysql.connection.cursor()
    cur.execute('''
    SELECT id_abstrak, kal_abs, kal_pred 
    FROM abstrak WHERE id_abstrak IN (''' 
    + ', '.join(['%s'] * len(docids)) +
    ''')''', tuple(docids))
    results = []
    docs = list(cur.fetchall())
    for docid in docids:
        for doc in docs:
            if docid == doc[0]:
                results.append({
                    'id_abstrak': doc[0],
                    'kal_abs': doc[1],
                    'kal_pred': doc[2],
                    'score': scores[docid]
                })
                break
    hasil_similarity = len(results)
    print("Hasil Similarity", hasil_similarity)
    return results

def loaddocuments_stem(docids, scores_stem):
    cur = mysql.connection.cursor()
    cur.execute('''
    SELECT id_abstrak, kal_abs, kal_pred, kal_stem
    FROM abstrak WHERE id_abstrak IN (''' 
    + ', '.join(['%s'] * len(docids)) +
    ''')''', tuple(docids))
    results_stem = []
    docs = list(cur.fetchall())
    for docid in docids:
        for doc in docs:
            if docid == doc[0]:
                results_stem.append({
                    'id_abstrak': doc[0],
                    'kal_abs': doc[1],
                    'kal_pred': doc[2],
                    'kal_stem': doc[3],
                    'score': scores_stem[docid]
                })
                break
    hasil_similarity = len(results_stem)
    print("Hasil Similarity tanpa stemming", hasil_similarity)
    return results_stem

#tanpa Synonym
@app.route("/result")
def result():
    abstrak = (request.args['query'])
    lenquery=len(tokenize(preprocess(abstrak)))
    abstrakpred = (tokenize(preprocess(abstrak)))
    doks = loaddoc(abstrakpred)
    scores = getscore(doks, abstrakpred, lenquery)
    docids = sorted(scores, key=scores.get, reverse=True)
    results = loaddocuments(docids, scores) if len(docids) > 0 else []
    return render_template("result.html", takok = abstrak, results = results )

def result_api(abstrak):
    tkn = tokenize(preprocess(abstrak))
    lenquery=len(tkn)
    abstrakpred = tkn
    doks = loaddoc(abstrakpred)
    scores = getscore(doks, abstrakpred, lenquery)
    docids = sorted(scores, key=scores.get, reverse=True)
    results = loaddocuments(docids, scores) if len(docids) > 0 else []
    return results

def resultsynonym_api(abstrak):
    tkn = tokenize(preprocess(abstrak))
    lenquery=len(tkn)
    abstrakpred = get_synonyms(tkn)
    doks = loaddoc(abstrakpred)
    scores = getscore(doks, abstrakpred, lenquery)
    docids = sorted(scores, key=scores.get, reverse=True)
    results = loaddocuments(docids, scores) if len(docids) > 0 else []
    return results

def resultstem_api(abstrak):
    tkn =tokenize_stem(pred_stem(abstrak))
    lenquery=len(tkn)
    abstrakpred = tkn
    doks = loaddoc_stem(abstrakpred)
    scores = getscore_stem(doks, abstrakpred, lenquery)
    docids = sorted(scores, key=scores.get, reverse=True)
    results = loaddocuments(docids, scores) if len(docids) > 0 else []
    return results

#Menggunakan Synonym
@app.route("/resultsynonym")
def resultsynonym():
    abstrak = (request.args['query'])
    lenquery=len(tokenize(preprocess(abstrak)))
    abstrakpred = get_synonyms(tokenize(preprocess(abstrak)))
    doks = loaddoc(abstrakpred)
    scores = getscore(doks, abstrakpred, lenquery)
    docids = sorted(scores, key=scores.get, reverse=True)
    results = loaddocuments(docids, scores) if len(docids) > 0 else []
    return render_template("result.html", takok = abstrak, results = results )

# tanpa stemming
@app.route("/resultstem")
def resultstem():
    abstrak = (request.args['query'])
    lenquery=len(tokenize_stem(pred_stem(abstrak)))
    abstrakpred = (tokenize_stem(pred_stem(abstrak)))
    doks = loaddoc_stem(abstrakpred)
    scores = getscore_stem(doks, abstrakpred, lenquery)
    docids = sorted(scores, key=scores.get, reverse=True)
    results = loaddocuments(docids, scores) if len(docids) > 0 else []
    return render_template("result.html", takok = abstrak, results = results )

# app.run(debug=True)