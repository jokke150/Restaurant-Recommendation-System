from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression


def logistic_regression(x_train, x_test, y_test, y_train):
    vectorizer = CountVectorizer()
    vectorizer.fit(x_train)

    x_train = vectorizer.transform(x_train)
    x_test = vectorizer.transform(x_test)
    
    classifier = LogisticRegression(class_weight="balanced").fit(x_train, y_train)

    score = classifier.score(x_test, y_test)
    print("Accuracy:", score)
    return (classifier, vectorizer)
