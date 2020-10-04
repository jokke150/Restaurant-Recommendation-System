import os

# Disable TF debug logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import pickle
from sklearn.utils import class_weight
from scipy.odr import Model
from tensorflow import keras
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from keras.layers import Dense, Dropout, Embedding, MaxPooling1D, Conv1D, Input, Flatten, GlobalMaxPooling1D
from keras.models import Model
from kerastuner.tuners import Hyperband
import numpy as np
from tensorflow.python.keras.models import load_model
from kerastuner import HyperModel

max_words = 100
num_words = 1000

HYPERBAND_MAX_EPOCHS = 40
MAX_TRIALS = 20
EXECUTION_PER_TRIAL = 2
SEED = 1


def train_nn(x_train, x_test, y_test, y_train):
    # Add class weights to deal with unbalanced distribution of labels
    class_weights = class_weight.compute_class_weight('balanced',
                                                      np.unique(y_train),
                                                      y_train)

    dictionary_weights = dict(enumerate(class_weights))

    # Tokenize our training data
    tokenizer = Tokenizer(num_words=num_words, oov_token='<UNK>')
    tokenizer.fit_on_texts(x_train)
    word_index = tokenizer.word_index

    # Encode data into sequences
    x_train = tokenizer.texts_to_sequences(x_train)
    x_test = tokenizer.texts_to_sequences(x_test)

    # Pad the sequences
    x_train = pad_sequences(x_train, padding='post', truncating='post', maxlen=max_words)
    x_test = pad_sequences(x_test, padding='post', truncating='post', maxlen=max_words)

    # Hot-encode labels
    num_classes = 15
    label_encoder = LabelEncoder()
    y_train = label_encoder.fit_transform(y_train)
    y_test = label_encoder.transform(y_test)
    y_train = keras.utils.to_categorical(y_train, num_classes)
    y_test = keras.utils.to_categorical(y_test, num_classes)

    # prepare GloVe embeddings
    embeddings_index = {}
    f = open(os.path.dirname(__file__) + '/../data/glove.6B.100d.txt', encoding="utf8")
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

    model = MyHyperModel(embedding_layer, max_words=max_words, num_classes=num_classes)
    tuner = Hyperband(
        model,
        max_epochs=HYPERBAND_MAX_EPOCHS,
        objective='val_accuracy',
        seed=SEED,
        executions_per_trial=EXECUTION_PER_TRIAL,
        directory='learners',
        project_name="MethodsAI",

    )

    tuner.search(x_train, y_train, epochs=20, validation_split=0.1)

    bestmodel = tuner.get_best_models(num_models=1)[0]

    score = bestmodel.evaluate(x_test, y_test, batch_size=128, verbose=1)
    print('Test loss:', score[0])
    print('Test accuracy:', score[1])

    return tokenizer, bestmodel, label_encoder


def save_nn(tokenizer, model, label_encoder):
    # save tokenizer for use in next exercise
    outfile = open(os.path.dirname(__file__) + '/../data/tokenizer.pickle', 'wb')
    pickle.dump(tokenizer, outfile)
    outfile.close()

    # save model for use in next exercise
    model.save(os.path.dirname(__file__) + '/../data/speech_act_model.h5')

    # save label encoder for use in next exercise
    outfile = open(os.path.dirname(__file__) + '/../data/label_encoder.pickle', 'wb')
    pickle.dump(label_encoder, outfile)
    outfile.close()


def load_nn():
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

    return tokenizer, model, label_encoder


def predict_nn(text, tokenizer, model, label_encoder):
    x_test = tokenizer.texts_to_sequences([text])

    # Pad the sequences
    x_test = pad_sequences(x_test, padding='post', truncating='post', maxlen=max_words)

    prediction = np.argmax(model.predict(x_test), axis=1)
    return label_encoder.inverse_transform(prediction)[0]


class MyHyperModel(HyperModel):
    def __init__(self, embedding_layer, num_classes, max_words):
        self.num_classes = num_classes
        self.embedding_layer = embedding_layer
        self.max_words = max_words

    def build(self, hp):
        # Model definition
        sequence_input = Input(shape=(self.max_words,), dtype='int64')
        embedded_sequences = self.embedding_layer(sequence_input)
        x = Conv1D(128, 2, activation='relu', padding='same')(embedded_sequences)
        x = MaxPooling1D(2)(x)
        x = Dropout(rate=hp.Float(
            'dropout_1',
            min_value=0.0,
            max_value=0.5,
            default=0.25,
            step=0.05,
        ))(x)  # To prevent overfitting
        x = Conv1D(128, 2, activation='relu', padding='same')(x)
        x = MaxPooling1D(2)(x)
        x = Dropout(rate=hp.Float(
            'dropout_2',
            min_value=0.0,
            max_value=0.5,
            default=0.25,
            step=0.05,
        ))(x)  # To prevent overfitting
        x = Conv1D(filters=hp.Choice(
            'num_filters',
            values=[32, 64],
            default=64,
        ), activation='relu', padding='same', kernel_size=2)(x)
        x = GlobalMaxPooling1D()(x)
        x = Flatten()(x)
        x = Dense(units=hp.Int(
            'units',
            min_value=32,
            max_value=512,
            step=32,
            default=128
        ),
            activation=hp.Choice(
                'dense_activation',
                values=['relu', 'tanh', 'sigmoid'],
                default='relu'
            ))(x)
        x = Dropout(rate=hp.Float(
            'dropout_3',
            min_value=0.0,
            max_value=0.5,
            default=0.25,
            step=0.05
        ))(x)  # To prevent overfitting
        preds = Dense(self.num_classes, activation='softmax')(x)
        model = Model(sequence_input, preds)
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        return model
