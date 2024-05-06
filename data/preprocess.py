import string
import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist

stemmer = StemmerFactory().create_stemmer()
stopword_list = set(stopwords.words('indonesian'))

def preprocess(kalimat: str) -> str:
    kalimat = kalimat.lower()
    # menghilangkan tanda baca
    kalimat = kalimat.translate(str.maketrans("", "", string.punctuation))
    kalimat = re.sub(r"\d+", "", kalimat)
    kalimat = stemmer.stem(kalimat)
    abstrak = ' '.join([x for x in abstrak.split(' ') if x not in stopword_list])
    return kalimat
    # tokens = word_tokenize(kalimat)
    # tokens = [x for x in tokens not in stopword_list]
    # return dict(FreqDist(tokens))

def pred_stem(kalimat: str) -> str:
    kalimat = kalimat.lower()
    # menghilangkan tanda baca
    kalimat = kalimat.translate(str.maketrans("", "", string.punctuation))
    kalimat = re.sub(r"\d+", "", kalimat)
    # kalimat = stemmer.stem(kalimat)
    return kalimat
    # tokens = word_tokenize(kalimat)
    # tokens = [x for x in tokens not in stopword_list]
    # return dict(FreqDist(tokens))

def tokenize(kalimat: str) -> set[str]:
    tokens = word_tokenize(kalimat)
    uniq_tokens = set()
    for x in tokens:
        if x not in stopword_list:
            uniq_tokens.add(x)
    return uniq_tokens
