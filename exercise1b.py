import pickle

import numpy as np
from tensorflow import keras
from keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.python.keras.preprocessing.sequence import pad_sequences


def ident_speech_act(tokenizer, model, label_encoder, text):
    max_words = 100

    x_test = tokenizer.texts_to_sequences([text])

    # Pad the sequences
    x_test = pad_sequences(x_test, padding='post', truncating='post', maxlen=max_words)

    prediction = np.argmax(model.predict(x_test), axis=1)
    return label_encoder.inverse_transform(prediction)[0]


if __name__ == '__main__':
    # load tokenizer
    infile = open('data/tokenizer.pickle', 'rb')
    tokenizer = pickle.load(infile)
    infile.close()

    # load model
    model = load_model('data/speech_act_model.h5')

    # load label encoder
    infile = open('data/label_encoder.pickle', 'rb')
    label_encoder = pickle.load(infile)
    infile.close()

    # how to predict:
    speech_act = ident_speech_act(tokenizer, model, label_encoder, 'hindi food is okay')
    print(speech_act)


