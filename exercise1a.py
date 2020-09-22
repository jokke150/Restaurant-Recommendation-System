import pandas as pd

from learners.baselines import baseline1, baseline2, check_labels, baseline2_check
from learners.log_regression import logistic_regression
from learners.neural_net import train_nn, save_nn, load_nn, predict_nn


def read_file():
    df = pd.read_csv("data/rand_dialog_acts.dat",
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


def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


if __name__ == '__main__':

    df = read_file()
    train_df, test_df = generate_dataframe(df)

    x_train = train_df['text'].values
    x_test = test_df['text'].values
    y_test = test_df['label'].values
    y_train = train_df['label'].values

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
            print('type "train" to run the training again')
            varinp = input()
            if varinp == 'train':
                tokenizer, model, label_encoder = train_nn(x_train, x_test, y_test, y_train)
                save_nn(tokenizer, model, label_encoder)
            else:
                tokenizer, model, label_encoder = load_nn()

            while not (varinp == "0"):
                print("return 0 to stop")
                print("Input an utterance")
                varinp = input()
                print(predict_nn(varinp, tokenizer, model, label_encoder))

        elif inp == 4:
            classifier, vectorizer = logistic_regression(x_train, x_test, y_test, y_train)
            varinp = 1
            while not (varinp == "0"):
                print("return 0 to stop")
                print("Input an utterance")
                varinp = input()
                i = vectorizer.transform([varinp])
                print(classifier.predict(i))
