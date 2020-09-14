from collections import Counter


class Utterance:
    def __init__(self, line):
        tokens = line.split()
        self.label = tokens[0]
        words = tokens[1:len(tokens)]
        self.words = words
        self.words_string = ' '.join(words)

    def __repr__(self):
        return 'Utterance(%r, %r)' % (self.label, self.words)


def read_file():
    dialog_acts = open("rand_dialog_acts.dat", "r")
    lines = dialog_acts.readlines()
    labels = []
    utterances = []
    for line in lines:
        line = line.lower()
        utterance = Utterance(line)
        labels.append(utterance.label)
        utterances.append(utterance)
    major_label = Counter(labels).most_common(1)[0][0]
    return utterances, major_label


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
    utterances, major_label = read_file()
    train_utterances = utterances[0: int(len(utterances) * 0.85) - 1]
    test_utterances = utterances[int(len(utterances) * 0.85): len(utterances)]
    test(test_utterances)
