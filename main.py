import re
import jieba
import string
import pickle
import streamlit as st
from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt', quiet=True)
import os
os.environ['DYLD_LIBRARY_PATH'] = '/opt/homebrew/Cellar/enchant/2.7.3/lib'
import enchant

english_dict = enchant.Dict("en_US")
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

def extract_features(tokens):
    return [{'word': token, 'prev_word': tokens[i - 1] if i > 0 else '', 'next_word': tokens[i + 1] if i < len(tokens) - 1 else '', 'is_english': english_dict.check(token), 'word_length': len(token), 'is_upper': token[0].isupper()} for i, token in enumerate(tokens)]


def classify_tokens(tokens, model):
    features = extract_features(tokens)
    predictions = model.predict([features])[0]
    categorized_tokens = {'english': [], 'spanish': [], 'chinese': [], 'other': [], 'punctuations': []}
    for token, prediction in zip(tokens, predictions):
        if punctuation_and_digits.match(token):
            categorized_tokens['punctuations'].append(token)
        elif '\u4E00' <= token[0] <= '\u9FFF':
            categorized_tokens['chinese'].append(token)
        elif prediction == 'lang1':
            categorized_tokens['english'].append(token)
        elif prediction == 'lang2':
            categorized_tokens['spanish'].append(token)
        else:
            categorized_tokens['other'].append(token)
    return categorized_tokens

def main():
    st.title('Language Detection System for Code-Switched Texts')
    st.markdown('Supported Languages: English, Spanish, Chinese.')
    text = st.text_area("Please enter a text:", height=150)
    st.markdown('Try these examples:')
    st.text("We should catch up soon lol, Tal vez podemos hablar over coffee y 聊聊天.")
    st.text('Hey bro, what did you think about el último episodio de that我们都喜欢的show?')
    st.text('Jajaja, I just尝试to make paella for the first time 😍')
    st.text("Puedes teach me cómo decir thank you en中文?")

    if st.button('Analyze Text'):
        if len(text) > 1:
            with open('model_crf.pkl', "rb") as f:
                model = pickle.load(f)
                tokens = smart_tokenize(text)
                categorized_tokens = classify_tokens(tokens, model)
        if len(text) == 1:
            with open('model_svm.pkl', "rb") as f:
                model = pickle.load(f)
                tokens = smart_tokenize(text)
                categorized_tokens = classify_tokens(tokens, model)

        if categorized_tokens:
            st.json({
                "English Tokens": {idx: token for idx, token in enumerate(categorized_tokens['english'])},
                "Spanish Tokens": {idx: token for idx, token in enumerate(categorized_tokens['spanish'])},
                "Chinese Tokens": {idx: token for idx, token in enumerate(categorized_tokens['chinese'])},
                "Unsupported Language's Tokens": {idx: token for idx, token in enumerate(categorized_tokens['other'])},
                "Punctuations": {idx: token for idx, token in enumerate(categorized_tokens['punctuations'])}
            })
    else:
        st.error("Please enter a valid text.")

if __name__ == '__main__':
    main()