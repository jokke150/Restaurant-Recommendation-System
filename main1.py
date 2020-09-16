import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization
from tensorflow.keras.models import Sequential
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation
import numpy as np

import pandas as pd
import os

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


def baseline1(training_dataframe, testing_dataframe):
    most_frequent = training_dataframe['label'].value_counts().idxmax()
    baseline1 = pd.DataFrame({'label': testing_dataframe['label'].values, 'text': testing_dataframe['text'].values})

    baseline1['match'] = ''

    for index, row in baseline1.iterrows():
        row['match'] = most_frequent

    return (most_frequent, baseline1)


def baseline2Check(text):
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
        row['match'] = baseline2Check(row['text'])

    return baseline2


def logisticRegression(training, testing):
    sentences_train = training['text'].values
    sentences_test = testing['text'].values
    y_train = training['label'].values
    y_test = testing['label'].values

    vectorizer = CountVectorizer()
    vectorizer.fit(sentences_train)

    X_train = vectorizer.transform(sentences_train)
    X_test = vectorizer.transform(sentences_test)

    classifier = LogisticRegression()
    classifier.fit(X_train, y_train)

    score = classifier.score(X_test, y_test)
    print("Accuracy:", score)
    return (classifier, vectorizer)


def neuralnet(training, testing):

    max_words = 5000
    
    sents_train = training['text'].values
    sents_test = testing['text'].values
    labels_test = testing['label'].values
    labels_train = training['label'].values

    print(sents_train[0])

    # Tokenize our training data
    tokenizer = Tokenizer(num_words=1000, oov_token='<UNK>')
    tokenizer.fit_on_texts(sents_train)

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

    model = Sequential()
    model.add(Dense(1024, input_shape=(max_words,)))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(1024))
    model.add(Activation('relu'))
    model.add(Dropout(0.25))
    model.add(Dense(num_classes))
    model.add(Activation('softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    try:
      tf.device("gpu:0")
    except:
      print("not using a gpu")
    
    history = model.fit(x_train, y_train, batch_size=2048, epochs=75, verbose=1, validation_split=0.2)
    score = model.evaluate(x_test, y_test, batch_size=1024, verbose=1)
    print('Test loss:', score[0])
    print('Test accuracy:', score[1])

    return model


def RepresentsInt(s):
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
    training_dataframe, testing_dataframe = generate_dataframe(df)
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

        while not (RepresentsInt(inp)):
            print("Select a number")
            inp = input()

        inp = int(inp)
        if inp == 1:
            most_frequent, baseline1 = baseline1(training_dataframe, testing_dataframe)
            check_labels(baseline1)
            varinp = 1
            while not (varinp == "0"):
                print("return 0 to stop")
                print("Input a utterance")
                varinp = input()
                print(most_frequent)

        elif inp == 2:
            baseline2 = baseline2(testing_dataframe)
            check_labels(baseline2)
            varinp = 1
            while not (varinp == "0"):
                print("return 0 to stop")
                print("Input a utterance")
                varinp = input()
                print(baseline2Check(varinp))

        elif inp == 3:
            model = neuralnet(training_dataframe, testing_dataframe)
            

        elif inp == 4:
            classifier, vectorizer = logisticRegression(training_dataframe, testing_dataframe)
            varinp = 1
            while not (varinp == "0"):
                print("return 0 to stop")
                print("Input a utterance")
                varinp = input()
                i = vectorizer.transform([varinp])
                print(classifier.predict(i))
