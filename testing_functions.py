from word_matching import matched_words_in_split
from restaurant_db import food_types, areas, price_ranges
from typodistance import typoGenerator


def get_all_finds(sentence):
    print("foodtypes")
    print(typo_vs_levenshtein(sentence,food_types))
    print("areas")
    print(typo_vs_levenshtein(sentence, areas))
    print("priceranges")
    print(typo_vs_levenshtein(sentence, price_ranges))


def typo_vs_levenshtein(sentence, words):
    split = sentence.split()
    return { "Levenshtein":matched_words_in_split(split, words,""), "TypoDistance": matched_words_in_split(split, words,"typoDistance")}

def generateTypos(sentence, distance):
    generator = typoGenerator(sentence, distance)
    for d in range(0,20):
        print(generator.__next__())