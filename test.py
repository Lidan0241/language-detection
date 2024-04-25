# Lancement du script: python3 test.py
import re
import jieba
import string
import logging
from translate import Translator
from nltk.tokenize import word_tokenize


text = "Hello 世界, this is a test 文本. 三菱电机总额高达3000万元。Je vais au cinéma À"

def preprocess(text):
    additional_punctuation = ['，', '。', '、', '；', '“', '”', '‘', '’', '（', '）', '【', '】', '《', '》', '！', '？', '：', '……', '—']
    all_punctuation = ''.join(list(string.punctuation) + additional_punctuation + list(string.digits))
    preprocessed_text = text.translate(str.maketrans('', '', all_punctuation))
    remplacement=\
    {'À':'à','Á':'á','Â':'â','Ä':'ä','Ã':'ã','Å':'å',
     'È':'è','É':'é','Ê':'ê','Ë':'ë',
     'Ì':'ì','Í':'í','Î':'î','Ï':'ï',
     'Ò':'ò','Ó':'ó','Ô':'ô','Ö':'ö','Õ':'õ','Ø':'ø',
     'Ù':'ù','Ú':'ú','Û':'û','Ü':'ü',
     'Ç':'ç','Œ':'œ','Æ':'æ','Ñ':'ñ'}
    for lettre in remplacement:
        preprocessed_text = preprocessed_text.replace(lettre,remplacement[lettre])
    return preprocessed_text

def is_en(token):
    return all('\u0000' <= char <= '\u007F' for char in token)

def is_zh(token):
    return any('\u4E00' <= char <= '\u9FFF' for char in token)

def is_fr(token):
    french_chars = "àâéèêëîïôöûüç"
    return any(char in french_chars for char in token)

def tokenize_text(text):
    tokens = preprocessed_text.split()
    english_tokens, chinese_tokens, french_tokens = [], [], []

    for token in tokens:
        if is_zh(token):
            jieba.setLogLevel(logging.INFO) # enlever rechargement jieba
            chinese_tokens.extend(jieba.cut(token, cut_all=False))
        elif is_en(token):
            english_tokens.extend(word_tokenize(token))
        elif is_fr(token):
            french_tokens.append(word_tokenize(token))

    return english_tokens, chinese_tokens, french_tokens

preprocessed_text = preprocess(text)
english, chinese, french = tokenize_text(preprocessed_text)

print("Preprocessed Text:", preprocessed_text)
print("English Tokens:", english)
print("Chinese Tokens:", chinese)
print("French Tokens:", french)
