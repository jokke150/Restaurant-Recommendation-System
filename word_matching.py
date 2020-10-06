import Levenshtein
from typodistance import typoDistance
import random


def closest_word_in_list(word, words, func):
    closest_words = []
    closest_distance = 500
    for baseword in words:
        if func == "typoDistance":
            dist = typoDistance(word, baseword)
        else:
            dist = Levenshtein.distance(word, baseword)
        if dist < closest_distance:
            closest_distance = dist
            closest_words = [baseword]
        elif dist == closest_distance:
            closest_words.append(baseword)

    return closest_distance, closest_words


def choose_closest_word(word, words, func):
    closest_distance, closest_words = closest_word_in_list(word, words, func)
    if func == "typoDistance":
        lensplit = 4
        shortwordmax = 1
        longwordmax = 3
    else:
        lensplit = 4
        shortwordmax = 1
        longwordmax = 3

    if (len(word) <= lensplit and closest_distance <= shortwordmax) or (
            len(word) > lensplit and closest_distance <= longwordmax):
        if len(closest_words) > 1:
            return closest_distance, closest_words[random.randrange(0, len(closest_words))]
        else:
            return closest_distance, closest_words[0]


def get_2_word_list(split):
    list = []
    for i in range(0, len(split) - 1):
        list.append(split[i] + " " + split[i + 1])
    return list


def matched_words_in_split(split, words, func):
    mp = map(lambda x: choose_closest_word(x, words, func), split)
    lst = list(filter(lambda x: x is not None, mp))
    mp2 = map(lambda x: choose_closest_word(x, words, func), get_2_word_list(split))
    lst2 = list(filter(lambda x: x is not None, mp2))
    lst.extend(lst2)
    lst.sort(key=take_first)
    return list(map(lambda x: take_second(x), lst))


def closest_words(split, words, func=""):
    matched_words = matched_words_in_split(split, words, func)
    if len(matched_words) != 0:
        return matched_words
    return []


def closest_word(split, words, func=""):
    matched_words = closest_words(split, words, func)
    if matched_words:
        return matched_words[0]
    return None


def take_first(item):
    return item[0]


def take_second(item):
    return item[1]
