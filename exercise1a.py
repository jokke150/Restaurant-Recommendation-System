import pickle

from scipy.odr import Model
from tensorflow import keras
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from keras.layers import Dense, Dropout, Embedding, MaxPooling1D, Conv1D, Input, Flatten, GlobalMaxPooling1D
from keras.models import Model
import numpy as np
import pandas as pd

def read_file():
    df = pd.read_csv("rand_dialog_acts.dat",
                     names=['all_words'])
    return df

def generate_dataframe(df):
    dialog_acts = []
    text = []

    for index, row in df.iterrows():
        (fword, rest) = row['all_words'].split(maxsplit=1)
        dialog_acts.append(fword)
        text.append(rest)

    train_dialog_acts = dialog_acts[0: int(len(dialog_acts) * 0.85) - 1]
    test_dialog_acts = dialog_acts[int(len(dialog_acts) * 0.85): len(dialog_acts)]

    train_text = text[0: int(len(text) * 0.85) - 1]
    test_text = text[int(len(text) * 0.85): len(text)]

    return (pd.DataFrame({'label': train_dialog_acts, 'text': train_text}),
            pd.DataFrame({'label': test_dialog_acts, 'text': test_text}))


def baseline1(train_df, test_df):
    most_frequent = train_df['label'].value_counts().idxmax()
    baseline1 = pd.DataFrame({'label': test_df['label'].values, 'text': test_df['text'].values})

    baseline1['match'] = ''

    for index, row in baseline1.iterrows():
        row['match'] = most_frequent

    return (most_frequent, baseline1)


def baseline2_check(text):
    if "yes" in text:
        return "affirm"
    elif "postcode" in text:
        return "request"
    elif "address" in text:
        return "request"
    elif "phone number" in text:
        return "request"
    elif "what is" in text:
        return "request"
    elif text.startswith("no"):
        return "negate"
    elif text.startswith("is it") or text.startswith("does it") or text.startswith("is that") or \
            text.startswith("do they") or text.startswith("is there"):
        return "confirm"
    elif text == "static" or text == "noise" or text == "sil" or text == "cough" or text == "um" \
            or text == "breathing" or text == "blow" or text == "ring" or text == "unintelligible":
        return "null"
    elif "start over" in text:
        return "restart"
    elif "reset" in text:
        return "restart"
    elif "start again" in text:
        return "restart"
    elif "back" in text:
        return "repeat"
    elif "hi" in text:
        return "hello"
    elif "hello" in text:
        return "hello"
    elif "wrong" in text:
        return "deny"
    elif "thank you" in text:
        return "thankyou"
    elif "goodbye" in text and not text.startswith("goodbye"):
        return "thankyou"
    elif text == "Good bye":
        return "bye"
    elif text == "goodbye":
        return "bye"
    elif text.startswith("is there anything else"):
        return "reqalts"
    elif text.startswith("what about"):
        return "reqalts"
    elif text == "kay":
        return "ack"
    elif text == "how about":
        return "null"
    elif text.startswith("how about"):
        return "reqalts"
    elif "mmhm" in text:
        return "affirm"
    elif "more" in text:
        return "reqmore"
    elif "located" in text:
        return "reqalts"
    else:
        return "inform"


def baseline2(dataframe):
    baseline2 = pd.DataFrame({'label': dataframe['label'].values, 'text': dataframe['text'].values})
    baseline2['match'] = ''

    for index, row in baseline2.iterrows():
        row['match'] = baseline2_check(row['text'])

    return baseline2


def logistic_regression(x_train, x_test, y_test, y_train):
    vectorizer = CountVectorizer()
    vectorizer.fit(x_train)

    x_train = vectorizer.transform(x_train)
    x_test = vectorizer.transform(x_test)

    classifier = LogisticRegression()
    classifier.fit(x_train, y_train)

    score = classifier.score(x_test, y_test)
    print("Accuracy:", score)
    return (classifier, vectorizer)


def neural_net(x_train, x_test, y_test, y_train):
    max_words = 100
    num_words = 1000

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

    # Model definition
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

    model.fit(x_train, y_train, batch_size=128, epochs=20, verbose=1, validation_split=0.2)

    score = model.evaluate(x_test, y_test, batch_size=128, verbose=1)
    print('Test loss:', score[0])
    print('Test accuracy:', score[1])

    # save tokenizer for use in next exercise
    outfile = open('tokenizer.pickle', 'wb')
    pickle.dump(tokenizer, outfile)
    outfile.close()

    # save model for use in next exercise
    model.save('speech_act_model.h5')

    # save label encoder for use in next exercise
    outfile = open('label_encoder.pickle','wb')
    pickle.dump(label_encoder, outfile)
    outfile.close()

    return model


def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def check_labels(baseline):
    correctlabels = 0
    labels = 0
    for index, row in baseline.iterrows():
        if row['label'] == row['match']:
            correctlabels = correctlabels + 1
        labels = labels + 1
    print("Correct Labels:", correctlabels, "/ Labels:", labels)
    print("Score:", 100 * correctlabels / labels)


if __name__ == '__main__':

    df = read_file()
    train_df, test_df = generate_dataframe(df)

    x_train = train_df['text'].values
    x_test = test_df['text'].values
    y_test = test_df['label'].values
    y_train = train_df['label'].values

    print(x_train)

    inp = 1
    varinp = 1
    while not (inp == 0):

        print("0: exit")
        print("1: baseline1")
        print("2: baseline2")
        print("3: machine learning")
        print("4: Logistic Regression")
        print("Input a number for selection")
        inp = input()

        while not (represents_int(inp)):
            print("Select a number")
            inp = input()

        inp = int(inp)
        if inp == 1:
            most_frequent, baseline1 = baseline1(train_df, test_df)
            check_labels(baseline1)
            varinp = 1
            while not (varinp == "0"):
                print("return 0 to stop")
                print("Input an utterance")
                varinp = input()
                print(most_frequent)

        elif inp == 2:
            baseline2 = baseline2(test_df)
            check_labels(baseline2)
            varinp = 1
            while not (varinp == "0"):
                print("return 0 to stop")
                print("Input an utterance")
                varinp = input()
                print(baseline2_check(varinp))

        elif inp == 3:
            model = neural_net(x_train, x_test, y_test, y_train)
            

        elif inp == 4:
            classifier, vectorizer = logistic_regression(x_train, x_test, y_test, y_train)
            varinp = 1
            while not (varinp == "0"):
                print("return 0 to stop")
                print("Input an utterance")
                varinp = input()
                i = vectorizer.transform([varinp])
                print(classifier.predict(i))
