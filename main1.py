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

import numpy as np

import pandas as pd
import os

labels = ['ack', 'affirm', 'bye', 'confirm', 'deny', 'hello', 'inform', 'negate', 'null', 'repeat', 'reqalts',
          'reqmore', 'request', 'restart', 'thankyou']


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


def ConvertLabeltoNumber(label):
    return labels.index(label)


def ConvertNumbertoLabel(number):
    return labels[number]


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


def machinelearning1(training, testing):
    traininglabel = pd.DataFrame({'label': training['label'].values})
    for index, row in traininglabel.iterrows():
        row['label'] = ConvertLabeltoNumber(row['label'])

    testinglabel = pd.DataFrame({'label': testing['label'].values})
    for index, row in testinglabel.iterrows():
        row['label'] = ConvertLabeltoNumber(row['label'])

    sentences_train = training['text'].values
    sentences_test = testing['text'].values
    y_train = traininglabel['label'].values.astype('int')
    y_test = testinglabel['label'].values.astype('int')

    tokenizer = Tokenizer(num_words=5000)
    tokenizer.fit_on_texts(sentences_train)

    X_train = tokenizer.texts_to_sequences(sentences_train)
    X_test = tokenizer.texts_to_sequences(sentences_test)

    vocab_size = len(tokenizer.word_index) + 1  # Adding 1 because of reserved 0 index

    maxlen = 1000

    X_train = pad_sequences(X_train, padding='post', maxlen=maxlen)
    X_test = pad_sequences(X_test, padding='post', maxlen=maxlen)
    embedding_dim = 50

    model = Sequential()
    model.add(layers.Embedding(input_dim=vocab_size,
                               output_dim=embedding_dim,
                               input_length=maxlen))
    model.add(layers.Flatten())
    model.add(layers.Dense(10, activation='relu'))
    model.add(layers.Dense(1, activation='sigmoid'))

    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    model.summary()

    history = model.fit(X_train, y_train,
                        epochs=1,
                        verbose=False,
                        validation_data=(X_test, y_test),
                        batch_size=5000)

    loss, accuracy = model.evaluate(X_train, y_train, verbose=False)
    print("Training Accuracy: {:.4f}".format(accuracy))
    loss, accuracy = model.evaluate(X_test, y_test, verbose=False)
    print("Testing Accuracy:  {:.4f}".format(accuracy))


def machinelearning2(training, testing):
    traininglabel = pd.DataFrame({'label': training['label'].values})
    for index, row in traininglabel.iterrows():
        row['label'] = ConvertLabeltoNumber(row['label'])

    testinglabel = pd.DataFrame({'label': testing['label'].values})
    for index, row in testinglabel.iterrows():
        row['label'] = ConvertLabeltoNumber(row['label'])

    sentences_train = training['text'].values
    sentences_test = testing['text'].values
    y_train = traininglabel['label'].values.astype('int')
    y_test = testinglabel['label'].values.astype('int')

    tokenizer = Tokenizer(num_words=5000)
    tokenizer.fit_on_texts(sentences_train)

    X_train = tokenizer.texts_to_sequences(sentences_train)
    X_test = tokenizer.texts_to_sequences(sentences_test)

    vocab_size = len(tokenizer.word_index) + 1  # Adding 1 because of reserved 0 index

    maxlen = 1000

    X_train = pad_sequences(X_train, padding='post', maxlen=maxlen)
    X_test = pad_sequences(X_test, padding='post', maxlen=maxlen)
    embedding_dim = 50

    model = Sequential()
    model.add(layers.Embedding(input_dim=vocab_size,
                               output_dim=embedding_dim,
                               input_length=maxlen))
    model.add(layers.Flatten())
    model.add(layers.Dense(10, activation='relu'))
    model.add(layers.Dense(1, activation='sigmoid'))

    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    model.summary()

    history = model.fit(X_train, y_train,
                        epochs=1,
                        verbose=False,
                        validation_data=(X_test, y_test),
                        batch_size=5000)

    loss, accuracy = model.evaluate(X_train, y_train, verbose=False)
    print("Training Accuracy: {:.4f}".format(accuracy))
    loss, accuracy = model.evaluate(X_test, y_test, verbose=False)
    print("Testing Accuracy:  {:.4f}".format(accuracy))

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
            machinelearning1(training_dataframe, testing_dataframe)

        elif inp == 4:
            classifier, vectorizer = logisticRegression(training_dataframe, testing_dataframe)
            varinp = 1
            while not (varinp == "0"):
                print("return 0 to stop")
                print("Input a utterance")
                varinp = input()
                i = vectorizer.transform([varinp])
                print(classifier.predict(i))
