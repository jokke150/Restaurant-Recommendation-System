import pandas as pd

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

def check_labels(baseline):
    correctlabels = 0
    labels = 0
    for index, row in baseline.iterrows():
        if row['label'] == row['match']:
            correctlabels = correctlabels + 1
        labels = labels + 1
    print("Correct Labels:", correctlabels, "/ Labels:", labels)
    print("Score:", 100 * correctlabels / labels)