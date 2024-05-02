import pickle
import streamlit as st

# loading svm model en format pkl
with open('model_svm', "rb") as f:
    model = pickle.load(f)

def prediction(text):
    text = ['jaja', 'i']
    test_prediction = model.predict(text)
    print(test_prediction)
    print('text')
    return test_prediction
