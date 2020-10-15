from word_matching import closest_word_in_list, get_2_word_list,take_second, take_first
from restaurant_db import food_types, areas, price_ranges
from typodistance import typoGenerator
import random

ADD_REQ_KEYWORDS = ["children", "romantic", "large group", "good value", "spicy", "first date",
                    "business meeting"]
lensplit = 4
shortwordmax = 1
longwordmax = 3

file = open("data2.csv","w")

def create_test_data():
    file1 = open('data/all_dialogs.txt', 'r')
    Lines = file1.readlines()
    datalines = []
    file.write("line,lev0,lev1,typ0,typ1\n")
    for i in range(0,len(Lines)):
        if Lines[i] == "turn index: 0\n":
            datalines.append(i+2)
    data = list(map(lambda x: Lines[x][len("user: "):][:-len("\n")], datalines))
    random.shuffle(data)
    data = list(filter(lambda x: x != "noise" and x != "static" and x != "sil" and x != "unintelligible" and
                                 x != "cough", data))
    ##data = list(map(lambda x: generateTypos(x,3),data))
    print(len(data))
    data = list(map(lambda x: get_all_finds(x),data))
    file.close()



def get_all_finds(sentence):
    split = sentence.split()
    words = split.copy()
    twowords = get_2_word_list(split)
    words.extend(twowords)

    lst = [typo_vs_levenshtein(words, food_types),
            typo_vs_levenshtein(words, areas),
            typo_vs_levenshtein(words, price_ranges),
            typo_vs_levenshtein(words, ADD_REQ_KEYWORDS)]

    x = [[lst[0][0], lst[1][0], lst[2][0], lst[3][0]], [lst[0][1], lst[1][1], lst[2][1], lst[3][1]],
         [lst[0][2], lst[1][2], lst[2][2], lst[3][2]], [lst[0][3], lst[1][3], lst[2][3], lst[3][3]]]

    if not (x[0] == x[1] and x[1] == x[2] and lst[2] == x[3]):

        file.write(sentence + tostring(x) + "\n")
        return lst
    return

def tostring(lst):
    string=  ""
    for i in lst:
        string += "," + tostrings(i)

    return string

def tostrings(s):

    string = "Do you want a restaurant "
    if len(s[0]) != 0:
        string += "with "+ s[0][1] + " cuisine "
    if len(s[1]) != 0:
        string += "in the " + s[1][1] + " part of town "

    if len(s[2]) != 0:
        string += "at a " + s[2][1] + " price range "

    if len(s[3]) != 0:
        string += "with this additional requirement: " + s[3][1]
    string += "."
    return string


def typo_vs_levenshtein(lst, words):
    lev1 ,lev2= matched_words_in_split(lst, words, "")
    typ1, typ2= matched_words_in_split(lst, words, "typoDistance")
    return (lev1,lev2,typ1,typ2)

def matched_words_in_split(lst, words, func,diff=0):
    additt = []
    additt2 = []
    for word in lst:
        closest_distance, closest_words = closest_word_in_list(word, words, func)
        wd = filt(word,closest_distance, closest_words,0)
        wd1 = filt(word,closest_distance, closest_words,1)
        if wd is not None:
            additt.append(wd)
        if wd1 is not None:
            additt2.append(wd1)

    additt.sort(key=take_first)
    additt2.sort(key=take_first)
    if len(additt) > 0:
        ob = additt[0]
    else:
        ob = additt
    if len(additt2) > 0:
        ob2 = additt2[0]
    else:
        ob2 = additt2
    return (ob,ob2)

def filt(word,closest_distance, closest_words,diff):
    if (len(word) <= lensplit and closest_distance <= (shortwordmax + diff)) or (
            len(word) > lensplit and closest_distance <= (longwordmax + diff)):
        if len(closest_words) > 1:
            return closest_distance, closest_words[random.randrange(0, len(closest_words))]
        else:
            return closest_distance, closest_words[0]

def generateTypos(sentence, distance):
    generator = typoGenerator(sentence, distance)
    for d in range(0, 20):
        generator.__next__()
    return generator.__next__()


if __name__ == '__main__':
    inp = True
    create_test_data()
