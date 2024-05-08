import re
import jieba
import string
import pickle
import streamlit as st
from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt', quiet=True)

jieba.setLogLevel(20)  # Set logging level for Jieba

# Define punctuation including Chinese punctuation explicitly
additional_punctuation = ['，', '。', '、', '；', '“', '”', '‘', '’', '（', '）', '【', '】', '《', '》', '！', '？', '：', '……', '—']
all_punctuation = f"[{string.punctuation}{''.join(additional_punctuation)}\d]+"
punctuation_and_digits = re.compile(all_punctuation)

def smart_tokenize(text):
    """ Tokenize text while managing transitions between Chinese and Roman characters and further splitting on whitespace """
    tokens = []
    buffer = ''
    is_chinese = lambda char: '\u4E00' <= char <= '\u9FFF'

    for char in text:
        if buffer and ((is_chinese(char) and not is_chinese(buffer[-1])) or (not is_chinese(char) and is_chinese(buffer[-1])) or punctuation_and_digits.match(char)):
            if not punctuation_and_digits.match(buffer):
                # Process buffer based on language
                if '\u4E00' <= buffer[0] <= '\u9FFF':
                    tokens.extend(jieba.cut(buffer, cut_all=False))  # Use jieba for Chinese
                else:
                    tokens.extend(word_tokenize(buffer))  # Use nltk for non-Chinese
            else:
                tokens.append(buffer)
            buffer = ''
        buffer += char
    if buffer:
        # Final flush of the buffer after loop
        if '\u4E00' <= buffer[0] <= '\u9FFF':
            tokens.extend(jieba.cut(buffer, cut_all=False))
        else:
            tokens.extend(word_tokenize(buffer))
    return tokens

def classify_tokens(tokens, model):
    english_tokens, spanish_tokens, chinese_tokens, other_tokens, punctuations = [], [], [], [], []
    for token in tokens:
        if punctuation_and_digits.match(token):
            punctuations.append(token)
        elif '\u4E00' <= token[0] <= '\u9FFF':
            chinese_tokens.append(token)
        else:
            prediction = model.predict([token])[0]
            # ajout pour i et I car le detecteur ne fonctionne pas sur cela
            if prediction == 'lang1' or token == "i" or token == 'I':
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
    st.text("Try: Puedes enseñarme cómo decir thank you en 中文? I want to use it.")
    st.text("Try: I was thinking 我们可以去那个新的 Spanish restaurant este fin de semana")

    if st.button('Analyze Text'):
        try:
            with open('model_svm.pkl', "rb") as f:
                model = pickle.load(f)
        except Exception as e:
            st.error(f"Failed to load model: {e}")
            return
        
        tokens = smart_tokenize(text)
        english, spanish, chinese, other, punctuations = classify_tokens(tokens, model)

        if text:
            st.write("English Tokens:", english)
            st.write("Spanish Tokens:", spanish)
            st.write("Chinese Tokens:", chinese)
            st.write("Unsupported Language's Tokens:", other)
            st.write("Punctuations:", punctuations)
        else:
            st.error("Please enter a valid text.")

if __name__ == '__main__':
    main()
