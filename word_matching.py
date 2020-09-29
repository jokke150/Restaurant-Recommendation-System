import Levenshtein
import random


def closest_word_in_list(word, words):
    closest_words = []
    closest_distance = 500
    for baseword in words:
        dist = Levenshtein.distance(word, baseword)
        if (dist < closest_distance):
            closest_distance = dist
            closest_words = [baseword]
        elif (dist == closest_distance):
            closest_words.append(baseword)

    return (closest_distance, closest_words)


def choose_closest_word(word, words):
    closest_distance, closest_words = closest_word_in_list(word, words)
    if (len(word) <= 3 and closest_distance <= 1) or (len(word) > 3 and closest_distance <= 3):
        # TODO Ask the user which of the options is the one he was asking for
        if len(closest_words) > 1:
            return closest_words[random.randrange(0, len(closest_words))]
        else:
            return closest_words[0]


def matched_words_in_split(split, words):
    mp = map(lambda x: choose_closest_word(x, words), split)
    return list(filter(lambda x: x != None, mp))
