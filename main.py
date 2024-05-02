import re
import jieba
import string
import pickle
import streamlit as st
from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt', quiet=True)

jieba.setLogLevel(20)  # Set logging level for Jieba

# Define punctuation
additional_punctuation = ['，', '。', '、', '；', '“', '”', '‘', '’', '（', '）', '【', '】', '《', '》', '！', '？', '：', '……', '—', '，']
all_punctuation = f"[{string.punctuation}{''.join(additional_punctuation)}\d]+"
punctuation_and_digits = re.compile(all_punctuation)

def tokenize_text(text):
    return word_tokenize(text)

def tokenize_chinese(text):
    return list(jieba.cut(text, cut_all=False))

def classify_tokens(tokens, model):
    english_tokens, spanish_tokens, chinese_tokens, other_tokens, punctuations = [], [], [], [], []
    for token in tokens:
        if punctuation_and_digits.match(token):
            punctuations.append(token)
        elif '\u4E00' <= token[0] <= '\u9FFF':
            chinese_tokens.extend(tokenize_chinese(token))
        else:
            prediction = model.predict([token])[0]
            if prediction == 'lang1':
                english_tokens.append(token)
            elif prediction == 'lang2':
                spanish_tokens.append(token)
            else:
                other_tokens.append(token)

    return english_tokens, spanish_tokens, chinese_tokens, other_tokens, punctuations

def main():
    st.title('Language Detection System for code-switching texts')
    st.markdown('Supported Languages: English, Spanish, Chinese.')
    text = st.text_area("Please enter a text:")

    if st.button('Analyze Text'):
        try:
            with open('model_svm.pkl', "rb") as f:
                model = pickle.load(f)
        except Exception as e:
            st.error(f"Failed to load model: {e}")
            return
        
        tokens = tokenize_text(text)
        english, spanish, chinese, other, punctuations = classify_tokens(tokens, model)

        if text:
            st.write("English Tokens:", english)
            st.write("Spanish Tokens:", spanish)
            st.write("Chinese Tokens:", chinese)
            st.write("Unsupported Language's Tokens", other)
            st.write("Punctuations:", punctuations)
        else:
            st.error("Please enter a valid text.")

if __name__ == '__main__':
    main()
