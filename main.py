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
additional_punctuation = ['，', '。', '、', '；', '“', '”', '‘', '’', '（', '）', '【', '】', '《', '》', '！', '？', '：', '……', '—', '¿']
all_punctuation = f"[{string.punctuation}{''.join(additional_punctuation)}\d]+"
punctuation_and_digits = re.compile(all_punctuation)

def smart_tokenize(text):
    """Tokenize text using jieba for Chinese characters and nltk for Roman characters, handling an extended set of punctuation."""
    tokens = []
    buffer = ''
    chinese_buffer = ''
    is_chinese = lambda char: '\u4E00' <= char <= '\u9FFF'

    for char in text:
        if is_chinese(char):
            if buffer:
                # Tokenize the non-Chinese buffer with nltk before flushing
                tokens.extend(word_tokenize(buffer))
                buffer = ''
            # Accumulate Chinese characters
            chinese_buffer += char
        elif punctuation_and_digits.match(char):
            if chinese_buffer:
                # Tokenize the Chinese buffer with jieba before flushing
                tokens.extend(jieba.cut(chinese_buffer, cut_all=False))
                chinese_buffer = ''
            if buffer:
                # Tokenize the non-Chinese buffer with nltk before flushing
                tokens.extend(word_tokenize(buffer))
                buffer = ''
            # Treat punctuation as separate tokens
            tokens.append(char)
        else:
            if chinese_buffer:
                # Tokenize the Chinese buffer with jieba before flushing
                tokens.extend(jieba.cut(chinese_buffer, cut_all=False))
                chinese_buffer = ''
            # Accumulate Roman characters and other symbols in the buffer
            buffer += char

    # Flush remaining buffers
    if chinese_buffer:
        tokens.extend(jieba.cut(chinese_buffer, cut_all=False))
    if buffer:
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
    st.title('Language Detection System for code-switched texts')
    st.markdown('Supported Languages: English, Spanish, Chinese.')
    text = st.text_area("Please enter a text:")
    st.markdown('Try:')
    st.text("We should catch up soon lol, Tal vez podemos hablar over coffee y 聊聊天. ")
    st.text('hey bro, what did you think about el último episodio de that我们都喜欢的show?')
    st.text('jajaja, I just尝试to make paella for the first time 😍')
    st.text("Puedes teach me cómo decir thank you en中文¿")

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