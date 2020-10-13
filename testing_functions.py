from word_matching import closest_word_in_list, get_2_word_list,take_second, take_first
from restaurant_db import food_types, areas, price_ranges
from typodistance import typoGenerator
import random

ADD_REQ_KEYWORDS = ["children", "romantic", "large group", "good value", "spicy", "first date",
                    "business meeting"]
lensplit = 4
shortwordmax = 1
longwordmax = 3

file = open("data.csv","w")

def create_test_data():
    file1 = open('data/all_dialogs.txt', 'r')
    Lines = file1.readlines()
    datalines = []
    file.write("line,lev0food,lev1food,typ0food,typ1food,"
               "lev0area,lev1area,typ0area,typ1area,"
               "lev0price,lev1price,typ0price,typ1price,"
               "lev0add,lev1add,typ0add,typ1add\n")
    for i in range(0,len(Lines)):
        if Lines[i] == "turn index: 0\n":
            datalines.append(i+2)

    data = list(map(lambda x: Lines[x][len("user: "):][:-len("\n")], datalines))
    data = list(filter(lambda x: x != "noise" and x != "static" and x != "sil" and x != "unintelligible" and
                                 x != "cough", data))
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

    if lst[0] is not None or lst[1] is not None or lst[2] is not None or lst[3] is not None:

        file.write(sentence + tostring(lst) + "\n")
        return lst
    return

def tostring(lst):
    string = ""
    for i in lst:
        if i is not None:
            for j in i:
                string += ","
                if len(j) != 0:
                    string += str(j[1])

        else:
            string += ",,,,"



    return string

def typo_vs_levenshtein(lst, words):
    lev1 ,lev2= matched_words_in_split(lst, words, "")
    typ1, typ2= matched_words_in_split(lst, words, "typoDistance")
    if len(lev1) == 0 and len(lev2) == 0 and len(typ1) == 0 and len(typ2) == 0:
        return
    if len(lev1) > 0 and len(lev2) > 0 and len(typ1) > 0 and len(typ2) > 0:
        if lev1[1] == lev2[1] and lev2[1] == typ1[1] and typ1[1] == typ2[1]:
            return
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
        print(generator.__next__())


if __name__ == '__main__':
    inp = True
    create_test_data()
