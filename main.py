import re
import jieba
import string
import pickle
import streamlit as st
from nltk.tokenize import word_tokenize

# Set Jieba's logging level once to prevent it from logging at each tokenization
jieba.setLogLevel(20)  # Equivalent to logging.INFO

# Compile regex for removing punctuation and digits
additional_punctuation = ['，', '。', '、', '；', '“', '”', '‘', '’', '（', '）', '【', '】', '《', '》', '！', '？', '：', '……', '—']
all_punctuation = f"[{string.punctuation}{''.join(additional_punctuation)}\d]+"
punctuation_and_digits = re.compile(all_punctuation)

def preprocess(text):
    return punctuation_and_digits.sub('', text)

def tokenize_text(text, prediction):
    tokens = text.split()
    english_tokens, chinese_tokens, spanish_tokens = [], [], []

    for token in tokens:
        if '\u4E00' <= token[0] <= '\u9FFF':
            chinese_tokens.extend(jieba.cut(token, cut_all=False))
        elif prediction == 'lang1':
            english_tokens.extend(word_tokenize(token))
        elif prediction == 'lang2':
            spanish_tokens.append(token)

    return english_tokens, chinese_tokens, spanish_tokens

def main():
    st.title('Language Detection System for code-switching texts')
    st.markdown('Supported Languages: English, Spanish, Chinese.')
    text = st.text_area("Enter text to analyze:")
    if st.button('Analyze Text'):
        with open('model_svm', "rb") as f:
            model = pickle.load(f)
        prediction = model.predict([text])[0]
        preprocessed_text = preprocess(text)
        english, chinese, spanish = tokenize_text(preprocessed_text, prediction)
        st.write("English Tokens:", english)
        st.write("Chinese Tokens:", chinese)
        st.write("Spanish Tokens:", spanish)

if __name__ == '__main__':
    main()
