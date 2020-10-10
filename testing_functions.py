from word_matching import choose_closest_word, get_2_word_list,take_second, take_first
from restaurant_db import food_types, areas, price_ranges
from typodistance import typoGenerator


def get_all_finds(sentence):
    print("foodtypes")
    print(typo_vs_levenshtein(sentence, food_types))
    print("areas")
    print(typo_vs_levenshtein(sentence, areas))
    print("priceranges")
    print(typo_vs_levenshtein(sentence, price_ranges))


def typo_vs_levenshtein(sentence, words):
    split = sentence.split()
    return {"Levenshtein": matched_words_in_split(split, words, ""),
            "TypoDistance": matched_words_in_split(split, words, "typoDistance")}

def matched_words_in_split(split, words, func):
    mp = map(lambda x: choose_closest_word(x, words, func), split)
    lst = list(filter(lambda x: x is not None, mp))
    mp2 = map(lambda x: choose_closest_word(x, words, func), get_2_word_list(split))
    lst2 = list(filter(lambda x: x is not None, mp2))
    lst.extend(lst2)
    lst.sort(key=take_first)
    return lst



def generateTypos(sentence, distance):
    generator = typoGenerator(sentence, distance)
    for d in range(0, 20):
        print(generator.__next__())
