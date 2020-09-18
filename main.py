import os
from collections import Counter
import keras
from keras.preprocessing.text import Tokenizer
from keras.datasets import reuters
from keras_preprocessing.sequence import pad_sequences
import numpy as np
from sklearn.preprocessing import LabelEncoder
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Embedding, MaxPooling1D, Conv1D, Input, Flatten, GlobalMaxPooling1D
from keras.models import Model

class Utterance:
    def __init__(self, words, label):
        self.label = label
        self.words = words
        self.words_string = ' '.join(words)

    def __repr__(self):
        return 'Utterance(%r, %r)' % (self.label, self.words)


def read_file():
    dialog_acts = open("rand_dialog_acts.dat", "r")
    lines = dialog_acts.readlines()
    labels = []
    utterances = []
    max_words = 0
    for line in lines:
        line = line.lower()
        tokens = line.split()
        label = tokens[0]
        labels.append(label)
        words = tokens[1:len(tokens)]
        max_words = len(words) if len(words) > max_words else max_words
        utterance = Utterance(words, label)
        utterances.append(utterance)
    major_label = Counter(labels).most_common(1)[0][0]
    return utterances, major_label, max_words


def ident_base(utterance):
    words = utterance.words
    words_string = utterance.words_string
    if 'yes' in words:
        return 'affirm'
    if 'postcode' in words:
        return 'request'
    if 'address' in words:
        return 'request'
    if 'phone number' in words_string:
        return 'request'
    if 'what is' in words_string:
        return 'request'
    if 'no' == words[0]:
        return 'negate'
    if len(words) > 2 and (['is', 'it'] == words[0:1]
                           or ['does', 'it'] == words[0:1]
                           or ['is', 'that'] == words[0:1]
                           or ['do', 'they'] == words[0:1]
                           or ['is', 'there'] == words[0:1]):
        return 'confirm'
    if len(words) == 1 and words[0] in {'static', 'noise', 'sil', 'cough', 'breathing', 'blow', 'ring',
                                        'unintelligible', 'um'}:
        return 'null'
    if 'start over' in words_string or 'reset' in words or 'start again' in words_string:
        return 'restart'
    if 'hi' in words or 'hello' in words:
        return 'hello'
    if 'wrong' in words:
        return 'deny'
    if 'thank you' in words_string or 'goodbye' in words:
        return 'thankyou'
    if 'good bye' == words_string or 'goodbye' == words_string:
        return 'bye'
    if len(words) >= 4 and ['is', 'there', 'anything', 'else'] == words[0:3]:
        return 'reqalts'
    if len(words) >= 2 and ['what', 'about'] == words[0:3]:
        return 'reqalts'
    if len(words) == 1 and 'kay' == words[0]:
        return 'ack'
    if 'how about' == words_string:
        return 'null'
    if len(words) > 2 and ['how', 'about'] == words[0:1]:
        return 'reqalts'
    if 'mmhm' in words:
        return 'affirm'
    if 'more' in words:
        return 'reqmore'
    if 'located' in words:
        return 'reqalts'
    return 'inform'


def test(test_utterances):
    print('Testing with', len(test_utterances), 'utterances.\n')
    cnt_corr_base1 = 0
    cnt_corr_base2 = 0
    for utterance in test_utterances:
        base1 = 'inform'
        base2 = ident_base(utterance)
        if utterance.label == base1:
            cnt_corr_base1 += 1
        if utterance.label == base2:
            cnt_corr_base2 += 1
    print('Base 1:', cnt_corr_base1, 'out of', len(test_utterances), 'utterances are correct (' +
          str(cnt_corr_base1 / len(test_utterances)) + ').\n')
    print('Base 2:', cnt_corr_base2, 'out of', len(test_utterances), 'utterances are correct (' +
          str(cnt_corr_base2 / len(test_utterances)) + ').\n')


if __name__ == '__main__':
    utterances, major_label, max_words = read_file()
    train_utterances = utterances[0: int(len(utterances) * 0.85) - 1]
    test_utterances = utterances[int(len(utterances) * 0.85): len(utterances)]

    sents_train = [utterance.words_string for utterance in train_utterances]
    sents_test = [utterance.words_string for utterance in test_utterances]
    labels_test = [utterance.label for utterance in test_utterances]
    labels_train = [utterance.label for utterance in train_utterances]

    # Tokenize our training data
    tokenizer = Tokenizer(num_words=1000, oov_token='<UNK>')
    tokenizer.fit_on_texts(sents_train)
    word_index = tokenizer.word_index

    # Encode data into sequences
    x_train = tokenizer.texts_to_sequences(sents_train)
    x_test = tokenizer.texts_to_sequences(sents_test)

    # Pad the sequences
    x_train = pad_sequences(x_train, padding='post', truncating='post', maxlen=max_words)
    x_test = pad_sequences(x_test, padding='post', truncating='post', maxlen=max_words)

    # Hot-encode labels
    num_classes = 15
    label_encoder = LabelEncoder()
    y_train = label_encoder.fit_transform(labels_train)
    y_test = label_encoder.transform(labels_test)
    y_train = keras.utils.to_categorical(y_train, num_classes)
    y_test = keras.utils.to_categorical(y_test, num_classes)

    embeddings_index = {}
    f = open('glove.6B.100d.txt', encoding="utf8")
    for line in f:
        values = line.split()
        word = values[0]
        coefs = np.asarray(values[1:], dtype='float32')
        embeddings_index[word] = coefs
    f.close()

    embedding_dim = 100

    embedding_matrix = np.zeros((len(word_index) + 1, embedding_dim))
    for word, i in word_index.items():
        embedding_vector = embeddings_index.get(word)
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            embedding_matrix[i] = embedding_vector

    embedding_layer = Embedding(len(word_index) + 1,
                                embedding_dim,
                                weights=[embedding_matrix],
                                input_length=max_words,
                                trainable=False)

    sequence_input = Input(shape=(max_words,), dtype='int64')
    embedded_sequences = embedding_layer(sequence_input)
    x = Conv1D(128, 2, activation='relu', padding='same')(embedded_sequences)
    x = MaxPooling1D(2)(x)
    x = Dropout(0.25)(x)  # To prevent overfitting
    x = Conv1D(128, 2, activation='relu', padding='same')(x)
    x = MaxPooling1D(2)(x)
    x = Dropout(0.25)(x)  # To prevent overfitting
    x = Conv1D(128, 2, activation='relu', padding='same')(x)
    x = GlobalMaxPooling1D()(x)
    x = Flatten()(x)
    x = Dense(128, activation="relu")(x)
    x = Dropout(0.5)(x)  # To prevent overfitting
    preds = Dense(num_classes, activation='softmax')(x)

    model = Model(sequence_input, preds)

    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    history = model.fit(x_train, y_train, batch_size=128, epochs=20, verbose=1, validation_split=0.2)
    score = model.evaluate(x_test, y_test, batch_size=128, verbose=1)
    print('Test loss:', score[0])
    print('Test accuracy:', score[1])

    # test(test_utterances)
