import pandas as pd
import word_matching as w_m
import exercise1a as main
from learners.neural_net import load_nn

df = pd.read_csv("data/restaurant_info.csv")

cuisines = ["spanish", "italian", "french", "world", "thai", "bistro", "chinese",
            "international", "portuguese", "mediterranean", "british", "indian",
            "gastropub", "turkish", "persian", "jamaican", "japanese", "seafood",
            "cuban", "european", "lebanese", "creative"]

locations = ["center", "north", "east", "south", "west"]

ranges = ["moderate", "cheap", "expensive"]

tokenizer, model, label_encoder = load_nn()


def input_output(state, utterance):
    dialog_act = main.predict_nn(utterance, tokenizer, model, label_encoder)

    if dialog_act == "bye":
        state["state"] = "end"
        return state, "Goodbye, enjoy your meal!"

    switcher = {
        "start": start_information_gathering,
        "pricerange": pricerange,
        "foodtype": foodtype,
        "area": area,
        "alt-restaurant-suggested": alt_restaurant_given,
        "restaurant-suggested": restaurant_given

    }
    # Get the function from switcher dictionary
    func = switcher.get(state["state"], lambda: (state, "State not defined"))

    return func(state, dialog_act, utterance)


def start_information_gathering(state, da, utterance):
    split = utterance.split()

    if (da == "inform"):
        # Check if the area is unknown but mentioned by the user
        if state["area"] == "":
            word = w_m.closest_word(split, locations)
            if word != "":
                state["area"] = word
        # Check if the pricerange is unknown but mentioned by the user
        if state["pricerange"] == "":
            
            word = w_m.closest_word(split, ranges)
            if word != "":
                state["pricerange"] = word
        # Check if the foodtype is unknown but mentioned by the user
        if state["foodtype"] == "":
            word = w_m.closest_word(split, cuisines)
            if word != "":
                state["foodtype"] = word
                
        if state["pricerange"] == "":
            return ask_pricerange(state)
        elif state["foodtype"] == "":
            return ask_foodtype(state)
        elif state["area"] == "":
            return ask_area(state)
        else:
            return suggest_restaurant(state)


def ask_pricerange(state):
    state["state"] = "pricerange"
    return (state, "What price range would you like?")


def ask_foodtype(state):
    state["state"] = "foodtype"
    return (state, "What type of food would you like?")


def ask_area(state):
    state["state"] = "area"
    return (state, "In what area would you like to look for a restaurant?")


def pricerange(state, da, utterance):
    if (da == "inform"):
        if utterance == "any":
            state["pricerange"] = "any"
            if state["area"] == "":
                return ask_area(state)
            elif state["foodtype"] == "":
                return ask_foodtype(state)
            else:
                return suggest_restaurant(state)
        if state["pricerange"] == "":
            for word in w_m.matched_words_in_split(utterance.split(), ranges):
                state["pricerange"] = word
                if state["area"] == "":
                    return ask_area(state)
                elif state["foodtype"] == "":
                    return ask_foodtype(state)
                else:
                    return suggest_restaurant(state)


def foodtype(state, da, utterance):
    if (da == "inform"):
        if utterance == "any":
            state["foodtype"] = "any"
            if state["pricerange"] == "":
                return ask_pricerange(state)
            elif state["area"] == "":
                return ask_area(state)
            else:
                return suggest_restaurant(state)
        if state["foodtype"] == "":
            for word in w_m.matched_words_in_split(utterance.split(), cuisines):
                state["foodtype"] = word
                if state["pricerange"] == "":
                    return ask_pricerange(state)
                elif state["area"] == "":
                    return ask_area(state)
                else:
                    return suggest_restaurant(state)


def area(state, da, utterance):
    if (da == "inform"):
        if utterance == "any":
            state["area"] = "any"
            if state["pricerange"] == "":
                return ask_pricerange(state)
            elif state["foodtype"] == "":
                return ask_foodtype(state)
            else:
                return suggest_restaurant(state)
        if state["area"] == "":
            for word in w_m.matched_words_in_split(utterance.split(), locations):
                state["area"] = word
                if state["pricerange"] == "":
                    return ask_pricerange(state)
                elif state["foodtype"] == "":
                    return ask_foodtype(state)
                else:
                    return suggest_restaurant(state)


# TODO
def restaurant_given(state, da, utterance):
    return (state, "")


# TODO
def alt_restaurant_given(state, da, utterance):
    return (state, "")


def suggest_restaurant(state):
    foodtype = state["foodtype"]
    area = state["area"]
    pricerange = state["pricerange"]

    subframe = df[(df["food"] == foodtype) & (df["area"] == area) & (df["pricerange"] == pricerange)]

    restaurant = subframe[:1]

    if len(subframe) == 0:
        if len(df[(df["food"] == foodtype) & (df["area"] == area)]) != 0:
            restaurant = df[(df["food"] == foodtype) & (df["area"] == area)][:1]
            name = restaurant["restaurantname"].iloc[0]
            foodtype = restaurant["food"].iloc[0]
            area = restaurant["area"].iloc[0]
            pricerange = restaurant["pricerange"].iloc[0]
            state["state"] = "alt-restaurant-suggested"
            return (state, print(
                "No restaurant available in that pricerange. However,  " + name + " also has " + foodtype + "food, is "
                                                                                                            "also in "
                                                                                                            "the " +
                area + " part of town, but is in the " + pricerange + " pricerange."))

        state["state"] = "end"
        return (state, print("Sorry no restaurant with your preferences"))

    name = restaurant["restaurantname"].iloc[0]
    foodtype = restaurant["food"].iloc[0]
    area = restaurant["area"].iloc[0]
    pricerange = restaurant["pricerange"].iloc[0]

    state["state"] = "restaurant-suggested"
    state["restaurant"] = name

    return (state, print(str(name) + " is a nice restaurant in the " + str(area) + " part of town that serves " + str(
        foodtype) + " food in the " + str(pricerange) + " price range"))


# TODO some of these parts arent built into the currently running code
def input_output_match(text, dialog_act, foodtype, area, pricerange, topic):
    split = text.split()

    if dialog_act == "affirm":
        if foodtype == "":
            return print("What type of food would you like")
        if area == "":
            return print("In what area would you like to look for a restaurant?")
        if pricerange == "":
            return print("What price range would you like?")

    if dialog_act == "hello":
        return print("You can ask for restaurants by area, price range or food type")

    if dialog_act == "reqalts":

        print("IN REQALTS")
        # If foodtype was known but a new foodtype preference is expressed, save this new one
        if foodtype != "":
            for word in w_m.matched_words_in_split(split, cuisines):
                foodtype = word
                return suggest_restaurant(foodtype, area, pricerange)

        # If foodtype area was known but a new area preference is expressed, save this new one
        if area != "":
            for word in w_m.matched_words_in_split(split, locations):
                area = word
                return suggest_restaurant(foodtype, area, pricerange)

        # If pricerange was known but a new foodtype preference is expressed, save this new one
        if pricerange != "":
            for word in w_m.matched_words_in_split(split, ranges):
                pricerange = word
                return suggest_restaurant(foodtype, area, pricerange)

    if dialog_act == "inform":

        if foodtype != "" and area != "" and pricerange != "":
            return suggest_restaurant(foodtype, area, pricerange)

        return "The system did not understand the input, please clarify."
