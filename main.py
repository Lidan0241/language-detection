import re
import jieba
import string
import logging
import streamlit as st
from translate import Translator
from nltk.tokenize import word_tokenize
'''
http://10.139.4.72:8502
'''

# Set Jieba's logging level once to prevent it from logging at each tokenization
jieba.setLogLevel(logging.INFO)

# Compile regex for removing punctuation and digits
additional_punctuation = ['，', '。', '、', '；', '“', '”', '‘', '’', '（', '）', '【', '】', '《', '》', '！', '？', '：', '……', '—']
all_punctuation = f"[{string.punctuation}{''.join(additional_punctuation)}\d]+"
punctuation_and_digits = re.compile(all_punctuation)


def preprocess(text):
    return punctuation_and_digits.sub('', text)

def is_en(token):
    return all('\u0000' <= char <= '\u007F' for char in token)

def is_zh(token):
    return any('\u4E00' <= char <= '\u9FFF' for char in token)

def is_es(token):
    spanish_chars = "àâéèêëîïôöûüç"
    return any(char in spanish_chars for char in token)

def tokenize_text(text):
    tokens = text.split()
    english_tokens, chinese_tokens, spanish_tokens = [], [], []

    for token in tokens:
        if is_zh(token):
            chinese_tokens.extend(jieba.cut(token, cut_all=False))
        elif is_en(token):
            english_tokens.extend(word_tokenize(token))
        elif is_es(token):
            spanish_tokens.append(token)  # Use simple append for spanish, no need for `word_tokenize` here

    return english_tokens, chinese_tokens, spanish_tokens

def main():
    st.title('Language Detection System')
    st.markdown('Compatible for English, Spanish and Chinese texts.')
    text = st.text_area("Enter text to analyze:")
    if st.button('Analyze Text'):
        preprocessed_text = preprocess(text)
        english, chinese, french = tokenize_text(preprocessed_text)
        st.write("English Tokens:", english)
        st.write("Chinese Tokens:", chinese)
        st.write("French Tokens:", french)

if __name__ == '__main__':
    main()

