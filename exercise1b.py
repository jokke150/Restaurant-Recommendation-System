import pickle

import numpy as np
from tensorflow.python.keras.preprocessing.sequence import pad_sequences

from learners.neural_net import load_neural_net


def ident_speech_act(tokenizer, model, label_encoder, text):
    max_words = 100

    x_test = tokenizer.texts_to_sequences([text])

    # Pad the sequences
    x_test = pad_sequences(x_test, padding='post', truncating='post', maxlen=max_words)

    prediction = np.argmax(model.predict(x_test), axis=1)
    return label_encoder.inverse_transform(prediction)[0]


if __name__ == '__main__':
    tokenizer, model, label_encoder = load_neural_net()

    # how to predict:
    speech_act = ident_speech_act(tokenizer, model, label_encoder, 'hindi food is okay')
    print(speech_act)


